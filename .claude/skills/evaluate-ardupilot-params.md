# Skill: Evaluate ArduPilot Parameters

Evaluate the ArduPilot drone parameter configuration in this repository and produce a
structured safety/tuning/best-practices audit report.

## When to invoke

Use this skill when asked to:
- Evaluate, audit, or review the drone parameters
- Check if the drone is safe to fly
- Check if the tune is correct or complete
- Find missing or incorrectly configured parameters
- Advise on completing configuration steps (files 45–66)
- Compare configuration against ArduPilot best practices

## How to run this skill

Work through each step in order. Read files directly — do not summarize or skip sections.

---

### Step 1 — Discover the configuration

1. Find all AMC vehicle directories: `Glob("ardupilot-methodic-configurator/*/vehicle_components.json")`
2. If multiple directories exist, ask the user which one to evaluate.
3. Set `VEHICLE_DIR` = the matched directory (e.g., `ardupilot-methodic-configurator/FPVDroneV2/`)

---

### Step 2 — Read hardware specification

Read `$VEHICLE_DIR/vehicle_components.json` fully. Extract and note:
- **Frame**: manufacturer, model, TOW (kg)
- **FC**: manufacturer, model, firmware version
- **Battery**: chemistry, cell count, capacity mAh, per-cell voltages (max/arm/low/crit/min)
  - **Flag if model name says "4S" but cell count says 6**: these must be consistent
- **Motors**: KV rating
- **Props**: diameter (inches), blade count
- **ESC**: protocol (DShot speed), bidirectional DShot support
- **GPS**: model, connection serial port
- **RC Receiver**: protocol (CRSF/SBUS/etc.), connection serial port
- **ESC Telemetry**: UART or bidirectional DShot or None

---

### Vehicle Catalog — HexacopterV2

Use these facts when evaluating `HexacopterV2/` — do not re-derive from vehicle_components.json each time.

- **Frame:** RJX 1300mm hex-X, 14.2–16.7 kg TOW (36.85 lb with 12S battery + Gremsy T7 + Sony A6500 payload)
- **FC:** CubeOrangePlus, 3 IMUs (IMU1/2 heated to 60°C, IMU3 non-heated to 48°C)
- **Battery:** Tattu Plus 12S 16000mAh (params use 15800 mAh); DroneCAN smart battery on CAN2; analog backup via Kore carrier board on BATT2; `BATT_CURR_MULT=-1` (Tattu reports inverted current direction)
- **Voltage table (12S):** MAX=50.4, ARM≈47.3 (step 11 / 3.94V/cell), LOW=43.2 (3.6V), CRT=42.6 (3.55V)
- **ESC:** Hobbywing XRotor X6 Plus DroneCAN on CAN1; `MOT_PWM_TYPE=0` (not DShot — DroneCAN handles protocol); `CAN_D1_UC_ESC_BM=63` (all 6 ESCs); `ESC_HW_POLES=14` (not functionally used; RPM reported digitally over CAN)
- **GPS:** Dual Here4 via DroneCAN on CAN1; `GPS1_CAN_OVRIDE=119`, `GPS2_CAN_OVRIDE=118`; `GPS_AUTO_SWITCH=1`
- **RC/Telemetry:** Herelink HD on SERIAL1; `SERIAL1_BAUD=115` (115200); `BRD_SER1_RTSCTS=2`
- **Props:** 24 inch → `INS_GYRO_FILTER=20Hz`; initial notch guess 28Hz (must be refined from log); `ATC_ACCEL_R/P_MAX=35400`, `ATC_ACCEL_Y_MAX=14400`
- **Gimbal:** Gremsy T7 on serial (921600 baud), `MNT1_TYPE=6`; Camera: Sony A6500, `CAM1_TYPE=5`
- **Companion Pi:** SERIAL4 at 921600 baud, MAVLink2
- **Sensors:** HereFlow optical flow; TFMini-S LiDAR; DroneCAN proximity sensor type 14
- **No ADSB receiver** — do not set `ADSB_TYPE` or any ADSB-related serial protocol in this config
- **Upload status:** Last completed step 25 — not autotuned; initial PID estimates only

### Vehicle Catalog — Holybro-X500-QuadcopterV2

Use these facts when evaluating `Holybro-X500-QuadcopterV2/` — do not re-derive from vehicle_components.json each time.

- **Frame:** Holybro X500 V2, 500mm, ~3 kg TOW; test/dev platform for validating params before applying to the hexacopter
- **FC:** CubeOrangePlus, 3 IMUs
- **Battery:** Tattu 6S 10000mAh; analog Cube Orange Power Brick Mini on BATT1; **no BATT2**
- **Voltage table (6S):** MAX=25.2, ARM≈23.6 (3.93V/cell), LOW=21.6 (3.6V), CRT=21.3 (3.55V)
- **ESC:** Holybro BLHeli_S 20A on standard PWM main outputs; `MOT_PWM_TYPE=0`; **no ESC telemetry** → `INS_HNTCH_MODE=1` (throttle-based notch)
- **GPS:** Single Here4 via DroneCAN on CAN1; no GPS2; `CAN_D2/P2` enabled in step 05 but **no device on CAN2** (artifact of AI conversion — harmless)
- **RC:** RadioMaster TX16S + FrSky X8R SBUS on RCin; `SERIAL2_PROTOCOL=10` (FrSky SPort Passthrough for Yaapu telemetry)
- **Telemetry:** Holybro SiK 915MHz on SERIAL1 at 57600 baud
- **Props:** 10 inch 1045 → `INS_GYRO_FILTER=42Hz`; notch tuned to 58Hz from log
- **No gimbal, no camera** — X500 is a test platform only
- **Companion Pi:** SERIAL4 at 921600 baud, MAVLink2
- **ADSB:** ADSB receiver IS installed; `ADSB_TYPE=1`, `SERIAL5_PROTOCOL=1` in step 15 is correct
- **Upload status:** Last completed step 44 (full autotune done); steps 45–66 pending
- **CRITICAL KNOWN BUG:** `66_everyday_use.param` is a direct copy of the Hexacopter file — contains `BATT_ARM_VOLT=44.3` (impossible for 6S, max 25.2V → drone **cannot arm**), plus gimbal/camera params that don't exist on this vehicle. This file **must be rewritten** before use.

---

### Step 3 — Check upload status and complete.param staleness

1. Read `$VEHICLE_DIR/last_uploaded_filename.txt`
2. List all numbered `.param` files in the directory and identify the last one
3. If `last_uploaded_filename.txt` does not match the last numbered file, list the un-uploaded steps
4. **Important**: `complete.param` may be STALE if the AMC was not regenerated after uploading all files.
   If the last uploaded file is past step 30 (MagFit results), compare compass values between
   `complete.param` and the MagFit results file to detect staleness.
   - If `COMPASS_OFS_X` in `complete.param` ≠ value in `32_inflight_magnetometer_fit_results.param`,
     the file is stale. Warn the user to regenerate `complete.param` via AMC.

---

### Step 4 — Read parameter files

Read `$VEHICLE_DIR/complete.param` fully. This is the intended final parameter state.

**Note**: `complete.param` values may differ from individual `.param` files when:
- AMC was not re-run after manual edits to individual files
- QuickTune script modified its own parameters at runtime (e.g., `QUIK_GAIN_MARGIN`, `QUIK_OSC_SMAX`)
- MagFit results changed compass parameters after `complete.param` was last generated

When discrepancies are found, the individual numbered `.param` files take precedence for
determining what was actually uploaded to the FC.

---

### Step 5 — Run the evaluation checklist

Evaluate each category below. Mark: ✅ Good / ⚠️ Review / ❌ Issue.

#### 5A — Battery configuration
- `BATT_MONITOR` ≠ 0 (monitoring enabled)
- Cross-check: cell count × 4.2V = `MOT_BAT_VOLT_MAX` (within 0.1V)
- Cell count × cell-arm-voltage = `BATT_ARM_VOLT` (within 0.1V)
- Cell count × cell-low-voltage = `BATT_LOW_VOLT`
- Cell count × cell-crit-voltage = `BATT_CRT_VOLT`
- `BATT_CAPACITY` ≤ battery capacity mAh
- `BATT_FS_LOW_ACT` = 2 (RTL) — not 0 (disabled)
- `BATT_FS_CRT_ACT` = 1 (Land) — not 0 (disabled)

#### 5B — Failsafe completeness
- `FS_THR_ENABLE` = 1
- `FS_THR_VALUE` in range 925–975 µs
- `RC_FS_TIMEOUT` ≤ 2 seconds
- `FS_EKF_ACTION` ≠ 0
- `FS_CRASH_CHECK` = 1
- `FS_VIBE_ENABLE` = 1
- `FS_DR_ENABLE` ≥ 1
- `FENCE_ENABLE` = 1, `FENCE_TYPE` ≠ 0, `FENCE_ACTION` ≠ 0
- `ARMING_CHECK` = 1

#### 5C — PID and attitude tuning
- `ATC_ANG_RLL_P`, `ATC_ANG_PIT_P`, `ATC_ANG_YAW_P`: flag if > 25 (high but may be valid post-AutoTune)
- `ATC_RAT_RLL_SMAX`, `ATC_RAT_PIT_SMAX`, `ATC_RAT_YAW_SMAX` > 0 (set by QuickTune, typically 50)
- `MOT_THST_HOVER` between 0.1 and 0.4
- `MOT_THST_EXPO`: for ducted props flag if > 0.55 (recommend 0.45–0.55)
- **`FLTMODE*` check**: if any flight mode is set to 15 (AutoTune) and autotune is complete,
  flag it — AutoTune should be removed from everyday switch positions
- `QUIK_ENABLE` = 0 for everyday flying
- `PSC_ACCZ_P` should equal `MOT_THST_HOVER` (final learned value)
- `PSC_ACCZ_I` should equal 2 × `MOT_THST_HOVER`
  - If they differ significantly from MOT_THST_HOVER, suggest updating (they were calculated
    at an earlier hover estimate and should be refreshed to the final value)

#### 5D — Harmonic notch filter
- `INS_HNTCH_ENABLE` = 1
- `INS_HNTCH_MODE` = 3 (ESC RPM tracking) — preferred over throttle-based (1)
- `INS_HNTCH_HMNCS` ≥ 3 (1st and 2nd harmonics)
- `INS_HNTCH_BW` ≈ `INS_HNTCH_FREQ`/4 (e.g., 35 Hz for 141 Hz fundamental)
- `INS_HNTCH_ATT` ≥ 30 dB
- `INS_HNTCH_OPTS` = 14 (multi-source + loop rate update + all IMUs) — optimal for FPV
- `SERVO_BLH_BDMASK` covers all motor outputs (bidirectional DShot provides RPM for mode=3)
- Second notch (`INS_HNTC2_ENABLE`) is NOT required when using multi-source mode=3
- `ATC_RAT_*_NTF` and `ATC_RAT_*_NEF` should be 0 (PID notch disabled when main notch covers it)

#### 5E — EKF configuration
- `AHRS_EKF_TYPE` = 3 and `EK3_ENABLE` = 1
- `EK3_SRC1_POSXY` = 3 (GPS), `EK3_SRC1_VELXY` = 3 if GPS equipped
- `EK3_SRC2_POSXY` = 5 (OpticalFlow) if optical flow hardware is present
- `EK3_SRC_OPTIONS` = 1 if multiple position sources configured
- `EK3_MAG_CAL` = 3 (when GPS available)
- Compass orientation: check if `COMPASS_ORIENT` value is consistent with physical mounting
  and verify it hasn't changed unexpectedly between file 14 and file 32

#### 5F — Flight modes
- At least one FLTMODE = 6 (RTL) — must be easily accessible
- At least one FLTMODE = 9 (Land)
- Stabilize (0) available as emergency manual override
- **No FLTMODE = 15 (AutoTune) after autotune is complete** — flag and recommend replacing
  with Auto (3), PosHold (16), or Sport (13)

#### 5G — Safety and motor parameters
- `MOT_SPIN_ARM` < `MOT_SPIN_MIN` < `MOT_SPIN_MAX` ≤ 0.95
- `MOT_PWM_TYPE` matches ESC protocol (6=DShot600, 7=DShot1200)
  — check against components JSON and verify file 09 isn't setting wrong type
- `SERVO_BLH_POLES` or `ESC_HW_POLES` = motor pole count
- `DISARM_DELAY` ≥ 2 seconds
- `TKOFF_RPM_MIN` > 0 (dead motor detection)
- `GPS_NAVFILTER` = 8 (Airborne 4G for FPV)
- `RTL_ALT` > 0
- `GPS1_RATE_MS` ≥ 200 (≤ 5Hz; per ArduPilot docs 5Hz is recommended max for EKF)

#### 5H — Serial/hardware consistency
- RC receiver serial port → `SERIAL{N}_PROTOCOL` = 23 (CRSF)
  - Note: ArduPilot auto-switches CRSF to 400000 baud internally; `SERIAL6_BAUD=57` is fine
- GPS serial port → `SERIAL{N}_PROTOCOL` = 5
- `SERIAL7_PROTOCOL=16` (ESC UART telemetry): flag if components JSON says no UART ESC
  telemetry cable — if using bidirectional DShot, set to -1
- Check for any `SERIAL{N}_PROTOCOL` that doesn't match components JSON

---

### Step 6 — Upload gap analysis (if files 45–66 not uploaded)

When the last uploaded file is ≤ 44 and files 45–66 exist, evaluate each file and advise:

**Files 45–49 (autotune finish, wind estimation):**
- File 45: Upload as-is (sets `ATC_THR_MIX_MAX=0.9`)
- File 46: Upload as-is (D_FF = 0)
- File 47: Requires calculation of `EK3_DRAG_BCOEF_X/Y` from drone TOW and frontal area,
  or can be skipped (leave at 0) for simple everyday use
- File 48: Upload as-is (barometer compensation disabled = 0)
- File 49: Upload as-is (clears disarmed/replay logging)

**Files 50–57 (system identification) — SKIP unless specifically doing SysID:**
- **Critical warning**: Files 50–56 deliberately reset `ATC_ANG_RLL_P`, `ATC_ANG_PIT_P`,
  `ATC_ANG_YAW_P` to 4.5 (default) for the chirp injection process. Uploading without
  understanding the process will OVERWRITE autotune results.
- File 57 template contains a bug: `PSC_ACCZ_I=1` should be 2×`MOT_THST_HOVER`
- Recommend skipping unless doing advanced frequency response analysis

**File 60 (position controller):**
- `ANGLE_MAX`: Template has 3000 (too restrictive). Conservative pilot: 4000 (40°). Aggressive: 4500 (45°). Match pilot skill.
- `LOIT_BRK_DELAY`: Template sets 0.5; if file 16 set it to 0.1 (more responsive), KEEP 0.1 by omitting or overriding
- `WP_NAVALT_MIN,2`: Add for mission safety (prevents horizontal nav below 2m)
- Conservative pilot profile: reduce WPNAV_SPEED, PILOT_ACCEL_Z, PILOT_SPEED_DN vs AMC defaults
- Check for duplicates vs file 16: LOIT_BRK_DELAY, LOIT_BRK_JERK, WPNAV_SPEED_UP/DN already set in f16

**File 61 (guided operation):** Upload as-is.

**File 62 (precision land) — MODIFY BEFORE UPLOADING:**
- Template sets `RC10_OPTION=0` and `RC11_OPTION=0`
- These would REMOVE Motor Emergency Stop (option 31) and Lost Copter Sound (option 30)
- Remove those lines or restore: `RC10_OPTION=31`, `RC11_OPTION=30`

**File 63 (optical flow setup) — MODIFY BEFORE UPLOADING:**
- Template sets `FLOW_TYPE=0` (DISABLES optical flow sensor!)
- If optical flow hardware is present (FLOW_TYPE=5 in earlier files), do NOT set FLOW_TYPE=0
- Replace content with ONLY EKF backup source config. FLOW_TYPE/POS already set in file 15 — do NOT repeat.
- EK3_SRC numbering (ArduCopter 4.6.3 confirmed): POSXY/VELXY: 3=GPS, 5=OpticalFlow; POSZ: 1=Baro; All: 0=None
  - `EK3_SRC2_POSXY=0` (None — optical flow cannot provide absolute position)
  - `EK3_SRC2_VELXY=5` (OpticalFlow horizontal velocity backup — confirmed value is 5, NOT 2)
  - `EK3_SRC2_POSZ=1` (Baro)
- Remove any `RC8_OPTION=0` or `RC9_OPTION=0` lines that would reset switch assignments

**File 64 (optical flow results) — MODIFY BEFORE UPLOADING:**
- Template sets `FLOW_FXSCALER=0` and `FLOW_FYSCALER=0`
- These OVERWRITE already-calibrated optical flow scalers (e.g., -36 and -118 from file 15)
- Update to preserve the calibrated values

**File 65 (use optical flow instead of GNSS) — SKIP:**
- Switches optical flow to primary, GPS to secondary — risky for outdoor flying
- If optical flow as backup was configured in file 63, skip file 65

**File 66 (everyday use) — ADD these items to existing content (minimum set):**
- `FLTMODE4,3` — restore from AutoTune (15) to Auto or other useful mode
- `SERIAL7_PROTOCOL,-1` — if no UART ESC telemetry cable and using bidirectional DShot
- `QUIK_ENABLE,0` — already required, verify it's there
- `RTL_ALT,500` — 5m RTL altitude (default 1500=15m is excessive for near-pilot FPV)
- `RTL_CLIMB_MIN,100` — rise 1m before horizontal RTL (obstacle clearance)
- `PILOT_Y_RATE,45` — if default 202.5 is too fast; conservative pilot: use 45 deg/s
- **Before adding any param to file 66: check if already set earlier in the sequence with the same value. Only include genuine changes.**
- PSC_ACCZ_P/I: only update if diff > 5% from current value (stale early-estimate vs final hover)

---

### Step 7 — Output the report

Structure the report as follows:

```
## ArduPilot Parameter Audit — [Vehicle Directory Name]
Hardware: [brief one-liner from components JSON]
Firmware: [version]
Upload status: [complete / INCOMPLETE — last uploaded: filename]
complete.param status: [current / STALE — MagFit values not reflected]

### 🔴 CRITICAL (fix before next flight)
[param_name = value → problem → recommended action]

### 🟡 TUNING (review / consider adjusting)
[Each item]

### 🔵 BEST PRACTICES (minor improvements)
[Each item]

### ✅ LOOKS GOOD
[Brief bullet list]
```

---

### Step 8 — Offer to apply fixes

Ask: "Would you like me to apply any of these fixes to the parameter files?"

If yes:
- Make changes in the **specific numbered step `.param` file** that owns that parameter.
- For new parameters without a clear owner, add to file 66 (`everyday_use.param`) or create
  `67_post_audit_fixes.param`.
- Do NOT edit `complete.param` directly — it is regenerated by AMC from all the individual files.
- After editing, note which files need to be re-uploaded to the FC via AMC.
- **Never** upload files 50–56 (SysID) without explicit user understanding that this will
  temporarily reset autotune gains during the test flights.
- **Never set a param to its ArduPilot default value** — if the value matches the firmware
  default, omit it entirely. Only params that differ from the default belong in the config files.
  Check defaults at https://ardupilot.org/copter/docs/parameters-Copter-stable-V4.6.3.html

---

## Reference: Known-Good Values — HexacopterV2 (RJX 1300mm, 12S, AMC 4.6.3)

| Parameter | Value | Notes |
|---|---|---|
| `MOT_BAT_VOLT_MAX` | 50.4 | 12 × 4.2V |
| `MOT_BAT_VOLT_MIN` | 42.6 | 12 × 3.55V (= BATT_CRT_VOLT; consider lowering to 40–41) |
| `BATT_ARM_VOLT` | 47.3 | 12 × 3.94V (step 11); step 66 lowers to 44.3 = 3.69V/cell ⚠️ |
| `BATT_LOW_VOLT` | 43.2 | 12 × 3.6V |
| `BATT_CRT_VOLT` | 42.6 | 12 × 3.55V |
| `BATT_CAPACITY` | 15800 | Tattu 12S 16000mAh |
| `BATT_CURR_MULT` | -1 | Tattu inverted current — do not remove |
| `CAN_D1_UC_ESC_BM` | 63 | All 6 ESCs (bitmask 0b00111111) |
| `CAN_D1_UC_OPTION` | 128 | Hobbywing ESC DroneCAN option |
| `GPS1_CAN_OVRIDE` | 119 | DroneCAN node ID for GPS1 |
| `GPS2_CAN_OVRIDE` | 118 | DroneCAN node ID for GPS2 |
| `INS_GYRO_FILTER` | 20 | 24-inch props |
| `INS_HNTCH_FREQ` | 28 | Initial estimate only — tune from first hover log |
| `MOT_PWM_TYPE` | 0 | Standard (DroneCAN ESCs, not DShot) |
| `MOT_THST_EXPO` | 0.74 | From component editor; validate from hover data |
| `MOT_THST_HOVER` | ~0.3–0.5 | Expected range for 35-lb hex; 0.2 is unlearned estimate |
| `MOT_SPIN_ARM` | 0.05 | |
| `MOT_SPIN_MIN` | 0.09 | |
| `TKOFF_RPM_MIN` | 200 | Dead motor detection |
| `SERIAL1_BAUD` | 115 | Herelink 115200 baud |
| `MNT1_TYPE` | 6 | Gremsy T7 |
| `CAM1_TYPE` | 5 | Sony A6500 via MAVLink |
| `LAND_SPEED` | 25 | Recommend for 35-lb aircraft (default 50 cm/s causes hard landings) |

## Reference: Known-Good Values — Holybro X500 QuadcopterV2 (6S, AMC 4.6.3)

| Parameter | Value | Notes |
|---|---|---|
| `MOT_BAT_VOLT_MAX` | 25.2 | 6 × 4.2V |
| `MOT_BAT_VOLT_MIN` | 21.3 | 6 × 3.55V (step 14 accidentally set 19.8 — fix to 21.3) |
| `BATT_ARM_VOLT` | 23.6 | 6 × 3.93V; step 66 MUST NOT set 44.3 (hexacopter value) |
| `BATT_LOW_VOLT` | 21.6 | 6 × 3.6V |
| `BATT_CRT_VOLT` | 21.3 | 6 × 3.55V |
| `BATT_CAPACITY` | 10000 | Tattu 6S |
| `INS_GYRO_FILTER` | 42 | 10-inch props |
| `INS_HNTCH_MODE` | 1 | Throttle-based (no ESC telemetry on BLHeli_S PWM) |
| `INS_HNTCH_FREQ` | 58 | Tuned from log |
| `INS_HNTCH_BW` | 14 | FREQ/4 |
| `INS_HNTCH_REF` | 0.249 | Hover throttle reference |
| `MOT_PWM_TYPE` | 0 | Standard PWM (BLHeli_S) |
| `MOT_THST_EXPO` | 0.65 | 10-inch props |
| `MOT_THST_HOVER` | ~0.244 | Learned (step 24 PSC_ACCZ_P=0.244 confirms this) |
| `MOT_SPIN_ARM` | 0.1 | |
| `MOT_SPIN_MIN` | 0.15 | |
| `PSC_ACCZ_P` | 0.244 | = learned MOT_THST_HOVER |
| `PSC_ACCZ_I` | 0.488 | = 2× MOT_THST_HOVER |
| `ATC_RAT_RLL_P/I` | 0.093694 | Final autotune (step 44) |
| `ATC_RAT_PIT_P/I` | 0.140066 | Final autotune (step 44) |
| `ATC_RAT_YAW_P` | 0.86697 | Final autotune (step 42) |
| `ATC_RAT_RLL_SMAX` | 50 | Add to step 66 (not set by AutoTune) |
| `ATC_RAT_PIT_SMAX` | 50 | Add to step 66 (not set by AutoTune) |
| `ATC_RAT_YAW_SMAX` | 10 | Add to step 66 (not set by AutoTune) |
| `PSC_ACCZ_SMAX` | 15 | Add to step 66 (not set by AutoTune) |
| `TKOFF_RPM_MIN` | 100 | Add to step 66 (not explicitly set) |
| `SERIAL1_BAUD` | 57 | SiK 915MHz 57600 baud |
| `SERIAL2_PROTOCOL` | 10 | FrSky SPort for Yaapu telemetry |

## Reference: Known-Good Values for This Drone (iFlight Protek 35, 6S, AMC 4.6.3)

| Parameter | Value | Source |
|---|---|---|
| `MOT_THST_HOVER` | 0.144385 | Learned |
| `PSC_ACCZ_P` | 0.14438 | = MOT_THST_HOVER |
| `PSC_ACCZ_I` | 0.28877 | = 2 × MOT_THST_HOVER |
| `INS_HNTCH_FREQ` | 141.4 Hz | Notch web tool |
| `INS_HNTCH_BW` | 35 Hz | ~FREQ/4 |
| `COMPASS_ORIENT` | 6 (Yaw270) | MagFit result |
| `FLOW_FXSCALER` | -36 | Calibrated |
| `FLOW_FYSCALER` | -118 | Calibrated |
| `ANGLE_MAX` | 4000 | Conservative pilot (40°) |
| `PILOT_Y_RATE` | 45 | Conservative yaw rate |
| `RTL_ALT` | 500 | 5m for near-pilot FPV |
| `RTL_CLIMB_MIN` | 100 | Rise 1m before horizontal RTL |
| `MOT_THST_EXPO` | 0.50 | Ducted props |
| `AUTOTUNE_AGGR` | 0.1 | Max aggressiveness |
| `GPS1_RATE_MS` | 200 | 5Hz (ArduPilot recommended max) |

## Reference: Common ArduPilot 4.6 best-practice values for FPV cinewhoops

| Parameter | Recommended | Notes |
|---|---|---|
| `ANGLE_MAX` | 4000–4500 | 3000 too restrictive; match pilot skill (this pilot: 4000) |
| `MOT_THST_EXPO` | 0.45–0.55 | Lower for ducted props; 0.65 is too high |
| `MOT_SPIN_ARM` | 0.02–0.04 | Just barely spins |
| `MOT_SPIN_MIN` | 0.05–0.08 | Above arm, below flight |
| `ATC_THR_MIX_MAN` | 0.5 | Balance attitude vs throttle |
| `ATC_THR_MIX_MAX` | 0.5 (Loiter/AltHold) or 0.9 (manual modes) | |
| `ATC_INPUT_TC` | 0.15–0.20 | Cinematic: 0.20, Sport: 0.10 |
| `GPS_NAVFILTER` | 8 | Airborne 4G for FPV |
| `GPS1_RATE_MS` | 200 | 5Hz max per ArduPilot docs |
| `INS_HNTCH_MODE` | 3 | Dynamic RPM tracking via bidirectional DShot |
| `INS_HNTCH_HMNCS` | 3 | 1st + 2nd harmonics |
| `INS_HNTCH_OPTS` | 14 | Multi-source + loop rate + all IMUs |
| `QUIK_ENABLE` | 0 | Disable for everyday flying |
| `FENCE_ENABLE` | 1 | Always |
| `FS_THR_ENABLE` | 1 | Always |
| `FS_VIBE_ENABLE` | 1 | Always |
| `TKOFF_RPM_MIN` | 100–300 | Dead-motor detection |

## Lessons Learned (from FPVDroneV2 audit)

1. **`complete.param` can be stale** — especially after MagFit changes compass orientation.
   Always cross-check compass values against file 32 results.

2. **QuickTune modifies its own runtime params** — `QUIK_GAIN_MARGIN`, `QUIK_OSC_SMAX`,
   `QUIK_MAX_REDUCE` in `complete.param` may differ from setup file 29. This is expected.

3. **FLTMODE4=15 (AutoTune) is set during mandatory hardware setup and never auto-restored**.
   Always check and reset in file 66 after tuning is done.

4. **Files 50–56 (SysID) contain ATC_ANG_*_P=4.5** — this is intentional for the SysID
   chirp process but will destroy autotune gains if uploaded naively. Always warn user.

5. **File 62 template zeros out RC10 and RC11 options** — removes Motor E-Stop and Lost
   Copter Sound. Always preserve these safety RC options.

6. **Files 63–64 (optical flow) template will disable flow and reset calibrated scalers**.
   If optical flow hardware is present, these files must be customized before uploading.

7. **File 09 may set wrong DShot type** — component editor may output DShot1200 (7) when
   hardware is DShot600 (6). Verify `MOT_PWM_TYPE` matches the actual ESC protocol.

8. **PSC_ACCZ_P/I go stale** — calculated in file 24 at initial hover estimate; need
   updating to the final `MOT_THST_HOVER` value in file 66.

9. **GPS 5Hz (200ms) is the recommended max** per ArduPilot docs. Do not recommend 10Hz.

10. **Compass ORIENT can change from initial calibration to MagFit result** — this is normal
    and MagFit's value is more accurate. Verify heading post-MagFit against known compass direction.

11. **Conservative pilot profile for this drone**: ANGLE_MAX=4000, PILOT_Y_RATE=45 deg/s,
    WPNAV_SPEED≤500, PILOT_SPEED_DN≤150. When proposing params, default to gentle values
    and prioritize stability and reaction time over responsiveness.

12. **No unnecessary duplicate params across files**: Before adding a param to any file, check
    if already set in an earlier file with the same value. Only include a param when its value
    is genuinely changing from what was set earlier. Key anchors: FLOW_TYPE/POS in file 15;
    LOIT/WPNAV in file 16. Intentional overrides (value changes) are always OK.

13. **EK3_SRC2_VELXY=5 for optical flow** (not 2): The correct source value for OpticalFlow
    horizontal velocity in ArduCopter 4.6.3 is 5, not 2. EK3_SRC2_POSXY must be 0 (None)
    because optical flow cannot provide absolute position.

14. **PSC_ACCZ_P/I must use actual MOT_THST_HOVER, not generic forum values**: xfacta and
    others often recommend PSC_ACCZ_P=0.3, I=0.6. These apply to ~30% hover throttle vehicles.
    Formula: P = MOT_THST_HOVER, I = 2 × MOT_THST_HOVER. For this drone (14.4% hover):
    P=0.144, I=0.289. Never apply generic xfacta values without checking actual hover throttle.

15. **PILOT_Y_RATE formula (0.005×ATC_ACCEL_Y_MAX) breaks for AutoTuned vehicles**: On a
    heavily-tuned small quad, ATC_ACCEL_Y_MAX=387011 centideg/s² gives PILOT_Y_RATE=1935 deg/s
    (nonsensical). Use a fixed conservative value (45 deg/s for this pilot) instead of the formula.

16. **SysID skip files and other dangerous template files should be comment-only**: Replace
    content with a plain comment warning. A comment-only file uploaded via AMC applies zero
    param changes — completely safe. Key skip files: 50–57 (SysID), 65 (optical flow primary).

17. **Safety double-check before any upload**: Verify no RC_OPTION=0 (removes switch function),
    FLOW_TYPE≠0 (disables sensor), FLTMODE≠15 (AutoTune stuck on), ATC_ANG_*_P≠4.5 (SysID
    template). Always regenerate complete.param after all uploads. Errors have real consequences.

18. **X500 `66_everyday_use.param` was copied from the Hexacopter file** — it contains
    `BATT_ARM_VOLT=44.3V` (6S maximum is 25.2V, so this is **physically impossible** — drone
    will never arm), plus `MNT1_TYPE=6` and all gimbal params, and `CAM1_TYPE=5`. Always
    verify voltage thresholds match the actual cell count when editing file 66. Cross-check:
    cell_count × 4.2 = `MOT_BAT_VOLT_MAX`; if arm voltage exceeds that, the file is wrong.

19. **DroneCAN ESCs use `MOT_PWM_TYPE=0`** — not DShot. The DroneCAN driver handles the
    ESC protocol over CAN. DShot types (6=DShot600, 7=DShot1200) only apply to ESCs wired
    directly to servo PWM outputs. Do not set `MOT_PWM_TYPE=6` for a hexacopter with
    DroneCAN ESCs like the Hobbywing XRotor X6 Plus.

20. **`ESC_HW_POLES` is not functionally used with DroneCAN ESCs** — RPM is reported
    digitally over CAN from the ESC firmware itself, not derived from back-EMF counting.
    The value is still correct to set (for documentation), but it does not affect notch
    filter behavior. With `INS_HNTCH_MODE=3`, ArduPilot uses the CAN-reported RPM directly.

21. **For 24-inch props, `INS_HNTCH_FREQ=28Hz` is only the initial pre-flight estimate**
    (= 1.4 × `INS_GYRO_FILTER`=20). Actual motor noise at hover for 150KV motors at 12S
    is approximately 67–100 Hz (RPM ≈ 4000–6000 → Hz = RPM/60). The 28 Hz filter will
    miss the actual noise band entirely. Always do a log-analyzed hover and use the notch
    filter web tool to find the true fundamental before relying on this filter.

22. **`CAN_D1_UC_ESC_BM` bitmask** — for a 6-motor hexacopter the correct value is 63
    (0b00111111, ESCs 1–6). For a 4-motor quadcopter it would be 15 (0b00001111, ESCs 1–4).
    Verify this when reviewing hexacopter vs quadcopter configs to avoid missing motors.

23. **`BATT_CURR_MULT=-1` for the Tattu Plus smart battery** — the Tattu Plus DroneCAN
    battery reports current with inverted polarity that ArduPilot reads as negative. Without
    this multiplier, current draw and mAh consumed appear negative, and remaining capacity
    calculations are inverted. Do not remove this param from the hexacopter config.

24. **Large drone hover throttle is far from the `MOT_THST_HOVER=0.2` initial estimate** —
    a 35-pound hexacopter with 24-inch props at 12S will likely hover at 30–50% throttle
    (`MOT_THST_HOVER≈0.3–0.5`). `PSC_ACCZ_P/I` calculated in step 24 at 0.186/0.372 (from
    the 0.2 estimate) will need significant updating after the real hover throttle is learned
    via `MOT_HOVER_LEARN=2`. Do not fly the hexacopter without at minimum completing step 29
    (QuickTune) to let the system learn the actual value.

25. **X500 `FLTMODE3=3` and `FLTMODE4=3` are duplicates (both Auto)** — both RC switch
    positions 3 and 4 do the same thing. Set `FLTMODE4=16` (PosHold) or `FLTMODE4=0`
    (Stabilize) for additional utility and emergency manual override capability.

26. **SMAX params must be set manually after AutoTune** — `ATC_RAT_*_SMAX` and
    `PSC_ACCZ_SMAX` remain at 0 (disabled) until QuickTune sets them (typically ~50).
    For the X500 which used AutoTune (not QuickTune), these were never set. Add to step 66:
    `ATC_RAT_RLL_SMAX=50`, `ATC_RAT_PIT_SMAX=50`, `ATC_RAT_YAW_SMAX=10`, `PSC_ACCZ_SMAX=15`.
    Without SMAX, rate oscillations from disturbances have no slew-rate protection.

27. **Never explicitly set a param that already matches the ArduPilot default** — unless
    the intent is to protect it from a future firmware default change or it is being set to
    a non-default value elsewhere in the sequence. Repeating defaults in param files:
    (a) makes files harder to read and audit, (b) silently breaks the AMC "no-repeat" workflow,
    and (c) makes firmware upgrades harder because stale defaults block clean migration.
    **How to apply:** Before adding any param to any step file, look up its ArduPilot 4.6.3
    default in the official param list. If the value you're setting equals the default and you
    have no intention of changing it, omit it entirely. Only include a param when its value
    is genuinely different from the default, or when an earlier step set it to X and this step
    deliberately changes it to Y.
