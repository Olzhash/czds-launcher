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


# ---------------------------------------------------------------- патч 1 + 2b
HUD_OLD = re.compile(
    r"^[ \t]*pPlayer->m_iHideHUD\s*\|=\s*\(\s*HIDEHUD_WEAPONS\s*\|\s*HIDEHUD_HEALTH\s*\|\s*"
    r"HIDEHUD_TIMER\s*\|\s*HIDEHUD_MONEY\s*\)\s*;[ \t]*$",
    re.M,
)

HUD_NEW = """\t// {m} Deleted Scenes: здоровье, броня и прицел видны всегда (в режиме тренировки CS прячет их до item_suit).
\t// Таймер и деньги в DS не используются, оставляем их скрытыми. Бит HIDEHUD_OBSERVER_CROSSHAIR не даёт
\t// серверу отправлять клиенту команду "скрыть прицел" при смене этих флагов (клиент этот бит игнорирует).
\t// Бит WEAPON_SUIT нужен клиентскому HUD, он рисует здоровье и броню только при его наличии.
\tpPlayer->pev->weapons |= (1 << WEAPON_SUIT);
\tpPlayer->m_iHideHUD &= ~(HIDEHUD_WEAPONS | HIDEHUD_HEALTH | HIDEHUD_CROSSHAIR);
\tpPlayer->m_iHideHUD |= (HIDEHUD_TIMER | HIDEHUD_MONEY | HIDEHUD_OBSERVER_CROSSHAIR);""".format(m=MARK)

WRAPPERS = """

// {m} В одиночной игре (maxclients == 1) отправляем владельцу события выстрелов и анимации оружия
// напрямую (без FEV_NOTHOST и без пропуска игрока). Иначе при CLIENT_WEAPONS они зависят от
// предсказания на клиенте, которое в одиночной игре под Xash3D может не работать.
void CZDS_PlaybackEventFull(int flags, const edict_t *pInvoker, unsigned short eventindex, float delay,
\tfloat *origin, float *angles, float fparam1, float fparam2, int iparam1, int iparam2, int bparam1, int bparam2)
{{
\tif (gpGlobals->maxClients <= 1)
\t\tflags &= ~FEV_NOTHOST;

\t(*g_engfuncs.pfnPlaybackEvent)(flags, pInvoker, eventindex, delay, origin, angles,
\t\tfparam1, fparam2, iparam1, iparam2, bparam1, bparam2);
}}

int CZDS_CanSkipPlayer(const edict_t *player)
{{
\tif (gpGlobals->maxClients <= 1)
\t\treturn 0;

\treturn (*g_engfuncs.pfnCanSkipPlayer)(player);
}}
""".format(m=MARK)


def patch_training(root):
    path = find_file(root, "training_gamerules.cpp")
    text, crlf = read(path)
    changed = False

    if MARK + " Deleted Scenes: здоровье" in text:
        print("  training_gamerules.cpp: HUD-правка уже применена")
    else:
        if len(HUD_OLD.findall(text)) != 1:
            fail("в training_gamerules.cpp не найдена строка с HIDEHUD_WEAPONS | HIDEHUD_HEALTH | ... "
                 "(код ReGameDLL изменился). Пришлите этот файл.")
        text = HUD_OLD.sub(lambda m: HUD_NEW, text, count=1)
        changed = True
        print("  training_gamerules.cpp: HUD-правка применена")

    if "CZDS_PlaybackEventFull" in text:
        print("  training_gamerules.cpp: обёртки событий уже есть")
    else:
        text = text.rstrip("\n") + "\n" + WRAPPERS
        changed = True
        print("  training_gamerules.cpp: добавлены обёртки событий оружия")

    if changed:
        write(path, text, crlf)


# ---------------------------------------------------------------- патч 2a
PB_OLD = re.compile(r"^#define[ \t]+PLAYBACK_EVENT_FULL[ \t]+\(\*g_engfuncs\.pfnPlaybackEvent\)[ \t]*$", re.M)
CS_OLD = re.compile(r"^#define[ \t]+ENGINE_CANSKIP[ \t]+\(\*g_engfuncs\.pfnCanSkipPlayer\)[ \t]*$", re.M)

PB_NEW = """// {m} реализация в training_gamerules.cpp
void CZDS_PlaybackEventFull(int flags, const edict_t *pInvoker, unsigned short eventindex, float delay, float *origin, float *angles, float fparam1, float fparam2, int iparam1, int iparam2, int bparam1, int bparam2);
#define PLAYBACK_EVENT_FULL\t\t\tCZDS_PlaybackEventFull""".format(m=MARK)

CS_NEW = """// {m} реализация в training_gamerules.cpp
int CZDS_CanSkipPlayer(const edict_t *player);
#define ENGINE_CANSKIP\t\t\t\tCZDS_CanSkipPlayer""".format(m=MARK)


def patch_enginecallback(root):
    path = find_file(root, "enginecallback.h")
    text, crlf = read(path)

    if "CZDS_PlaybackEventFull" in text and "CZDS_CanSkipPlayer" in text:
        print("  enginecallback.h: правка уже применена")
        return
    if len(PB_OLD.findall(text)) != 1 or len(CS_OLD.findall(text)) != 1:
        fail("в enginecallback.h не найдены определения PLAYBACK_EVENT_FULL / ENGINE_CANSKIP "
             "(код ReGameDLL изменился). Пришлите этот файл.")
    text = PB_OLD.sub(lambda m: PB_NEW, text, count=1)
    text = CS_OLD.sub(lambda m: CS_NEW, text, count=1)
    write(path, text, crlf)
    print("  enginecallback.h: правка применена")


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        sys.exit(2)
    root = sys.argv[1]
    print("Применяю правки CZDS к " + root)
    patch_training(root)
    patch_enginecallback(root)
    print("Готово.")


if __name__ == "__main__":
    main()
