"""対話式CLIエントリポイント。

使い方:
    python -m src.cli
"""

from __future__ import annotations

import os
import sys

import anthropic
from dotenv import load_dotenv

from .coordinator import Coordinator
from .expert import Expert, load_expert_profiles
from .panel import MeetingResult, PanelMeeting

EXPERTS_YAML = os.path.join(os.path.dirname(__file__), "..", "experts", "experts.yaml")
DEFAULT_MODEL = "claude-sonnet-5"


def _print_section(title: str) -> None:
    print(f"\n{'=' * 10} {title} {'=' * 10}")


def _print_meeting_result(result: MeetingResult) -> None:
    _print_section("専門家の初回意見")
    for name, opinion in result.opinions.items():
        print(f"\n--- {name} ---\n{opinion}")

    _print_section("討議ラウンド")
    for name, comment in result.discussion.items():
        print(f"\n--- {name} ---\n{comment}")

    _print_section("AI秘書からの提案")
    print(f"\n{result.proposal}")


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: 環境変数 ANTHROPIC_API_KEY が設定されていません。", file=sys.stderr)
        print(".env.example を参考に .env を作成してください。", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
    client = anthropic.Anthropic(api_key=api_key)

    profiles = load_expert_profiles(EXPERTS_YAML)
    coordinator = Coordinator(client=client, model=model)
    relevant_profiles = profiles  # 案件による絞り込みは coordinator 側で拡張可能

    experts = [Expert(profile, client=client, model=model) for profile in relevant_profiles]
    panel = PanelMeeting(experts=experts, coordinator=coordinator)

    print("相談内容を入力してください（複数行可。入力を終えたら空行でEnter）:")
    lines: list[str] = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    case = "\n".join(lines).strip()
    if not case:
        print("相談内容が空のため終了します。")
        return

    result = panel.run(case)
    _print_meeting_result(result)

    while True:
        print("\nフィードバック・追加指示があれば入力してください（何もせずEnterで終了）:")
        feedback = input("> ").strip()
        if not feedback:
            print("終了します。")
            break
        result = panel.continue_with_feedback(result, feedback)
        _print_meeting_result(result)


if __name__ == "__main__":
    main()
