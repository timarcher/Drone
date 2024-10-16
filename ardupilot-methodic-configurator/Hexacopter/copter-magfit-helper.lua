--[[----------------------------------------------------------------------------

magfit-helper ArduPilot Lua script

Inserts a figure-8 pattern into an auto mission to help optimize magfit
results.

Several parameters are created for configuration:
    MAGH_CMD: nav script time command index (0-255)
    MAGH_B: pattern width scaling factor (1-2 should make nice figure 8s)
    MAGH_ALT_DELTA: (m) amount by which to climb during pattern execution
    MAGH_MIN_SPEED: speed at which to start the pattern (speed will increment
                    to WPNAV_SPEED during execution)
    MAGH_COUNT: number of figure 8s to fly
    MAGH_NUM_WP: spline count of lemniscate figure 8 pattern
    MAGH_USE_LOITER: insert a LOITER_UNLIM point into the mission prior
                     to the pattern to allow the user to download the inserted
                     waypoints and confirm location prior to execution;
                     can be disabled if the script must be used without a GCS;
                     use caution when disabling this feature!
    MAGH_LOG_ENABLE: log MAGH.Active during pattern execution when set to 1

The nav script time command to trigger waypoint creation takes two arguments:
    speed: speed at which to begin the pattern
    altitude delta: height above present altitude to climb during the pattern

CAUTION: This script is capable of engaging and disengaging autonomous control
of a vehicle.  Use this script AT YOUR OWN RISK.

-- Yuri -- Feb 2023

LICENSE - GNU GPLv3 https://www.gnu.org/licenses/gpl-3.0.en.html
------------------------------------------------------------------------------]]

local RUN_INTERVAL_MS = 100

-- MAVLink 'constants'
local MAV_SEVERITY_WARNING     =   4
local MAV_SEVERITY_NOTICE      =   5
local MAV_SEVERITY_INFO        =   6
local MAV_CMD_NAV_WAYPOINT     =  16
local MAV_CMD_NAV_LOITER_UNLIM =  17
local MAV_CMD_DO_JUMP          = 177
local MAV_CMD_DO_CHANGE_SPEED  = 178
local COPTER_MODE_AUTO         =   3

local function param_get(name)  -- error checking wrapper for param:get()
    return assert(param:get(name), ('MagHelper: %s parameter error'):format(name))
end

local wpnav_speed = param_get('WPNAV_SPEED') / 100

local PARAM_PREFIX    = 'MAGH'
local PARAM_TABLE_KEY = 117 -- unique index value between 0 and 200
local PARAM_TABLE     = {
--  { name, default value },
    { 'CMD',        117 },  -- script time command index
    { 'B',          1.2 },  -- lemniscate width scaling parameter
    { 'ALT_DELTA',   10 },  -- (m) climb this much above start altitude
    { 'MIN_SPEED',
        wpnav_speed / 2 },  -- (m/s) min speed for pattern
    { 'COUNT',        6 },  -- do this many laps
    { 'NUM_WP',      18 },  -- lemniscate segment count
    { 'USE_LOITER',   1 },  -- insert a loiter prior to the pattern
    { 'LOG_ENABLE',   1 },  -- set 1 to enable logging
}
local function add_params(key, prefix, tbl)
    assert(param:add_table(key, prefix, #tbl), ('Could not add %s param table.'):format(prefix))
    for num, data in ipairs(tbl) do
        assert(param:add_param(key, num, data[1], data[2]), ('Could not add %s%s.'):format(prefix, data[1]))
    end
end
add_params(PARAM_TABLE_KEY, PARAM_PREFIX .. '_', PARAM_TABLE)

local maghelper_cmd  = param_get(('%s_CMD'):format(PARAM_PREFIX))
local b              = param_get(('%s_B'):format(PARAM_PREFIX))
local alt_delta      = param_get(('%s_ALT_DELTA'):format(PARAM_PREFIX))
local min_speed      = param_get(('%s_MIN_SPEED'):format(PARAM_PREFIX))
local max_iterations = param_get(('%s_COUNT'):format(PARAM_PREFIX))
local num_waypoints  = param_get(('%s_NUM_WP'):format(PARAM_PREFIX))
local use_loiter     = param_get(('%s_USE_LOITER'):format(PARAM_PREFIX))
local log_enabled    = param_get(('%s_LOG_ENABLE'):format(PARAM_PREFIX))

local wp_start = 0
local wp_end   = 0
local base_alt = 0
local desired_speed = min_speed

local function log_state(bool_state)
    local uint_state = ({ [false] = 0, [true] = 1 })[bool_state]
    logger:write('MAGH', 'Active', 'B', '-', '-', uint_state)
end

local function is_active()
    if vehicle:get_mode() ~= COPTER_MODE_AUTO then return false end
    local nav_index = mission:get_current_nav_index()
    local result = nav_index >= wp_start and nav_index <= wp_end
    if log_enabled then log_state(result) end
    return result
end

local function get_wp_location(item)
    local loc = Location()
    loc:lat(item:x())
    loc:lng(item:y())
    loc:alt(math.floor(item:z() * 100))
    return loc
end

local function create_waypoint(location)
    local item = mavlink_mission_item_int_t()
    item:command(MAV_CMD_NAV_WAYPOINT)
    item:x(location:lat())
    item:y(location:lng())
    item:z(location:alt() / 100)
    return item
end

local function create_loiter(location)
    local item = create_waypoint(location)
    item:command(MAV_CMD_NAV_LOITER_UNLIM)
    return item
end

local function create_do_change_speed(speed)
    local item = mavlink_mission_item_int_t()
    item:command(MAV_CMD_DO_CHANGE_SPEED)
    item:param1(0)
    item:param2(speed)
    return item
end

local function create_do_jump(sequence_number, repeat_count)
    local item = mavlink_mission_item_int_t()
    item:command(MAV_CMD_DO_JUMP)
    item:param1(sequence_number)
    item:param2(repeat_count or 0)
    return item
end

local function read_mission()
    local items = {}
    for n = 1, mission:num_commands() do
        items[#items+1] = mission:get_item(n)
    end
    return items
end

local function write_mission(items)
    for index, item in ipairs(items) do
        mission:set_item(index, item)
    end
end

local function insert_pattern(items, index)
    if not items or not index then return end
    local location = assert(ahrs:get_location(), 'MagHelper: AHRS location error')
    local next_wp = assert(mission:get_item(index), 'MagHelper: Exit waypoint undefined')
    local next_wp_location = get_wp_location(next_wp)
    local bearing = location:get_bearing(next_wp_location)
    local rotation = bearing + math.rad(-90)
    local a = location:get_distance(next_wp_location) / 2
    local max_y = 0
    if use_loiter > 0 then
        table.insert(items, index, create_loiter(location))
    end
    wp_start = index + 1
    wp_end = wp_start
    base_alt = location:alt() / 100
    table.insert(items, wp_end, create_do_change_speed(desired_speed))
    wp_end = wp_end + 1
    location:offset_bearing(math.deg(bearing), a)
    for t = 0, math.rad(359), 2 * math.pi / num_waypoints do
        local x = a * math.cos(t) / (1 + math.sin(t)^2)
        local y = a * b * math.sin(t) * math.cos(t) / (1 + math.sin(t)^2)
        if y > max_y then max_y = y end
        local ofs_e = x * math.cos(rotation) + y * math.sin(rotation)
        local ofs_n = y * math.cos(rotation) - x * math.sin(rotation)
        local wp_loc = location:copy()
        wp_loc:offset(ofs_n, ofs_e)
        table.insert(items, wp_end, create_waypoint(wp_loc))
        wp_end = wp_end + 1
    end
    table.insert(items, wp_end, create_do_jump(wp_start, max_iterations - 1))

    -- ensure last waypoint is in the absolute reference frame
    wp_end = wp_end + 1
    items[wp_end]:frame(0)
    items[wp_end]:z(base_alt)

    gcs:send_text(MAV_SEVERITY_INFO, ('MagHelper: Pattern is %.1f x %.1f meters'):format(a * 2, max_y * 2))
    if use_loiter > 0 then
        gcs:send_text(MAV_SEVERITY_WARNING, ('MagHelper: Set waypoint %d to begin'):format(wp_start))
    end
    return items
end

local make_altitude_changes = 0
local lap_counter = 0
local last_wp_index = 0

function do_maghelper_pattern()
    if not is_active() then
        wp_start = 0
        wp_end = 0
        make_altitude_changes = 0
        lap_counter = 0
        last_wp_index = 0
        gcs:send_text(MAV_SEVERITY_NOTICE, 'MagHelper: Exiting pattern')
        return standby, RUN_INTERVAL_MS
    end

    local wp_index = mission:get_current_nav_index()
    if wp_index ~= last_wp_index and wp_index == wp_start + 1 then
        local speed_inc = (wpnav_speed - min_speed) / max_iterations * 2
        desired_speed = desired_speed + speed_inc * lap_counter * (make_altitude_changes ~ 1)
        if desired_speed > wpnav_speed then desired_speed = wpnav_speed end
        local ceil_alt = base_alt + alt_delta * make_altitude_changes
        local alt_change_index = math.random(wp_start + 1, wp_end - math.ceil(num_waypoints / 2))
        for i = wp_start, wp_end do
            local item = mission:get_item(i)
            if item then
                if item:command() == MAV_CMD_DO_CHANGE_SPEED then
                    item:param2(desired_speed)
                end
                if item:command() == MAV_CMD_NAV_WAYPOINT then
                    local alt = base_alt
                    if i >= alt_change_index and i <= alt_change_index + math.ceil(num_waypoints / 2) then
                        alt = ceil_alt
                    end
                    item:z(alt)
                end
                mission:set_item(i, item)
            end
        end
        make_altitude_changes = make_altitude_changes ~ 1
        lap_counter = lap_counter + 1
        gcs:send_text(MAV_SEVERITY_INFO, ('MagHelper: Lap %d, Speed %.1f, Alt Δ %.1f'):format(lap_counter, desired_speed, ceil_alt - base_alt))
    end

    last_wp_index = wp_index

    return do_maghelper_pattern, RUN_INTERVAL_MS
end

function standby()
    if not arming:is_armed() then return standby, RUN_INTERVAL_MS end

    if is_active() then
        gcs:send_text(MAV_SEVERITY_NOTICE, 'MagHelper: Entering pattern')
        return do_maghelper_pattern, RUN_INTERVAL_MS
    end

    local id, cmd, arg1, arg2 = vehicle:nav_script_time()

    if id and cmd == maghelper_cmd then
        -- poll parameters for changes
        maghelper_cmd = param_get(('%s_CMD'):format(PARAM_PREFIX))
        b              = param_get(('%s_B'):format(PARAM_PREFIX))
        alt_delta      = param_get(('%s_ALT_DELTA'):format(PARAM_PREFIX))
        min_speed      = param_get(('%s_MIN_SPEED'):format(PARAM_PREFIX))
        max_iterations = param_get(('%s_COUNT'):format(PARAM_PREFIX))
        num_waypoints  = param_get(('%s_NUM_WP'):format(PARAM_PREFIX))
        use_loiter     = param_get(('%s_USE_LOITER'):format(PARAM_PREFIX))
        log_enabled    = param_get(('%s_LOG_ENABLE'):format(PARAM_PREFIX))

        desired_speed = ({ [true] = arg1, [false] = min_speed })[arg1 > 0]
        alt_delta = ({ [true] = arg2, [false] = alt_delta })[arg2 > 0]
        local msn = read_mission()
        msn = insert_pattern(msn, mission:get_current_nav_index() + 1)
        write_mission(msn)
        vehicle:nav_script_time_done(id)
        return standby, RUN_INTERVAL_MS
    end

    if id then
        gcs:send_text(MAV_SEVERITY_NOTICE, ('MagHelper: Unknown NavScriptTime command, %d'):format(cmd))
    end

    return standby, RUN_INTERVAL_MS
end

gcs:send_text(MAV_SEVERITY_INFO, 'MagHelper: Script ready')

return standby, RUN_INTERVAL_MS
