# Обеспечение обратной поддержки BeamMP Lua

В KiuToi есть практически полная поддержка lua плагинов с BeamMP, все необходимые методы созданы, тестирование показало следующие нюансы:

В KiuToi не будет поддержки: `MP.Set()`

#### Economic Rework V2.0 (Платный, Discord (RU): [Hlebushek](https://discordapp.com/users/449634697593749516))

1. Для получения `pluginPath` нужно: `debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")` так как пусть возвращается с `@`, что сломало плагин.

#### Cobalt Essentials V1.7.5 (Бесплатный, [github](https://github.com/prestonelam2003/CobaltEssentials/))

1. Для получения `pluginPath` нужно: `debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")` так как пусть возвращается с `@`, что сломало плагин.
2. `cobaltSysChar` 

### Немного о принципе работы

Загрузка плагина проходит в несколько этапов:

1. Сканируется папка `plugins/`
2. Если папки нет в PyPlugins и в папке есть `*.lua`, то она добавляется, допустим это будет `plugins/LuaPlugin`
3. Далее из этой папки проходит `lua.loadfile({filename})` (Это стандартный метод в lua)
4. И в конце вызывается ивент и функция `onInit()`
5. Если во время выполнения `onInit()` не произошло ошибок, можно будет увидеть через команду `lua_plugins` такое сообщение: `Lua plugins: LuaPlugin:ok`
