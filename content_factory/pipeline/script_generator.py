"""Тема из банка идей -> сценарий Reels (Claude API)."""
import json

import anthropic
import yaml

PROMPT_TEMPLATE = """Ты пишешь сценарий вертикального Reels-ролика (20-30 секунд) для
бренда косметики {brand}. Персона рассказчика: {persona_name}, тон: {persona_tone}.

Тема: {topic}
Продукт: {product}
Рубрика: {rubric_name} (цель: {rubric_goal})

Верни ТОЛЬКО валидный JSON без markdown-разметки, со полями:
{{
  "hook": "первая фраза, 0-3 сек, должна зацепить с первого слова",
  "body": "основной текст, который проговорит аватар на камеру, разговорный стиль, без канцелярита",
  "cta": "призыв к действию в конце (1 фраза)",
  "caption": "подпись к посту в Instagram, 2-3 предложения + вопрос к аудитории",
  "hashtags": ["до 8 хэштегов на русском и английском, релевантных теме"]
}}

Требования: body должен звучать естественно при озвучке, 60-80 слов, без выдуманных
медицинских утверждений и обещаний гарантированного результата (только "может помочь",
"способствует" — избегать рекламных заявлений, которые нельзя подтвердить)."""


def load_content_bank(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pick_next_idea(bank: dict) -> dict | None:
    for idea in bank["ideas"]:
        if idea["status"] == "not_used":
            return idea
    return None


def mark_idea_used(bank: dict, path: str, idea: dict) -> None:
    idea["status"] = "used"
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(bank, f, allow_unicode=True, sort_keys=False)


def generate_script(config: dict, idea: dict, bank: dict) -> dict:
    client = anthropic.Anthropic(api_key=config["anthropic"]["api_key"])
    rubric = bank["rubrics"][idea["rubric"]]
    persona = bank["avatar_persona"]

    prompt = PROMPT_TEMPLATE.format(
        brand=config["brand"]["name"],
        persona_name=persona["name"],
        persona_tone=persona["tone"],
        topic=idea["topic"],
        product=idea["product"],
        rubric_name=rubric["name"],
        rubric_goal=rubric["goal"],
    )

    response = client.messages.create(
        model=config["anthropic"]["model"],
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    script = json.loads(raw)

    script["caption"] = script["caption"] + config["brand"]["ai_disclosure_suffix"]
    script["idea"] = idea
    script["rubric"] = rubric
    return script
