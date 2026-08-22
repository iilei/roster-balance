# Decision / Weighting Engine

## Purpose

The engine evaluates potential assignments using:

1. hard constraints
2. metrics / features
3. weighted scoring rules
4. deterministic tie-breaking
5. explainable results

## Conceptual pipeline

```text
Candidate
   |
Decision Context
   |
Hard Constraints
   |
Metrics / Features
   |
Weighted Scoring
   |
Decision Result
   |
Explanation
```

## Separation of concepts

### Constraint

Determines whether an assignment is allowed.

Examples:

- member unavailable
- insufficient rest after on-call
- member not eligible for the lane

The minimum-rest constraint compares a candidate period's start with each
matching member's latest prior assignment:

```text
previous_assignment.ends_at + previous_assignment.cooldown_after
  <= candidate_period.starts_at
```

The comparison is inclusive at the boundary. A failed result should identify
the prior assignment end and the earliest eligible time.

Factoring-entity durations use a strict compact form with `w`, `d`, `h`, and
`m` units. Multiple whitespace-separated tokens are allowed, for example
`1d 12h`. API input is normalized to integer seconds internally and returned
as canonical integer seconds, such as `36h` becoming `129600`.
Months, years, negative values, decimals, and partial token matches are not
accepted. A configured maximum is checked after all tokens have been summed.

### Metric

Measures something without deciding.

Examples:

- historical weighted load
- days since last on-call
- holiday burden deviation
- member avoidance score

### Scoring Rule

Transforms a metric into a score contribution.

Example:

```text
historical_load_deviation * weight
```

## Versioned decision policies

Decision policies are versioned application resources managed through the REST
API and persisted with the operational data. An active policy is immutable, and
each planning result records the exact policy ID and version used.

Policy definitions contain declarative references to constraints, metrics,
scoring factors, weights, and transforms. They must not contain executable
expressions, dynamic imports, or arbitrary formulas.

Suggested endpoints:

```text
GET   /teams/{team_id}/decision-policies
POST  /teams/{team_id}/decision-policies
GET   /teams/{team_id}/decision-policies/{policy_id}
PATCH /teams/{team_id}/decision-policies/{policy_id}
POST  /teams/{team_id}/decision-policies/{policy_id}/activate
```

For local development and tests, a checked-in TOML fixture may seed a policy or
provide representative input. TOML is not the authoritative runtime source.

Example policy definition:

```json
{
  "id": "default-on-call",
  "version": 1,
  "status": "active",
  "constraints": [
    {"id": "availability", "type": "availability"},
    {"id": "minimum-rest", "type": "minimum_rest", "params": {"hours": 24}}
  ],
  "factors": [
    {"id": "historical-load", "metric": "historical_load_deviation", "weight": 100.0, "transform": "linear"},
    {"id": "avoidance", "metric": "member_avoidance", "weight": 30.0, "transform": "linear"}
  ]
}
```

## Safety / maintainability

Do not allow:

- `eval()`
- arbitrary Python expressions
- dynamic imports configured by untrusted TOML
- arbitrary executable formulas

Instead, map configured `type`, `metric` and `transform` names through explicit registries.

## Suggested engine interfaces

```python
class Constraint(Protocol):
    def evaluate(
        self,
        candidate: AssignmentCandidate,
        context: DecisionContext,
    ) -> ConstraintResult:
        ...

class Metric(Protocol):
    def evaluate(
        self,
        candidate: AssignmentCandidate,
        context: DecisionContext,
    ) -> float:
        ...
```

## Decision result

The result should contain enough information to answer:

> Why was Alice selected instead of Bob?

Example shape:

```json
{
  "selectedMemberId": "alice",
  "candidates": [
    {
      "memberId": "alice",
      "eligible": true,
      "score": 14.2,
      "factors": [
        {
          "id": "historical-load",
          "rawValue": 0.12,
          "weight": 100,
          "contribution": 12
        },
        {
          "id": "avoidance",
          "rawValue": 0.0733,
          "weight": 30,
          "contribution": 2.2
        }
      ]
    },
    {
      "memberId": "bob",
      "eligible": false,
      "rejectedBy": ["vacation"]
    }
  ]
}
```

## Database independence

Application code prepares a complete DecisionContext before invoking the engine.

Bad:

```python
def score_member(member_id):
    session.execute(...)
```

Good:

```python
context = roster_context_repository.load(...)
result = decision_engine.evaluate(candidate, context)
```
