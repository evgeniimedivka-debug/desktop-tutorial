"""Оркестратор контент-завода Milis Cosmo.

Использование:
    python run_pipeline.py --once     # сгенерировать 1 ролик, отправить на утверждение,
                                       # дождаться решения (до 1 часа) и опубликовать при "да"
"""
import argparse
import os
import sys

import yaml

from pipeline import (
    avatar_video,
    hosting,
    instagram_publish,
    script_generator,
    telegram_approval,
    tracker,
)


def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        sys.exit(
            f"Не найден {path}. Скопируйте config.example.yaml -> config.yaml и заполните ключи."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_once(config: dict) -> None:
    bank_path = config["paths"]["content_bank"]
    bank = script_generator.load_content_bank(bank_path)

    idea = script_generator.pick_next_idea(bank)
    if idea is None:
        print("Банк идей пуст — добавьте новые темы в content_bank.yaml")
        return

    print(f"Тема: {idea['topic']} ({idea['product']})")
    script = script_generator.generate_script(config, idea, bank)
    print("Сценарий сгенерирован.")

    os.makedirs(config["paths"]["output_dir"], exist_ok=True)
    local_video = avatar_video.generate_avatar_video(
        config, script, config["paths"]["output_dir"]
    )
    print(f"Видео сгенерировано: {local_video}")

    public_url = hosting.upload_public(config, local_video)
    print(f"Публичная ссылка: {public_url}")

    tracker.log_result(
        config["paths"]["tracker_xlsx"],
        product=idea["product"],
        rubric_name=script["rubric"]["name"],
        status="Готово (на утверждении)",
        link=public_url,
    )

    message_id = telegram_approval.send_for_approval(config, local_video, script)
    print("Отправлено на утверждение в Telegram, жду решения...")

    decision = telegram_approval.wait_for_decision(config, message_id)

    if decision == "approve":
        media_id = instagram_publish.publish_reel(config, public_url, script["caption"])
        print(f"Опубликовано в Instagram: media_id={media_id}")
        tracker.log_result(
            config["paths"]["tracker_xlsx"],
            product=idea["product"],
            rubric_name=script["rubric"]["name"],
            status="Опубликовано",
            link=public_url,
        )
        script_generator.mark_idea_used(bank, bank_path, idea)
    else:
        print("Отклонено или не подтверждено вовремя — публикация отменена.")
        tracker.log_result(
            config["paths"]["tracker_xlsx"],
            product=idea["product"],
            rubric_name=script["rubric"]["name"],
            status="Отклонено",
            link=public_url,
            comment="Отклонено при ручном утверждении",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Сгенерировать и обработать один ролик")
    args = parser.parse_args()

    config = load_config()

    if args.once:
        run_once(config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
