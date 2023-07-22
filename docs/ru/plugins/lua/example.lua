print("example.lua")

--CreateTimer Testing
local mytimer = MP.CreateTimer()
--.--.--.--.--.--.--.

--GetOSName Testing
print("OS Name: "..MP.GetOSName())
--.--.--.--.--.--.-

--GetServerVersion Testing
local major, minor, patch = MP.GetServerVersion()
print("Server Version: "..major.."."..minor.."."..patch)
--.--.--.--.--.--.--.--.--

--Events Testing--
function handleChat(player_id, player_name, message)
    print("Lua handleChat:", player_id, player_name, message, "; Uptime: "..mytimer:GetCurrent())
    return 1
end

MP.RegisterEvent("onChatMessage", "handleChat")
--.--.--.--.--.--.

function onInit()
    print("Initializing ready!")
end
