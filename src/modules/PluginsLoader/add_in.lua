package.path = package.path..";modules/PluginsLoader/lua_libs/?.lua"

function MP.Sleep(time_ms)
    local start = getTickCount()
    while getTickCount() - start < time_ms do end
end

MP.CallStrategy = {
    BestEffort = 0,
    Precise = 1
}
