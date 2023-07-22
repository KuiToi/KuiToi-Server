package.path = package.path..";modules/PluginsLoader/lua_libs/?.lua"

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

function MP.CreateTimer()
  MP.log.debug("request MP.CreateTimer()")
  local timer = {}
  timer.start_time = os.clock()

  function timer:GetCurrent()
    return os.clock() - self.start_time
  end

  function timer:Start()
    self.start_time = os.clock()
  end

  return timer
end

----Timer object for event timers
--local TimedEvent = {}
--TimedEvent.__index = TimedEvent
--
--function TimedEvent:new(interval_ms, event_name, strategy)
--  local o = {}
--  setmetatable(o, self)
--  o.interval = interval_ms
--  o.event_name = event_name
--  o.strategy = strategy or MP.CallStrategy.BestEffort
--  o.last_trigger_time = 0
--  o.timer = MP.CreateTimer()
--  return o
--end
--
--function TimedEvent:trigger()
--  MP.TriggerLocalEvent(self.event_name)
--  self.last_trigger_time = self.timer:GetCurrent()
--end
--
--function TimedEvent:is_ready()
--  local elapsed_time = self.timer:GetCurrent() - self.last_trigger_time
--  return elapsed_time * 1000 >= self.interval
--end
--
---- Event timer management functions
--MP.event_timers = {}
--MP.event_timers_mutex = {}
--
--function MP.CreateEventTimer(event_name, interval_ms, strategy)
--  MP.log.debug("request MP.CreateEventTimer()")
--  strategy = strategy or MP.CallStrategy.BestEffort
--  local timer = TimedEvent:new(interval_ms, event_name, strategy)
--  table.insert(MP.event_timers, timer)
--  MP.log.debug("created event timer for \"" .. event_name .. "\" with " .. interval_ms .. "ms interval")
--end
--
--function MP.CancelEventTimer(event_name)
--  MP.log.debug("request MP.CancelEventTimer()")
--  for i, timer in ipairs(MP.event_timers) do
--    if timer.event_name == event_name then
--      table.remove(MP.event_timers, i)
--    end
--  end
--  MP.log.debug("cancelled event timer for \"" .. event_name .. "\"")
--end
--
--function MP.run_event_timers()
--  MP.log.debug("request MP.run_event_timers()")
--  while true do
--    -- Wait for some time before checking timers
--    MP.Sleep(100)
--
--    -- Check each timer and trigger events as necessary
--    for _, timer in ipairs(MP.event_timers) do
--      if timer:is_ready() then
--        if timer.strategy == MP.CallStrategy.Precise then
--          while timer:is_ready() do
--            timer:trigger()
--          end
--        else
--          timer:trigger()
--        end
--      end
--    end
--  end
--end
