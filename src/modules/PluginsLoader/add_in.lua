package.path = package.path..";modules/PluginsLoader/lua_libs/?.lua"

function MP.Sleep(time_ms)
    local start = getTickCount()
    while getTickCount() - start < time_ms do end
end

MP.CallStrategy = {
    BestEffort = 0,
    Precise = 1
}

MP.Settings = {
    Debug = 0,
    Private = 1,
    MaxCars = 2,
    MaxPlayers = 3,
    Map = 4,
    Name = 5,
    Description = 6
}
