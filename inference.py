import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline-rule-agent")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy_token")
SEED = int(os.getenv("SEED", "42"))


def choose_action(state: dict) -> float:
    soil = state["soil_moisture"]
    rain = state["rain_forecast"]
    water_left = state["water_available"]
    stage = state["crop_stage"]

    if rain == 1:
        if soil < 45:
            return min(3.0, water_left)
        return 0.0

    if stage == "early":
        if soil < 45:
            return min(6.0, water_left)
        elif soil < 52:
            return min(3.0, water_left)
        return 0.0

    if stage == "mid":
        if soil < 45:
            return min(7.0, water_left)
        elif soil < 52:
            return min(4.0, water_left)
        return 0.0

    if soil < 48:
        return min(5.0, water_left)

    return 0.0


def run_episode(difficulty: str):
    reset_res = requests.post(
        f"{API_BASE_URL}/reset",
        params={"difficulty": difficulty, "seed": SEED},
        timeout=30
    )
    reset_res.raise_for_status()
    state = reset_res.json()["state"]

    while not state["done"]:
        action = {"water_amount": choose_action(state)}
        step_res = requests.post(f"{API_BASE_URL}/step", json=action, timeout=30)
        step_res.raise_for_status()
        state = step_res.json()["state"]

    eval_res = requests.get(f"{API_BASE_URL}/evaluate", timeout=30)
    eval_res.raise_for_status()
    return eval_res.json()


if __name__ == "__main__":
    print("Baseline Inference Results")
    print(f"API_BASE_URL={API_BASE_URL}")
    print(f"MODEL_NAME={MODEL_NAME}")
    print(f"SEED={SEED}")
    print("-" * 50)

    for difficulty in ["easy", "medium", "hard"]:
        result = run_episode(difficulty)
        print(result)