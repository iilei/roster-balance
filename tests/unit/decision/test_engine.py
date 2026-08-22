from dataclasses import dataclass
from datetime import UTC, datetime

from roster_balance.decision.context import (
    AssignmentCandidate,
    DecisionContext,
    PlanningPeriod,
)
from roster_balance.decision.engine import DecisionEngine, Hop, Policy
from roster_balance.decision.result import ConstraintResult


@dataclass
class Availability:
    def evaluate(
        self, candidate: AssignmentCandidate, _context: DecisionContext
    ) -> ConstraintResult:
        if candidate.member_id == 'bob':
            return ConstraintResult(
                step_id='availability',
                passed=False,
                hard=True,
                reason='Vacation calendar blocks this period',
            )
        return ConstraintResult(
            step_id='availability',
            passed=True,
            hard=True,
            reason='No blocking availability event',
        )


@dataclass
class LoadMetric:
    values: dict[str, float]

    def evaluate(
        self, candidate: AssignmentCandidate, _context: DecisionContext
    ) -> float:
        return self.values[candidate.member_id]


policy = Policy(
    id='test-policy',
    version=1,
    hops=(
        Hop(
            id='constraints',
            constraints=(('availability', Availability()),),
        ),
        Hop(
            id='scoring',
            metrics=(
                ('historical-load', LoadMetric({'alice': 0.2, 'carol': 0.8}), 1.0),
            ),
        ),
    ),
)


def test_engine_returns_ranked_and_ruled_out_candidates() -> None:
    period = PlanningPeriod(
        id='period-1',
        starts_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
        ends_at=datetime(2026, 8, 24, 17, tzinfo=UTC),
        duty_role_id='on-call',
    )
    context = DecisionContext(periods=(period,))
    candidates = (
        AssignmentCandidate('alice', 'period-1'),
        AssignmentCandidate('bob', 'period-1'),
        AssignmentCandidate('carol', 'period-1'),
    )

    result = DecisionEngine().evaluate(candidates, context, policy)

    board = result.boards[0]
    assert [item.member_id for item in board.ranked] == ['carol', 'alice']
    assert [item.member_id for item in board.ruled_out] == ['bob']
    assert board.ruled_out[0].rejected_by == ('availability',)
    assert board.ranked[0].score == 0.8
    assert board.ranked[0].hops[0].step_id == 'availability'
    assert board.selected_member_id == 'carol'
