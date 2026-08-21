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

## TOML configuration

TOML describes policies declaratively.

Example:

```toml
[policy]
id = "default-on-call"
version = 1

[[constraints]]
id = "availability"
type = "availability"

[[constraints]]
id = "minimum-rest"
type = "minimum_rest"

[constraints.params]
hours = 24

[[factors]]
id = "historical-load"
metric = "historical_load_deviation"
weight = 100.0
transform = "linear"

[[factors]]
id = "avoidance"
metric = "member_avoidance"
weight = 30.0
transform = "linear"
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
