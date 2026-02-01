import ollama
import json

MODEL_NAME = "llama3"

TEACHER_PROMPT = """
You are the Expert AI Supervisor for a Smart Ironing System. 
Your decisions are ground-truth labels for training a TinyML model on the edge device.
Input data: Temperature (C), Humidity (%), Fabric Detected (bool).

Goal: Maintain optimal ironing temperature (120C - 150C) for Cotton/General use when fabric is present. Ensure absolute safety.

Rules:
1. SAFETY FIRST: If Fabric Detected is False, Relay MUST be FALSE. (Prevent fires).
2. OVERHEAT PROTECTION: If Temp > 170C, Relay MUST be FALSE, Buzzer TRUE.
3. IRONING LOGIC (Only if Fabric is True):
    - If Temp < 120C: Relay TRUE (Heat up).
    - If Temp > 150C: Relay FALSE (Cool down).
    - If Temp is 120C-150C: Maintain current state (Hysteresis) or False to save energy.

Output JSON format strictly:
{
    "relay": true/false,
    "buzzer": true/false,
    "reason": "Clear explanation for the decision"
}
"""

def get_ai_decision(temp, humidity, fabric_detected):
    user_msg = f"Data: Temp={temp}, Humidity={humidity}, FabricDetected={fabric_detected}."
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': TEACHER_PROMPT},
            {'role': 'user', 'content': user_msg}
        ])
        
        content = response['message']['content']
        # Extract JSON from potential markdown text
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            return {"relay": False, "buzzer": False, "reason": "Error parsing JSON"}
            
    except Exception as e:
        print(f"AI Error: {e}")
        return {"relay": False, "buzzer": False, "reason": f"AI Exception: {e}"}

if __name__ == "__main__":
    # Test
    print(get_ai_decision(100, 50, True))
