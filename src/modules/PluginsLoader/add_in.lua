package.path = package.path..";modules/PluginsLoader/lua_libs/?.lua"

MP.Timer = {}
function MP.CreateTimer()
    local newObj = {
        startTime = os.clock()
    }
    setmetatable(newObj, { __index = MP.Timer })
    return newObj
end
function MP.Timer:GetCurrent()
    return os.clock() - self.startTime
end
function MP.Timer:Start()
    self.startTime = os.clock()
end

function MP.Sleep(time_ms)
    local start = getTickCount()
    while getTickCount() - start < time_ms do end
end

MP.CallStrategy = {
    BestEffort = 0,
    Precise = 1
}
