import time
import requests
import json
from ai_engine import get_ai_decision

from config import TB_URL, USERNAME, PASSWORD, DEVICE_ID

# --- Auth ---
def get_token():
    url = f"{TB_URL}/api/auth/login"
    try:
        response = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        return response.json()["token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def main():
    print("Starting Smart Iron AI Agent...")
    token = get_token()
    if not token:
        return

    headers = {"X-Authorization": f"Bearer {token}"}
    
    while True:
        try:
            # 1. Get Latest Telemetry
            # API: /api/plugins/telemetry/{entityType}/{entityId}/values/timeseries
            url = f"{TB_URL}/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries?keys=temperature,humidity,fabric_detected&useStrictDataTypes=true"
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            # Debugging Raw Data
            print(f"Raw Data: {data}") 
            
            def get_val(key, default=0):
                series = data.get(key, [])
                if not series:
                    return default
                val = series[0].get('value')
                if val is None:
                    return default
                return float(val)

            def get_bool(key, default=False):
                series = data.get(key, [])
                if not series:
                    return default
                val = series[0].get('value')
                if val is None:
                    return default
                return str(val).lower() == 'true'

            temp = get_val('temperature', 0)
            hum = get_val('humidity', 0)
            fabric = get_bool('fabric_detected', False)
            
            print(f"Received: Temp={temp}, Hum={hum}, Fabric={fabric}")
            
            # 2. Ask AI
            decision = get_ai_decision(temp, hum, fabric)
            print(f"AI Decision: {decision}")
            
            # 3. Send Command via RPC
            # Try standard device endpoint first
            rpc_url = f"{TB_URL}/api/plugins/rpc/oneway/{DEVICE_ID}"
            try:
                cmd_relay = {"method": "setRelay", "params": decision['relay']}
                rpc_resp = requests.post(rpc_url, headers=headers, json=cmd_relay)
                if rpc_resp.status_code != 200:
                    print(f"RPC Failed: {rpc_resp.status_code} - {rpc_resp.text}")
                else:
                    print("RPC Relay Sent OK")
                    
                if decision['buzzer']:
                    cmd_buzzer = {"method": "setBuzzer", "params": True}
                    requests.post(rpc_url, headers=headers, json=cmd_buzzer)
            except Exception as e:
                print(f"RPC Error: {e}")

            time.sleep(2) # Decision Loop Interval
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error (Main Loop): {e}")
            if e.response.status_code == 401:
                print("Token expired, refreshing...")
                token = get_token()
                headers = {"X-Authorization": f"Bearer {token}"}
            else:
                time.sleep(5)
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
