"""AI秘書（Coordinator）。専門家パネルのリーダー役。

個々の専門知識には立ち入らず、全体像の把握・論点整理・最終提案の作成・
ユーザーとの窓口に専念する。
"""

from __future__ import annotations

import anthropic

from .expert import ExpertProfile, extract_text

SECRETARY_SYSTEM_PROMPT = """\
あなたは専門家パネルを取りまとめるAI秘書です。あなた自身は特定分野の
専門知識を持たず、以下の役割に専念してください。

- 専門家たちの意見を俯瞰し、全体像を把握すること
- 意見が一致している点と、意見が割れている論点を明確に区別すること
- 意見が割れている場合は、対立点をユーザーに分かりやすく提示すること
- 専門家全体の意見を踏まえた「秘書としての推奨方針」を1つ示すこと
  （ただし専門家の判断を上書きする断定はせず、あくまで整理・推奨に留める）
- 専門用語はできるだけユーザー向けに噛み砕くこと
- 出力は「合意点」「論点・対立点」「秘書としての推奨方針」「ユーザーへの
  確認事項」の4セクション構成でまとめること
"""


class Coordinator:
    def __init__(self, client: anthropic.Anthropic, model: str):
        self._client = client
        self._model = model

    def select_relevant_experts(
        self, case: str, experts: list[ExpertProfile]
    ) -> list[ExpertProfile]:
        """案件に関連する専門家を選ぶ。現状は全員招集がデフォルト。

        案件によって専門家を絞り込みたい場合は、ここをLLM呼び出しに
        差し替える（例: 案件文とexpertsの一覧をLLMに渡し、関連するidの
        リストを返させる）。
        """
        return experts

    def synthesize(
        self,
        case: str,
        opinions: dict[str, str],
        discussion: dict[str, str],
    ) -> str:
        """初回意見＋討議コメントを統合し、ユーザー向けの提案文を作る。"""
        opinions_text = "\n\n".join(
            f"◆{name}の初回意見:\n{text}" for name, text in opinions.items()
        )
        discussion_text = "\n\n".join(
            f"◆{name}の討議コメント:\n{text}" for name, text in discussion.items()
        )
        prompt = (
            f"相談内容:\n{case}\n\n"
            f"【専門家の初回意見】\n{opinions_text}\n\n"
            f"【討議ラウンドでのコメント】\n{discussion_text}\n\n"
            "以上を踏まえて、指定のフォーマット（合意点／論点・対立点／"
            "秘書としての推奨方針／ユーザーへの確認事項）でまとめてください。"
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1200,
            system=SECRETARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return extract_text(message)

    def reframe_feedback(self, case: str, previous_proposal: str, feedback: str) -> str:
        """ユーザーのフィードバック・追加指示を、専門家パネルへの
        次の論点として再展開する。
        """
        prompt = (
            f"元の相談内容:\n{case}\n\n"
            f"あなたが前回まとめた提案:\n{previous_proposal}\n\n"
            f"ユーザーからのフィードバック・追加指示:\n{feedback}\n\n"
            "この内容を踏まえて、専門家パネルに再検討してもらうための"
            "論点を、次の会議のインプットとして簡潔に整理してください。"
        )
        message = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            system=SECRETARY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return extract_text(message)
