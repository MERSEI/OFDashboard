# core/ai.py
from typing import List, Dict, Any


def ai_warmup_suggestion(history: List[Dict[str, Any]], fan_name: str) -> str:
    # TODO: заменить на реальный вызов LLM/другой модели
    last_user_msgs = [m for m in history if m["role"] == "user"]
    last = last_user_msgs[-1]["text"] if last_user_msgs else ""
    return (
        f"Продолжи тему: \"{last}\" и мягко подведи к платному контенту "
        f"(кастом видео, фото-сет). Обращайся по имени: {fan_name}."
    )


def estimate_generation_cost(tokens: int, price_per_1k: float = 0.002) -> float:
    return tokens / 1000 * price_per_1k


def fake_generate_images(prompt: str, model_name: str, lora_id: str, n: int = 4):
    return [f"https://via.placeholder.com/400x600/FF69B4/FFFFFF?text={i+1}" for i in range(n)]


def fake_generate_videos(prompt: str, model_name: str, lora_id: str, n: int = 2):
    return [f"https://example.com/fake_video_{i+1}.mp4" for i in range(n)]
