def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def grade_run(
    avg_moisture_deviation: float,
    final_crop_health: float,
    water_left_ratio: float
):
    """
    Returns scores in 0.0 to 1.0 range.
    Lower moisture deviation is better.
    Higher crop health is better.
    Higher water_left_ratio is better.
    """

    stability_score = clamp(1.0 - (avg_moisture_deviation / 30.0))
    health_score = clamp(final_crop_health / 100.0)
    efficiency_score = clamp(water_left_ratio)

    final_score = round(
        0.45 * stability_score +
        0.35 * health_score +
        0.20 * efficiency_score,
        3
    )

    return {
        "stability_score": round(stability_score, 3),
        "efficiency_score": round(efficiency_score, 3),
        "health_score": round(health_score, 3),
        "final_score": final_score,
    }