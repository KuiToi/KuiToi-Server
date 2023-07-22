# Providing Backward Compatibility for BeamMP Lua

KiuToi provides almost full support for lua plugins with BeamMP. All necessary methods have been created, and testing has revealed the following nuances:

KiuToi does not support: `MP.Set()`

#### Economic Rework V2.0 (Paid, Discord (RU): [Hlebushek](https://discordapp.com/users/449634697593749516))

1. To obtain `pluginPath`, use: `debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")` as the path returns with `@`, which broke the plugin.

#### Cobalt Essentials V1.7.5 (Free, [github](https://github.com/prestonelam2003/CobaltEssentials/))

1. To obtain `pluginPath`, use: `debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")` as the path returns with `@`, which broke the plugin.
2. All `require()` statements had to be moved after `onInit`.
3. In some cases, `MP.RegisterEvent` had to be moved after the function declaration, i.e.:
```lua
--This is incorrect, registration may fail
MP.RegisterEvent("onPlayerAuth","onPlayerAuth") 
function onPlayerAuth(name, role, isGuest)
    -- Some plugin code
end

--This is the correct version
MP.RegisterEvent("onPlayerAuth","onPlayerAuth")
```

### A Little About How it Works

Plugin loading goes through several stages:

1. The `plugins/` folder is scanned.
2. If the folder is not in PyPlugins and there are `*.lua` files in the folder, then it is added as a plugin folder, let's say it will be `plugins/LuaPlugin`
3. Next, `lua.loadfile({filename})` is performed from this folder (this is the standard method in lua).
4. Finally, the `onInit()` function is called, and an event is triggered.
5. If no errors occur during the execution of `onInit()`, you can see the message `Lua plugins: LuaPlugin:ok` through the `lua_plugins` command.