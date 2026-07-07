"""専門家パネルの会議（初回意見 → 討議 → 統合提案）を進行するモジュール。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from .coordinator import Coordinator
from .expert import Expert


@dataclass
class MeetingResult:
    case: str
    opinions: dict[str, str] = field(default_factory=dict)
    discussion: dict[str, str] = field(default_factory=dict)
    proposal: str = ""


class PanelMeeting:
    """専門家AI群とAI秘書による会議を1案件分オーケストレーションする。"""

    def __init__(self, experts: list[Expert], coordinator: Coordinator, rounds: int = 1):
        self._experts = experts
        self._coordinator = coordinator
        self._rounds = rounds

    def run(self, case: str) -> MeetingResult:
        result = MeetingResult(case=case)

        # 1. 初回意見（並行して問い合わせる。専門家同士はまだお互いの
        #    意見を見ていない）
        with ThreadPoolExecutor(max_workers=len(self._experts) or 1) as pool:
            futures = {
                expert.name: pool.submit(expert.opinion, case) for expert in self._experts
            }
            result.opinions = {name: future.result() for name, future in futures.items()}

        # 2. 討議ラウンド（他の専門家の初回意見を踏まえてコメントする）
        discussion = dict(result.opinions)
        for _ in range(self._rounds):
            with ThreadPoolExecutor(max_workers=len(self._experts) or 1) as pool:
                futures = {
                    expert.name: pool.submit(
                        expert.discuss,
                        case,
                        {name: op for name, op in discussion.items() if name != expert.name},
                    )
                    for expert in self._experts
                }
                discussion = {name: future.result() for name, future in futures.items()}
        result.discussion = discussion

        # 3. AI秘書による統合提案
        result.proposal = self._coordinator.synthesize(
            case=case, opinions=result.opinions, discussion=result.discussion
        )
        return result

    def continue_with_feedback(self, previous: MeetingResult, feedback: str) -> MeetingResult:
        """ユーザーのフィードバックを踏まえて、次の論点で会議をやり直す。"""
        next_case = self._coordinator.reframe_feedback(
            case=previous.case, previous_proposal=previous.proposal, feedback=feedback
        )
        return self.run(next_case)
