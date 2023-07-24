# BeamMP Lua反馈支持

KiuToi几乎完全支持BeamMP的lua插件，所有必要的方法都已经创建，测试显示以下细节：

在KiuToi中没有支持:`MP.Set()`

#### Economic Rework V2.0（付费，Discord（RU）：[Hlebushek](https://discordapp.com/users/449634697593749516)）

1. 要获取`pluginPath`，需要：`debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")`，因为路径返回值中包含`@`，这破坏了插件。

#### Cobalt Essentials V1.7.5（免费，[github ↗](https://github.com/prestonelam2003/CobaltEssentials/)）

1. 要获取`pluginPath`，需要：`debug.getinfo(1).source:gsub("\\","/")` => `debug.getinfo(1).source:gsub("\\","/"):gsub("@", "")`，因为路径返回值中包含`@`，这破坏了插件。

### 工作原理

插件加载经过几个阶段：

1. 扫描`plugins/`文件夹
2. 如果文件夹不在PyPlugins中，并且文件夹中存在`*.lua`，则添加它，例如`plugins/LuaPlugin`
3. 然后从该文件夹中进行`lua.loadfile({filename})`（这是lua中的标准方法）
4. 最后调用事件和函数`onInit()`
5. 如果在执行`onInit()`期间没有发生错误，则可以通过`lua_plugins`命令看到这样的消息：`Lua plugins: LuaPlugin:ok`
