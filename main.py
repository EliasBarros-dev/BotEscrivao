import argparse

from bot.app import run_bot, run_dry_run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bot Discord com menu inicial.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida a estrutura basica sem conectar ao Discord.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run:
        print(run_dry_run())
        return

    run_bot()


if __name__ == "__main__":
    main()
