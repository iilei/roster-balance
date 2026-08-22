"""Minimum-rest hard constraint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from roster_balance.decision.result import ConstraintResult

if TYPE_CHECKING:
    from roster_balance.decision.context import AssignmentCandidate, DecisionContext


class MinimumRestConstraint:
    """Reject a candidate whose prior assignment cooldown has not elapsed."""

    def evaluate(
        self, candidate: AssignmentCandidate, context: DecisionContext
    ) -> ConstraintResult:
        period = next(
            period for period in context.periods if period.id == candidate.period_id
        )
        events = (
            *context.historical_events,
            *context.committed_events,
            *context.suggested_events,
        )
        prior_events = sorted(
            (
                event
                for event in events
                if event.member_id == candidate.member_id
                and event.ends_at <= period.starts_at
            ),
            key=lambda event: event.ends_at,
            reverse=True,
        )
        if not prior_events:
            return ConstraintResult(
                step_id='minimum-rest',
                passed=True,
                hard=True,
                reason='No prior assignment requires cooldown',
            )

        prior = prior_events[0]
        eligible_at = prior.ends_at + prior.cooldown_after
        passed = period.starts_at >= eligible_at
        if passed:
            reason = f'Previous assignment cooldown ended at {eligible_at.isoformat()}'
        else:
            reason = (
                f'Previous assignment ended at {prior.ends_at.isoformat()}; '
                f'cooldown ends at {eligible_at.isoformat()}'
            )
        return ConstraintResult(
            step_id='minimum-rest',
            passed=passed,
            hard=True,
            reason=reason,
        )
