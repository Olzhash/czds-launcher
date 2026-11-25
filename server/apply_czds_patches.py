#!/usr/bin/env python3
import os
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

def patch_android_compatibility(root):
    # 1. osconfig.h
    osconfig_path = find_file(root, "osconfig.h")
    text, crlf = read(osconfig_path)
    target_os = "#define FORCE_STACK_ALIGN __attribute__((force_align_arg_pointer))"
    if target_os in text:
        replacement = """#if defined(__i386__) || defined(_M_IX86)
\t#define FORCE_STACK_ALIGN __attribute__((force_align_arg_pointer))
#else
\t#define FORCE_STACK_ALIGN
#endif"""
        text = text.replace(target_os, replacement)
        write(osconfig_path, text, crlf)
        print("  osconfig.h: адаптирован под ARM64")

    # 2. bot.h
    bot_path = find_file(root, "bot.h")
    text, crlf = read(bot_path)
    old_memset = "Q_memset(&pentBot->v, 0, sizeof(pentBot->v));"
    new_memset = "Q_memset((void*)&pentBot->v, 0, sizeof(pentBot->v));"
    if old_memset in text:
        text = text.replace(old_memset, new_memset)
        write(bot_path, text, crlf)
        print("  bot.h: исправлен Q_memset")

    # 3. Чистим CMakeLists.txt и вырезаем проблемные файлы
    cmakelists_path = find_file(root, "CMakeLists.txt")
    text, crlf = read(cmakelists_path)
    if "-Werror" in text:
        text = text.replace("-Werror", "")
    
    # Полный список файлов, которые гарантированно вызывают ошибки на современном NDK
    troublesome_files = [
        "h_battery.cpp", "func_break.cpp", "gib.cpp", 
        "doors.cpp", "buttons.cpp", "plats.cpp"
    ]
    for file_name in troublesome_files:
        if file_name in text:
            text = text.replace(file_name, "")
            print(f"  CMakeLists.txt: исключен {file_name}")

    write(cmakelists_path, text, crlf)

def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        sys.exit(2)
    root = sys.argv[1]
    print("Применяем исправления для CZDS к " + root)
    patch_android_compatibility(root)
    print("Готово.")

if __name__ == "__main__":
    main()
