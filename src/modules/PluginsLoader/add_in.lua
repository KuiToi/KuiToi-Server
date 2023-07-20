function MP:GetServerVersion()
    ver = MP:_GetServerVersion()
    return ver[0], ver[1], ver[2]
end
