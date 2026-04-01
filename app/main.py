from fastapi import FastAPI, Query
from app.env import SmartIrrigationEnv
from app.models import IrrigationAction, StepResponse, EvaluationResponse
from app.graders import grade_run

app = FastAPI(title="Smart Irrigation OpenEnv")

env = SmartIrrigationEnv(difficulty="easy", seed=42)


@app.get("/")
def root():
    return {"message": "Smart Irrigation OpenEnv API is running"}


@app.post("/reset")
def reset(
    difficulty: str = Query(default="easy", enum=["easy", "medium", "hard"]),
    seed: int = Query(default=42)
):
    global env
    env = SmartIrrigationEnv(difficulty=difficulty, seed=seed)
    state = env.reset()
    return {
        "message": "Environment reset successful",
        "difficulty": difficulty,
        "seed": seed,
        "task_info": env.get_task_info().model_dump(),
        "state": state.model_dump(),
    }


@app.get("/state")
def get_state():
    return env.state().model_dump()


@app.post("/step", response_model=StepResponse)
def step(action: IrrigationAction):
    state, reward, done, message = env.step(action.water_amount)
    return StepResponse(
        state=state,
        reward=reward,
        done=done,
        message=message,
    )


@app.get("/evaluate", response_model=EvaluationResponse)
def evaluate():
    grade = grade_run(
        avg_moisture_deviation=env.average_moisture_deviation(),
        final_crop_health=env.crop_health,
        water_left_ratio=env.water_left_ratio(),
    )

    return EvaluationResponse(
        difficulty=env.difficulty,
        total_reward=round(env.total_reward, 3),
        final_crop_health=round(env.crop_health, 2),
        water_left=round(env.water_available, 2),
        days_completed=min(env.day - 1, env.max_days),
        grade=grade,
        metadata={
            "seed": str(env.seed),
            "environment": "Smart Irrigation OpenEnv",
        },
    )