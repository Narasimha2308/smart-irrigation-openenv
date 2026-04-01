from pydantic import BaseModel, Field
from typing import Literal, Dict


class IrrigationState(BaseModel):
    day: int
    soil_moisture: float = Field(..., ge=0, le=100)
    rain_forecast: int = Field(..., ge=0, le=1)
    crop_stage: Literal["early", "mid", "late"]
    water_available: float = Field(..., ge=0)
    crop_health: float = Field(..., ge=0, le=100)
    done: bool
    difficulty: Literal["easy", "medium", "hard"]


class IrrigationAction(BaseModel):
    water_amount: float = Field(..., ge=0, le=10)


class StepResponse(BaseModel):
    state: IrrigationState
    reward: float
    done: bool
    message: str


class TaskInfo(BaseModel):
    difficulty: Literal["easy", "medium", "hard"]
    description: str
    max_days: int
    max_water_budget: float
    target_moisture_min: float
    target_moisture_max: float


class GradeBreakdown(BaseModel):
    stability_score: float
    efficiency_score: float
    health_score: float
    final_score: float


class EvaluationResponse(BaseModel):
    difficulty: Literal["easy", "medium", "hard"]
    total_reward: float
    final_crop_health: float
    water_left: float
    days_completed: int
    grade: GradeBreakdown
    metadata: Dict[str, str]