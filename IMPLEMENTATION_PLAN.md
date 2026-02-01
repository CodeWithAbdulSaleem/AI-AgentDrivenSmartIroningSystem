# Implementation Plan - Debugging Sensors & Safety

## Goal
Fix the reported "inverted" cloth detection, ensure "Fabric Type" is logically consistent with detection, and eliminate random buzzer triggers.

## Proposed Changes

### `agent/dashboard.py`

#### [NEW] Advanced Settings (Sidebar)
- Add an `st.expander("⚙️ Advanced Settings")`.
- **Invert Sensor Logic**: A checkbox (default `False`).
    - If Checked: `fabric_detected = not raw_value`.
    - If Unchecked: `fabric_detected = raw_value`.
    - *Rationale*: Allows user to toggle behavior instantly without code edits.

#### [MODIFY] Cloth Detection Logic
- Use the "Invert Sensor Logic" checkbox state to determine `fabric_detected`.
- If `fabric_detected` is `False`:
    - Force `st.session_state.fabric_type = "Unknown"`.
    - Do NOT run "Detect Cloth Type" logic even if button clicked (or show warning).

#### [MODIFY] Buzzer Logic (Safety Patch)
- The user reports "shouting randomly". This might be due to fleeting high-temp readings or aggressive AI.
- **Fix**: Only allow AI to trigger buzzer if `temperature > 170` (Hard Safety Limit) OR if "Critical Manual Override" is active.
- Ignore AI `buzzer: true` if temperature is normal (< 150).

## Verification Plan

### Manual Verification
1.  **Cloth Detection**:
    - Toggle "Invert sensor logic". Verify "Cloth Detection" card flips between Red/Green.
    - Confirm "No Fabric" (Red) is shown when sensor is empty.
2.  **Fabric Type Sync**:
    - Ensure "Cloth Detection" is Red (No Fabric).
    - Check "Fabric Type" card. It should say "Unknown".
    - Try clicking "Detect Cloth Type". It should either warn "No Cloth Detected" or reset to "Unknown".
3.  **Buzzer**:
    - Monitor dashboard for 1-2 minutes.
    - Verify "Recommended Action" can recommend "IRON ON" without falsely triggering buzzer state.
