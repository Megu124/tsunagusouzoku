"""専門家AI 1体を表すクラス。experts.yaml の1エントリに対応する。"""

from __future__ import annotations

from dataclasses import dataclass

import anthropic
import yaml


@dataclass(frozen=True)
class ExpertProfile:
    id: str
    name: str
    role: str
    system_prompt: str


def load_expert_profiles(yaml_path: str) -> list[ExpertProfile]:
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        ExpertProfile(
            id=entry["id"],
            name=entry["name"],
            role=entry["role"],
            system_prompt=entry["system_prompt"].strip(),
        )
        for entry in data["experts"]
    ]


def extract_text(message: anthropic.types.Message) -> str:
    return "".join(block.text for block in message.content if block.type == "text").strip()


class Expert:
    """単一の専門分野に特化したAI。自分の専門領域からの意見のみを述べる。"""

    def __init__(self, profile: ExpertProfile, client: anthropic.Anthropic, model: str):
        self.profile = profile
        self._client = client
        self._model = model

    @property
    def name(self) -> str:
        return self.profile.name

    def opinion(self, case: str) -> str:
        """案件に対する初回意見（他の専門家の意見は見ていない状態）。"""
        message = self._client.messages.create(
            model=self._model,
            max_tokens=700,
            system=self.profile.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"相談内容:\n{case}\n\n"
                        "この内容について、あなたの専門的な立場から意見を述べてください。"
                    ),
                }
            ],
        )
        return extract_text(message)

    def discuss(self, case: str, other_opinions: dict[str, str]) -> str:
        """他の専門家の初回意見を踏まえた討議コメント。"""
        others_text = "\n\n".join(
            f"◆{name}の意見:\n{opinion}" for name, opinion in other_opinions.items()
        )
        prompt = (
            f"相談内容:\n{case}\n\n"
            f"他の専門家の初回意見は以下の通りです。\n\n{others_text}\n\n"
            "これらを踏まえて、あなたの専門分野の立場から、賛同する点・懸念点・"
            "追加で検討すべき論点を簡潔にコメントしてください。"
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=700,
            system=self.profile.system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        return extract_text(message)
