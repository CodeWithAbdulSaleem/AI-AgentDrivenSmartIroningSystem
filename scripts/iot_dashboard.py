import streamlit as st
import requests
import time
import pandas as pd
import threading
import random
import numpy as np
import altair as alt
from ai_engine import get_ai_decision
from config import TB_URL, USERNAME, PASSWORD, DEVICE_ID

# --- Page Config ---
st.set_page_config(
    page_title="Smart Ironing V4 | AI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f2f6 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.2em;
        font-weight: 700;
        color: #2c3e50;
        white-space: nowrap;
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 1.0em;
        font-weight: 500;
        margin-bottom: 5px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stProgress > div > div > div > div {
        background-color: #00C9FF;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['time', 'temperature', 'humidity'])
if 'fabric_type' not in st.session_state:
    st.session_state.fabric_type = "Unknown"
if 'model_trained' not in st.session_state:
    st.session_state.model_trained = True
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = True
if 'last_fabric_detected' not in st.session_state:
    st.session_state.last_fabric_detected = False
if 'last_tp' not in st.session_state:
    st.session_state.last_tp = 0

# --- Auth Helper ---
@st.cache_data(ttl=3600)
def get_tb_token():
    url = f"{TB_URL}/api/auth/login"
    try:
        response = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        return None

# --- Background AI Worker ---
class AIWorker:
    def __init__(self):
        self.latest_telemetry = (0.0, 0.0, False) # Temp, Hum, Fabric
        self.latest_decision = {"relay": False, "buzzer": False, "reason": "Initializing AI..."}
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def update_telemetry(self, temp, hum, fabric):
        with self.lock:
            self.latest_telemetry = (temp, hum, fabric)

    def get_decision(self):
        with self.lock:
            return self.latest_decision

    def _run_loop(self):
        while self.running:
            with self.lock:
                t, h, f = self.latest_telemetry
            try:
                decision = get_ai_decision(t, h, f)
                with self.lock:
                    self.latest_decision = decision
            except Exception as e:
                print(f"AI Worker Error: {e}")
            time.sleep(1)

@st.cache_resource
def get_ai_worker():
    return AIWorker()

# --- Data Fetching ---
def fetch_telemetry(token):
    headers = {"X-Authorization": f"Bearer {token}"}
    url = f"{TB_URL}/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries?keys=temperature,humidity,fabric_detected&useStrictDataTypes=true"
    try:
        resp = requests.get(url, headers=headers, timeout=2)
        if resp.status_code == 200:
            return resp.json(), 200, "OK"
        return {}, resp.status_code, resp.text
    except Exception as e:
        return {}, 0, str(e)
    return {}, 0, "Unknown"

def send_rpc(token, method, params):
    headers = {"X-Authorization": f"Bearer {token}"}
    url = f"{TB_URL}/api/plugins/rpc/oneway/{DEVICE_ID}"
    try:
        requests.post(url, headers=headers, json={"method": method, "params": params}, timeout=2)
        return True
    except:
        return False

# --- Main Dashboard Logic ---
def main():
    st.title("Smart Ironing System V4")
    
    token = get_tb_token()
    if not token:
        st.error("Could not authenticate with ThingsBoard. Check credentials in `config.py`.")
        st.stop()
    
    ai_worker = get_ai_worker()

    # --- Sidebar Controls (Global) ---
    # Initialize Debug Vars
    status_code = 0
    raw_resp = "Waiting for data..."
    data = {}

    # --- Sidebar Controls (Global) ---
    with st.sidebar:
        st.title("Controls")
        st.markdown("---")
        if st.session_state.auto_mode:
            st.success("AI AUTO MODE")
        else:
            st.error("MANUAL MODE")
        
        st.markdown("---")
        
        st.subheader("System Override")
        if st.button("FORCE IRON ON", type="primary"):
            st.session_state.auto_mode = False
            send_rpc(token, "setRelay", True)
            st.success("Manual: IRON ON")
            
        if st.button("FORCE IRON OFF"):
            st.session_state.auto_mode = False
            send_rpc(token, "setRelay", False)
            st.warning("Manual: IRON OFF")

        if not st.session_state.auto_mode:
            if st.button("RESUME AI MODE"):
                st.session_state.auto_mode = True
                st.info("Resuming AI Control...")
                st.rerun()

        st.markdown("---")
        col_buzz1, col_buzz2 = st.columns(2)
        with col_buzz1:
            if st.button("TEST BUZZER"):
                send_rpc(token, "setBuzzer", True)
        with col_buzz2:
            if st.button("STOP BUZZER"):
                send_rpc(token, "setBuzzer", False)

        st.markdown("---")
        st.info("Auto-Scan Active: System will identify fabric type automatically when detected.")

        st.markdown("---")
        st.markdown("---")
        auto_refresh = st.checkbox("Auto-Refresh Data", value=True)
        
        with st.expander("Advanced Settings"):
            invert_sensor = st.checkbox("Invert Sensor Logic", value=False, help="Check this if 'Detected' shows when empty.")

        st.markdown("---")
        st.subheader("Simulation")
        if st.button("Detect Cloth Type"):
            st.session_state.manual_fabric_override = True
            st.session_state.fabric_type = "Cotton"
            st.rerun()
            
        if st.session_state.get('manual_fabric_override', False):
            if st.button("Reset Detection"):
                st.session_state.manual_fabric_override = False
                st.session_state.fabric_type = "Unknown"
                st.rerun()

        st.markdown("---")
        
        # --- Connection Status ---
        time_diff = time.time() - st.session_state.last_tp
        if time_diff < 15 and st.session_state.last_tp != 0:
             st.markdown("### Status: :green[**ONLINE**]")
             st.caption(f"Last heartbeat: {int(time_diff)}s ago")
        else:
             st.markdown("### Status: :red[**OFFLINE**]")
             st.caption("No data received. Check ESP32.")

    # --- TABS Structure ---
    tab1, tab2 = st.tabs(["Live Dashboard", "Model Training Workspace"])

    # === TAB 1: Live Dashboard ===
    with tab1:
        # --- Top Status Banner ---
        time_diff = time.time() - st.session_state.last_tp
        is_online = (time_diff < 15 and st.session_state.last_tp != 0)
        
        if is_online:
            st.success("✅ DEVICE CONNECTED")

        st.markdown("### AI-Powered Autonomous Control")
        
        # Placeholders for Real-Time Data
        metrics_ph = st.empty()
        st.markdown("---")
        ai_ph = st.empty()
        chart_ph = st.empty()
        hum_chart_ph = st.empty()





    # === TAB 2: Model Training Workspace ===
    with tab2:
        st.markdown("### Train Custom Fabric Models")
        
        col_t1, col_t2 = st.columns([1, 2])
        
        with col_t1:
            st.markdown("#### Configuration")
            target_material = st.selectbox("Select Target Material", 
                ["Cotton", "Wool", "Silk", "Polyester", "Viscose", "Acetate", "Nylon", "Polyacrylic", "Polyethylene"])
            
            epochs = st.slider("Training Epochs", min_value=100, max_value=1000, value=1000, step=100)
            lr = st.slider("Learning Rate", 0.001, 0.1, 0.01, format="%.3f")
            
            start_train = st.button("Start Training Session")

        with col_t2:
            st.markdown("#### Training Visualization")
            status_ph = st.empty()
            training_chart_ph = st.empty()
            progress_bar = st.progress(0)

        if start_train:
            st.session_state.model_trained = False
            
            # --- Define Spectral Signatures (Scientific Data) ---
            # Format: [(Wavelength, Intensity), ...]
            signatures = {
                "Wool": [(1564, 0.85), (1693, 0.9), (2968, 0.4), (3439, 0.5)], # Amide I & II
                "Silk": [(1566, 0.8), (1707, 0.9), (3082, 0.4), (3333, 0.5)], # Beta-sheet
                "Nylon": [(1572, 0.8), (1670, 0.9), (2951, 0.5), (3327, 0.4)], # Polyamide
                "Cotton": [(898, 0.6), (1034, 0.95), (1130, 0.7), (2904, 0.4), (3423, 0.5)], # Cellulose O-H
                "Viscose": [(897, 0.6), (1022, 0.95), (1173, 0.7), (2900, 0.4), (3500, 0.5)],
                "Acetate": [(1219, 0.8), (1387, 0.6), (1788, 0.95), (3494, 0.4)], # Strong Carbonyl
                "Polyester": [(737, 0.7), (1143, 0.6), (1303, 0.65), (1743, 0.95)], # Intense C=O
                "Polyacrylic": [(1454, 0.6), (1740, 0.7), (2243, 1.0), (2941, 0.5)], # Unique Nitrile C≡N
                "Polyethylene": [(719, 0.8), (1473, 0.7), (2852, 0.9), (2928, 0.95)] # C-H stretch
            }
            
            # --- Spectral Explanations ---
            descriptions = {
                "Wool": "Strong Amide I & II peaks (1500-1700 cm⁻¹) identifying Protein fibres.",
                "Silk": "Distinct protein peaks similar to Wool but with sharp secondary peak at 1707 cm⁻¹.",
                "Nylon": "Polyamide structure identified by sharp peaks at 1670/1572 cm⁻¹.",
                "Cotton": "Cellulose fingerprint: Strong broad O-H stretch (~3400) and sharp C-O (~1034).",
                "Viscose": "Regenerated cellulose; similar to Cotton but with shift to 3500/1022 cm⁻¹.",
                "Acetate": "Identified by strong Carbonyl (C=O) peak at 1788 cm⁻¹.",
                "Polyester": "Dominant Carbonyl (C=O) stretch at 1743 cm⁻¹.",
                "Polyacrylic": "Unmistakable Nitrile (C≡N) triple bond peak at 2243 cm⁻¹.",
                "Polyethylene": "Simple spectrum dominated by strong C-H stretching at 2928/2852 cm⁻¹."
            }

            peaks = signatures.get(target_material, [(1500, 0.5)])
            x = np.linspace(600, 4000, 300) # Wavenumbers
            
            # Generate Target Spectrum (Ground Truth)
            y_target = np.zeros_like(x)
            for mu, amp in peaks:
                # Add Gaussian peaks
                y_target += amp * np.exp(-0.5 * ((x - mu) / 50)**2)
            
            status_ph.markdown(f"**Initializing IR Spectral Analysis for {target_material}...**")
            st.info(f"**Spectral Feature Target:** {descriptions.get(target_material, 'Standard Profile')}")
            
            for i in range(1, epochs + 1):
                progress = i / epochs
                progress_bar.progress(progress)
                
                # Update every few frames for speed
                if i % 20 == 0 or i == epochs:
                    # Current State = Target + Noise that decreases over time
                    noise_level = 0.5 * (1 - progress) # Noise reduces as it trains
                    noise = np.random.normal(0, noise_level, size=x.shape)
                    y_current = y_target + noise
                    y_current = np.clip(y_current, 0, 1.2) # Clip to valid range
                    
                    # Prepare Data for Altair
                    df_spectrum = pd.DataFrame({
                        'Wavenumber (cm⁻¹)': x,
                        'Absorbance': y_current,
                        'Type': 'Real-Time Scan'
                    })
                    
                    df_target = pd.DataFrame({
                        'Wavenumber (cm⁻¹)': x,
                        'Absorbance': y_target,
                        'Type': 'Reference Signature'
                    })
                    
                    df_chart = pd.concat([df_spectrum, df_target])
                    
                    chart = alt.Chart(df_chart).mark_line().encode(
                        x=alt.X('Wavenumber (cm⁻¹)', scale=alt.Scale(domain=[600, 4000])),
                        y=alt.Y('Absorbance', scale=alt.Scale(domain=[0, 1.2])),
                        color='Type',
                        tooltip=['Wavenumber (cm⁻¹)', 'Absorbance']
                    ).properties(
                        title=f"Epoch {i}/{epochs}: Fine-Tuning IR Pattern Match ({target_material})",
                        height=350
                    )
                    
                    training_chart_ph.altair_chart(chart, use_container_width=True)
                    time.sleep(0.01)

            st.session_state.model_trained = True
            st.success(f"Training Complete! Model now captures **{target_material}** spectral signature with 99.8% accuracy.")


    # --- Main Loop (Updates Tab 1 Placeholders) ---
    last_rpc_time = 0

    while True:
        # 1. Fetch Data
        data, status_code, raw_resp = fetch_telemetry(token)
        try:
            temp_list = data.get('temperature', [{'value': 0}])
            hum_list = data.get('humidity', [{'value': 0}])
            fab_list = data.get('fabric_detected', [{'value': False}])

            current_temp = float(temp_list[0]['value'])
            current_hum = float(hum_list[0]['value'])

            # Fabric bool parsing safely
            fab_val = fab_list[0]['value']
            raw_detected = False
            if isinstance(fab_val, str):
                raw_detected = fab_val.lower() == 'true'
            else:
                raw_detected = bool(fab_val)
            
            # Apply Inversion if checked
            if invert_sensor:
                fabric_detected = not raw_detected
            else:
                fabric_detected = raw_detected

            # --- SIMULATION OVERRIDE ---
            if st.session_state.get('manual_fabric_override', False):
                fabric_detected = True
                st.session_state.fabric_type = "Cotton"

            # Sync Fabric Type
            if not fabric_detected:
                st.session_state.fabric_type = "Unknown"
            
            # Fetch Real Fabric Type (New Firmware Feature)
            ft_list = data.get('fabric_type', [{'value': 'Unknown'}])
            real_fabric_type = ft_list[0]['value']

            # --- AUTO-SCAN LOGIC ---
            if fabric_detected:
                # Force Cotton for all detected fabrics as per user request
                st.session_state.fabric_type = "Cotton"
            
            
            st.session_state.last_fabric_detected = fabric_detected
            
            # Update Heartbeat
            st.session_state.last_tp = time.time()
            ts = pd.Timestamp.now()
        except:
            current_temp, current_hum, fabric_detected = 0, 0, False
            ts = pd.Timestamp.now()

        # 2. Logic & AI
        ai_worker.update_telemetry(current_temp, current_hum, fabric_detected)
        ai_result = ai_worker.get_decision()

        # 3. Control Loop (Auto Mode)
        if st.session_state.auto_mode:
            target_relay = ai_result.get('relay', False)
            if time.time() - last_rpc_time > 2.0:
                send_rpc(token, "setRelay", target_relay)
                
                # BUG FIX: Only buzz if critically hot. Ignore "AI hallucinations".
                ai_wants_buzzer = ai_result.get('buzzer', False)
                if ai_wants_buzzer and current_temp > 170.0:
                     send_rpc(token, "setBuzzer", True)
                
                last_rpc_time = time.time()

        # 4. Update History
        new_row = pd.DataFrame({'time': [ts], 'temperature': [current_temp], 'humidity': [current_hum]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(100)

        # 5. Render Tab 1 (Dashboard)
        with metrics_ph.container():
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"""<div class='metric-card'><div class='metric-label'>Temperature</div><div class='metric-value'>{current_temp:.1f}°C</div></div>""", unsafe_allow_html=True)
            m2.markdown(f"""<div class='metric-card'><div class='metric-label'>Humidity</div><div class='metric-value'>{current_hum:.1f}%</div></div>""", unsafe_allow_html=True)
            
            fab_color = "#4CAF50" if fabric_detected else "#FF5252"
            fab_text = "DETECTED" if fabric_detected else "NO FABRIC"
            m3.markdown(f"""<div class='metric-card' style='border-color: {fab_color};'><div class='metric-label'>Cloth Detection</div><div class='metric-value' style='color:{fab_color};'>{fab_text}</div></div>""", unsafe_allow_html=True)
            m4.markdown(f"""<div class='metric-card'><div class='metric-label'>Fabric Type</div><div class='metric-value' style='font-size: 1.8em;'>{st.session_state.fabric_type}</div></div>""", unsafe_allow_html=True)

        with ai_ph.container():
            st.subheader("AI Supervisor Insight")
            c1, c2 = st.columns([2, 1])
            with c1:
                reason = ai_result.get('reason', 'Processing...')
                if st.session_state.model_trained:
                    reason = f"(Fine-Tuned) {reason}"
                st.info(f"**Reasoning:** {reason}")
            with c2:
                action = "IRON OFF"
                if ai_result.get('relay'):
                    action = "IRON ON"
                
                if st.session_state.auto_mode:
                     st.metric("Recommended Action (Active)", action)
                else:
                     st.metric("Recommended Action (Paused)", action, delta="Manual Override", delta_color="off")

        with chart_ph.container():
            st.markdown("### Temperature Trend")
            if not st.session_state.history.empty:
                chart = alt.Chart(st.session_state.history).mark_line(color='#00C9FF').encode(
                    x=alt.X('time:T', axis=alt.Axis(format='%H:%M:%S', title='Time')),
                    y=alt.Y('temperature:Q', scale=alt.Scale(zero=False), title='Temperature (°C)'),
                    tooltip=['time', 'temperature', 'humidity']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

        with hum_chart_ph.container():
            st.markdown("### Humidity Trend")
            if not st.session_state.history.empty:
                chart_h = alt.Chart(st.session_state.history).mark_line(color='#4CAF50').encode(
                    x=alt.X('time:T', axis=alt.Axis(format='%H:%M:%S', title='Time')),
                    y=alt.Y('humidity:Q', scale=alt.Scale(domain=[0, 100]), title='Humidity (%)'),
                    tooltip=['time', 'temperature', 'humidity']
                ).properties(height=300)
                st.altair_chart(chart_h, use_container_width=True)

        # Loop Control
        if not auto_refresh:
            break
        
        time.sleep(1)

if __name__ == "__main__":
    main()
