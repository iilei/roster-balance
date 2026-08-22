"""Decision engine orchestration.

This module must remain independent from SQLAlchemy, FastAPI and AWS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from roster_balance.decision.result import (
    CandidateBoard,
    CandidateRecommendation,
    CandidateRejection,
    ConstraintResult,
    DecisionResult,
    HopResult,
    ScoreContribution,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from roster_balance.decision.context import AssignmentCandidate, DecisionContext


class Constraint(Protocol):
    def evaluate(
        self, candidate: AssignmentCandidate, context: DecisionContext
    ) -> ConstraintResult: ...


class Metric(Protocol):
    def evaluate(
        self, candidate: AssignmentCandidate, context: DecisionContext
    ) -> float: ...


@dataclass(frozen=True, slots=True)
class Hop:
    id: str
    constraints: tuple[tuple[str, Constraint], ...] = ()
    metrics: tuple[tuple[str, Metric, float], ...] = ()


@dataclass(frozen=True, slots=True)
class Policy:
    id: str
    version: int
    hops: tuple[Hop, ...]


class DecisionEngine:
    def evaluate(
        self,
        candidates: Sequence[AssignmentCandidate],
        context: DecisionContext,
        policy: Policy,
    ) -> DecisionResult:
        boards: list[CandidateBoard] = []

        for period in context.periods:
            period_candidates = [
                candidate
                for candidate in candidates
                if candidate.period_id == period.id
            ]
            ranked: list[CandidateRecommendation] = []
            ruled_out: list[CandidateRejection] = []
            for candidate in period_candidates:
                hops: list[HopResult] = []
                rejected_by: list[str] = []
                for policy_hop in policy.hops:
                    for step_id, constraint in policy_hop.constraints:
                        outcome = constraint.evaluate(candidate, context)
                        hops.append(
                            HopResult(
                                step_id=outcome.step_id,
                                kind='constraint',
                                passed=outcome.passed,
                                reason=outcome.reason,
                            )
                        )
                        if outcome.hard and not outcome.passed:
                            rejected_by.append(step_id)
                    if rejected_by:
                        break
                if rejected_by:
                    ruled_out.append(
                        CandidateRejection(
                            member_id=candidate.member_id,
                            rejected_by=tuple(rejected_by),
                            hops=tuple(hops),
                        )
                    )
                    continue

                factors: list[ScoreContribution] = []
                score = 0.0
                for policy_hop in policy.hops:
                    for step_id, metric, weight in policy_hop.metrics:
                        raw_value = metric.evaluate(candidate, context)
                        contribution = raw_value * weight
                        factors.append(
                            ScoreContribution(step_id, raw_value, weight, contribution)
                        )
                        hops.append(
                            HopResult(
                                step_id=step_id,
                                kind='metric',
                                passed=True,
                                reason=f'Checkpoint {policy_hop.id}: metric evaluated',
                                value=raw_value,
                            )
                        )
                        score += contribution
                ranked.append(
                    CandidateRecommendation(
                        member_id=candidate.member_id,
                        score=score,
                        rank=0,
                        factors=tuple(factors),
                        hops=tuple(hops),
                    )
                )

            ranked.sort(key=lambda item: (-item.score, item.member_id))
            ranked = [
                CandidateRecommendation(
                    member_id=item.member_id,
                    score=item.score,
                    rank=rank,
                    factors=item.factors,
                    hops=item.hops,
                )
                for rank, item in enumerate(ranked, start=1)
            ]
            board = CandidateBoard(
                period_id=period.id,
                starts_at=period.starts_at,
                ends_at=period.ends_at,
                duty_role_id=period.duty_role_id,
                ranked=tuple(ranked),
                ruled_out=tuple(ruled_out),
                selected_member_id=ranked[0].member_id if ranked else None,
            )
            boards.append(board)

        return DecisionResult(
            policy_id=policy.id,
            policy_version=policy.version,
            boards=tuple(boards),
        )
