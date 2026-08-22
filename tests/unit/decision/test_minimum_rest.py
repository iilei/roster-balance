from datetime import UTC, datetime, timedelta

from roster_balance.decision.constraints.minimum_rest import MinimumRestConstraint
from roster_balance.decision.context import (
    AssignmentCandidate,
    AssignmentEvent,
    DecisionContext,
    PlanningPeriod,
)


def make_context(starts_at: datetime) -> DecisionContext:
    return DecisionContext(
        periods=(
            PlanningPeriod(
                'next', starts_at, starts_at + timedelta(hours=24), 'on-call'
            ),
        ),
        committed_events=(
            AssignmentEvent(
                member_id='alice',
                lane_id='on-call',
                starts_at=datetime(2026, 8, 24, 9, tzinfo=UTC),
                ends_at=datetime(2026, 8, 25, 9, tzinfo=UTC),
                cooldown_after=timedelta(hours=24),
            ),
        ),
    )


def test_minimum_rest_allows_assignment_at_cooldown_boundary() -> None:
    result = MinimumRestConstraint().evaluate(
        AssignmentCandidate('alice', 'next'),
        make_context(datetime(2026, 8, 26, 9, tzinfo=UTC)),
    )

    assert result.passed is True
    assert result.hard is True
    assert '2026-08-26T09:00:00+00:00' in result.reason


def test_minimum_rest_rejects_assignment_before_cooldown_boundary() -> None:
    result = MinimumRestConstraint().evaluate(
        AssignmentCandidate('alice', 'next'),
        make_context(datetime(2026, 8, 26, 8, 59, tzinfo=UTC)),
    )

    assert result.passed is False
    assert result.step_id == 'minimum-rest'
    assert 'cooldown ends at 2026-08-26T09:00:00+00:00' in result.reason


def test_minimum_rest_ignores_assignments_for_other_members() -> None:
    result = MinimumRestConstraint().evaluate(
        AssignmentCandidate('bob', 'next'),
        make_context(datetime(2026, 8, 26, 8, 59, tzinfo=UTC)),
    )

    assert result.passed is True
    assert result.reason == 'No prior assignment requires cooldown'
