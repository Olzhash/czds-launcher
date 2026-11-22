# CZ Deleted Scenes — лаунчер для Xash3D FWGS (экспериментальный)

## Статус (читать первым)
- **APK ещё не собран и не запускался.** В среде, где писался проект, нет Android SDK/NDK, Gradle, `d8`, `apksigner` и сети. Проверено только: Java-код компилируется против моих заглушек Android API, XML корректен, ссылки на ресурсы существуют.
- Даже после сборки **кампания Deleted Scenes не заработает**: игровая логика оригинала (`cz.dll`, `client.dll`) — Windows x86, а UI построен на VGUI2. Подробности и цифры: `COMPAT.md`.
- Что реально можно получить: проверку, что Xash3D грузит ресурсы `czeror` и карты. При запуске приложение прямо об этом предупреждает.

## Что это
Лаунчер того же устройства, что клиент CS 1.6 (`in.celest.xash3d.cs16client` 1.35): сам игру не содержит, а запускает движок `su.xash.engine[.test]` с параметрами `gamedir`, `gamelibdir`, `argv`, `package` (восстановлено из байткода оригинала).

| Из клиента CS 1.6 | Как использовано |
|---|---|
| Механизм запуска движка | Повторён в `MainActivity.java` |
| `libclient.so`, `libmenu.so`, `libserver.so` (ARM) | Взяты как есть (arm64-v8a, armeabi-v7a) |
| Сенсорное управление: `touch/`, `touch_presets/`, `touch.cfg`, `touch_default/` | Взято как есть |
| Меню настроек графики/управления | Это меню самого движка (`libmenu.so`), отдельно не переписывалось |

**Намеренно не взято** (это контент CS 1.6, он мог бы подменить файлы czeror): `sound/`, `gfx/`, `media/`, `addons/`, `BotChatter.db`, `BotProfile.db`, `BotCampaignProfile.db`, `gameinfo.txt` (прописывает `gamedir cstrike`, `multiplayer_only`), `fastdl.txt`, `userconfig.d/`, `libyapb.so` (боты CS).

**Изменено:** package `app.czds.xash3d.launcher`, название, иконка (нарисована с нуля), `gamedir=czeror`, запуск с `-dll libserver.so` вместо `libyapb.so`, `-language russian`, предупреждение перед запуском.

## Сборка
- **Android Studio:** открыть папку проекта → Build → Build APK(s). Нужны JDK 17 и Android SDK 34.
- **Без ПК:** залить проект в репозиторий GitHub → Actions → `build-apk` → Run workflow → скачать артефакт (`.github/workflows/build.yml`).
- В `app/build.gradle.kts` обязательно `useLegacyPackaging = true`: движок грузит `.so` по пути `nativeLibraryDir`.

## Установка и запуск
1. Установить `xash3d-fwgs-android.apk` (движок).
2. Установить собранный APK этого проекта.
3. Положить игровые файлы в папку движка (обычно `/sdcard/xash/`, **не проверено**): `valve`, `cstrike`, `czeror`, `czeror_russian`. Без `valve` (нужен `halflife.wad`) и `cstrike` (в `liblist.gam` стоит `fallback_dir "cstrike"`) игра не загрузится. Файлы должны быть из вашей собственной лицензионной копии.
4. Запустить приложение и подтвердить предупреждение.

## Параметры
Всё в константах вверху `MainActivity.java`: `GAMEDIR`, `ENGINE_ARGS`, `GAME_DLL`. Если `-language russian` не подмонтирует `czeror_russian`, объедините папки `czeror_russian` → `czeror` копированием (оригиналы не удаляйте).
