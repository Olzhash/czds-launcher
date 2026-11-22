# Проверка совместимости czeror → Xash3D FWGS (Android)

Метод: статический разбор файлов, ничего не запускалось на устройстве. Данные: `czeror.7z`, `czeror_russian.7z` (6713 файлов, размеры совпали со списками архивов; CRC отдельных файлов не проверялись).

## Совместимо (по форматам)
| Компонент | Итог |
|---|---|
| Карты | 73 BSP v30 (`cz_*`, включая `cz_recoil-intro` и `cz_train01`), в пределах лимитов GoldSrc. Две карты с entity-блоком чуть больше 128 КБ (`cz_downed3`, `cz_miami1`) |
| Модели | 1073 MDL, все версии 10; максимум костей 120 (<128) |
| Звуки | 4458 WAV, все PCM моно (8/16 бит) + 95 MP3; в движке есть mpg123 |
| Текстуры | 23 WAD3 (4450 текстур, размеры кратны 16), 161 спрайт IDSP v2, TGA/BMP в `gfx` |
| Скрипты `events/*.sc` | Пустые заглушки, движку нужно только их наличие |

## Несовместимо
| Компонент | Проблема |
|---|---|
| `dlls/cz.dll` (695 экспортов), `cl_dlls/client.dll` (101) | 32-битные Windows PE (2004 г.), на Android не загружаются |
| Игровая логика | Из 244 классов объектов на картах в ReGameDLL (`libserver.so`) есть 115, нет 129; 10 из них закрывает HL-логика движка (`info_node`, `scripted_sequence`, `monstermaker`…), **119 не реализованы нигде на ARM**: 90 `monster_*` (солдаты, заложники), `trigger_objective`, `trigger_endmission`, `env_missionfailure`, `trigger_usetool`, оружие (`weapon_blowtorch`, `camera`, `fiberopticcamera`, `radiocontrolledbomb`, `laws`, `m60`, `shieldgun`, `zipline`…). Это 7286 размещений из 40958 |
| HUD и меню | `client.dll` построен на VGUI2 (карта мира, выбор миссий, брифинги `classes/*.res`); Xash3D VGUI2 не поддерживает |
| Данные, читаемые только DLL | `sequences/*.seq`, `materials/*.mat`, `maps/graphs/*.nod|.nrp` |

## Не хватает файлов
`valve`: `halflife.wad`, модели `*gibs*`, `bigrat`, `skeleton`, спрайты (`glow*`, `fexplo*`, `fire`, `laserbeam`, `steam1`…), часть `ambience/*.wav`. `cstrike` — по `fallback_dir`. Пять моделей (`drug_lord`, `null`, `player`, `urban`, `props/autocannon`) ссылаются на внешние файлы текстур, которых нет в архивах; проверить после добавления `valve`/`cstrike`.

## Не проверено
Запуск на устройстве, загрузка карты, работа `-language`, путь к данным движка, поведение `libclient.so` (cs16-client) с ресурсами czeror, установка собранного APK.

## Что нужно для настоящей кампании
Либо переписать на ARM логику и интерфейс Deleted Scenes (119 классов, VGUI2-экраны), либо запускать оригинальную Windows-версию через слой совместимости (Wine + Box64, напр. Winlator), что не даёт отдельного APK.
