import random
from app.models import IrrigationState, TaskInfo


class SmartIrrigationEnv:
    TASK_CONFIGS = {
        "easy": {
            "description": "Maintain healthy soil moisture in stable no-rain conditions.",
            "max_days": 7,
            "max_water_budget": 50.0,
            "target_moisture_min": 50.0,
            "target_moisture_max": 70.0,
        },
        "medium": {
            "description": "Handle random rain while maintaining irrigation efficiency.",
            "max_days": 7,
            "max_water_budget": 45.0,
            "target_moisture_min": 50.0,
            "target_moisture_max": 70.0,
        },
        "hard": {
            "description": "Optimize crop health with limited water and changing crop stages.",
            "max_days": 7,
            "max_water_budget": 35.0,
            "target_moisture_min": 50.0,
            "target_moisture_max": 70.0,
        },
    }

    def __init__(self, difficulty: str = "easy", seed: int = 42):
        self.difficulty = difficulty
        self.seed = seed
        self.rng = random.Random(seed)

        config = self.TASK_CONFIGS[difficulty]
        self.max_days = config["max_days"]
        self.max_water_budget = config["max_water_budget"]
        self.target_moisture_min = config["target_moisture_min"]
        self.target_moisture_max = config["target_moisture_max"]

        self.day = 1
        self.soil_moisture = 50.0
        self.rain_forecast = 0
        self.crop_stage = "early"
        self.water_available = self.max_water_budget
        self.crop_health = 100.0
        self.done = False

        self.moisture_history = []
        self.total_reward = 0.0

    def reset(self):
        self.rng = random.Random(self.seed)
        self.day = 1
        self.done = False
        self.crop_health = 100.0
        self.water_available = self.max_water_budget
        self.total_reward = 0.0
        self.moisture_history = []

        if self.difficulty == "easy":
            self.soil_moisture = 50.0
            self.rain_forecast = 0
            self.crop_stage = "early"

        elif self.difficulty == "medium":
            self.soil_moisture = self.rng.uniform(35, 60)
            self.rain_forecast = self.rng.choice([0, 1])
            self.crop_stage = "mid"

        elif self.difficulty == "hard":
            self.soil_moisture = self.rng.uniform(30, 65)
            self.rain_forecast = self.rng.choice([0, 1])
            self.crop_stage = self.rng.choice(["early", "mid", "late"])

        self.moisture_history.append(self.soil_moisture)
        return self.state()

    def state(self):
        return IrrigationState(
            day=self.day,
            soil_moisture=round(self.soil_moisture, 2),
            rain_forecast=self.rain_forecast,
            crop_stage=self.crop_stage,
            water_available=round(self.water_available, 2),
            crop_health=round(self.crop_health, 2),
            done=self.done,
            difficulty=self.difficulty,
        )

    def get_task_info(self):
        config = self.TASK_CONFIGS[self.difficulty]
        return TaskInfo(
            difficulty=self.difficulty,
            description=config["description"],
            max_days=config["max_days"],
            max_water_budget=config["max_water_budget"],
            target_moisture_min=config["target_moisture_min"],
            target_moisture_max=config["target_moisture_max"],
        )

    def _update_crop_stage(self):
        if self.day <= 2:
            self.crop_stage = "early"
        elif self.day <= 5:
            self.crop_stage = "mid"
        else:
            self.crop_stage = "late"

    def _get_rain_amount(self):
        if self.rain_forecast == 1:
            if self.difficulty == "medium":
                return self.rng.uniform(5, 10)
            if self.difficulty == "hard":
                return self.rng.uniform(4, 12)
        return 0.0

    def _get_evaporation(self):
        if self.crop_stage == "early":
            return self.rng.uniform(4, 6)
        elif self.crop_stage == "mid":
            return self.rng.uniform(5, 7)
        return self.rng.uniform(6, 8)

    def _calculate_reward(self, water_amount: float):
        reward = 0.0

        if self.target_moisture_min <= self.soil_moisture <= self.target_moisture_max:
            reward += 1.0
        elif 40 <= self.soil_moisture < self.target_moisture_min or self.target_moisture_max < self.soil_moisture <= 80:
            reward += 0.4
        else:
            reward -= 0.6

        if water_amount > 8:
            reward -= 0.25

        if self.soil_moisture < 25:
            self.crop_health -= 10
            reward -= 0.5
        elif self.soil_moisture > 85:
            self.crop_health -= 8
            reward -= 0.5
        else:
            self.crop_health = min(100, self.crop_health + 0.5)

        return round(reward, 3)

    def step(self, water_amount: float):
        if self.done:
            return self.state(), 0.0, True, "Environment already finished."

        water_amount = max(0.0, min(water_amount, 10.0))
        water_amount = min(water_amount, self.water_available)

        self.water_available -= water_amount

        rain_amount = self._get_rain_amount()
        evaporation = self._get_evaporation()

        self.soil_moisture += water_amount + rain_amount
        self.soil_moisture -= evaporation
        self.soil_moisture = max(0.0, min(100.0, self.soil_moisture))

        reward = self._calculate_reward(water_amount)
        self.total_reward += reward
        self.moisture_history.append(self.soil_moisture)

        self.day += 1
        self._update_crop_stage()

        if self.difficulty in ["medium", "hard"]:
            self.rain_forecast = self.rng.choice([0, 1])
        else:
            self.rain_forecast = 0

        if self.day > self.max_days:
            self.done = True

        return self.state(), reward, self.done, "Step completed."

    def average_moisture_deviation(self):
        target_mid = (self.target_moisture_min + self.target_moisture_max) / 2
        if not self.moisture_history:
            return 100.0
        deviations = [abs(x - target_mid) for x in self.moisture_history]
        return sum(deviations) / len(deviations)

    def water_left_ratio(self):
        if self.max_water_budget == 0:
            return 0.0
        return self.water_available / self.max_water_budget