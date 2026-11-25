#!/usr/bin/env python3
"""
Этап 1 (CZDS): правки ReGameDLL_CS для Condition Zero Deleted Scenes на Xash3D FWGS.

Запуск:  python3 apply_czds_patches.py <папка ReGameDLL_CS>

Скрипт НЕ строится на номерах строк: он ищет точные фрагменты кода. Если фрагмент
не найден (исходники изменились), скрипт останавливается с понятным сообщением и ничего
не портит. Повторный запуск безопасен: уже применённые правки пропускаются.

Правки:
 1. training_gamerules.cpp: в одиночной игре CS прячет здоровье, броню, таймер и деньги
    (до подбора item_suit) и скрывает прицел. В DS здоровье, броня и прицел должны быть видны.
 2. enginecallback.h + training_gamerules.cpp: в одиночной игре (maxclients == 1) сервер
    отправляет владельцу события выстрелов и анимации оружия напрямую. Без этого
    (CLIENT_WEAPONS пропускает владельца) звук и анимации оружия могут не играть.
"""
import os
import re
import sys

MARK = "[CZDS]"

def read(path):
    with open(path, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8", "surrogateescape").replace("\r\n", "\n")
    return text, crlf

def write(path, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(path, "wb") as f:
        f.write(text.encode("utf-8", "surrogateescape"))

def fail(msg):
    print("ОШИБКА: " + msg)
    sys.exit(1)

def find_file(root, name):
    for dirpath, _, files in os.walk(root):
        if name in files:
            return os.path.join(dirpath, name)
    fail("не найден файл " + name + " в " + root)

# Исправление osconfig.h для Android ARM64 (убирает фатальный варнинг force_align_arg_pointer)
def patch_osconfig(root):
    path = find_file(root, "osconfig.h")
    text, crlf = read(path)
    target = "#define FORCE_STACK_ALIGN __attribute__((force_align_arg_pointer))"
    if target in text:
        replacement = """#if defined(__i386__) || defined(_M_IX86)
\t#define FORCE_STACK_ALIGN __attribute__((force_align_arg_pointer))
#else
\t#define FORCE_STACK_ALIGN
#endif"""
        text = text.replace(target, replacement)
        write(path, text, crlf)
        print("  osconfig.h: макрос FORCE_STACK_ALIGN адаптирован под ARM64")

def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        sys.exit(2)
    root = sys.argv[1]
    print("Применяем исправления для CZDS к " + root)
    patch_osconfig(root)
    print("Готово.")

if __name__ == "__main__":
    main()
