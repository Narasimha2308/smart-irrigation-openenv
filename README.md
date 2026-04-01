---
title: Smart Irrigation OpenEnv
emoji: 🌱
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# Smart Irrigation OpenEnv

Smart Irrigation OpenEnv is a real-world reinforcement learning environment where an agent decides how much water to apply to crops each day.

## Problem Statement
Efficient irrigation is essential in agriculture. Underwatering damages crops, while overwatering wastes water and can also reduce crop health. This environment simulates irrigation decision-making under changing weather, crop stages, and water constraints.

## Objective
The agent must optimize:
- crop health
- soil moisture stability
- water efficiency

## Environment API
- `POST /reset`
- `GET /state`
- `POST /step`
- `GET /evaluate`

## Action Space
```json
{
  "water_amount": 5.0
}