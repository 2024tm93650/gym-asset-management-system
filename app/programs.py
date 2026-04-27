"""Program catalog for ACEest Fitness & Gym.

Ported from the professor's Aceestver-1.0.py / 1.1.py reference designs.
Each program has a workout chart, diet chart, accent color, and
calorie factor (kcal per kg of bodyweight) used by later versions.
"""
from __future__ import annotations

from typing import TypedDict


class Program(TypedDict):
    key: str
    name: str
    workout: str
    diet: str
    color: str
    calorie_factor: int


PROGRAMS: dict[str, Program] = {
    "FL": {
        "key": "FL",
        "name": "Fat Loss (FL)",
        "workout": (
            "Mon: 5x5 Back Squat + AMRAP\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: 10RFT Deadlifts/Box Jumps\n"
            "Fri: 30min Active Recovery"
        ),
        "diet": (
            "B: 3 Egg Whites + Oats Idli\n"
            "L: Grilled Chicken + Brown Rice\n"
            "D: Fish Curry + Millet Roti\n"
            "Target: 2,000 kcal"
        ),
        "color": "#e74c3c",
        "calorie_factor": 22,
    },
    "MG": {
        "key": "MG",
        "name": "Muscle Gain (MG)",
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "B: 4 Eggs + PB Oats\n"
            "L: Chicken Biryani (250g Chicken)\n"
            "D: Mutton Curry + Jeera Rice\n"
            "Target: 3,200 kcal"
        ),
        "color": "#2ecc71",
        "calorie_factor": 35,
    },
    "BG": {
        "key": "BG",
        "name": "Beginner (BG)",
        "workout": (
            "Circuit Training: Air Squats, Ring Rows, Push-ups.\n"
            "Focus: Technique Mastery & Form (90% Threshold)"
        ),
        "diet": (
            "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\n"
            "Protein: 120g/day"
        ),
        "color": "#3498db",
        "calorie_factor": 26,
    },
}


def estimate_calories(weight_kg: float, program_key: str) -> int:
    """Return daily calorie estimate = weight (kg) x program calorie factor."""
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    if program_key not in PROGRAMS:
        raise KeyError(f"unknown program: {program_key}")
    return int(weight_kg * PROGRAMS[program_key]["calorie_factor"])
