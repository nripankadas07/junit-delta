# Research and project brief

Observed: 2026-10-06T06:11:30.320333+00:00 UTC, exact query `junit report`, sorted by stars descending.
[Search receipt](https://api.github.com/search/repositories?q=junit%20report&sort=stars&order=desc&per_page=5). Only the first ten results were inspected;
this is not an exhaustive worldwide ranking. jstemmer/go-junit-report is the highest-star
relevant comparable found in this query. Comparables can serve broader/different workflows.

| Repository | Observed stars | Repository pushed UTC | License metadata |
|---|---:|---|---|
| [jstemmer/go-junit-report](https://github.com/jstemmer/go-junit-report) | 824 | 2026-08-19T21:28:10Z | MIT |
| [mikepenz/action-junit-report](https://github.com/mikepenz/action-junit-report) | 428 | 2026-10-05T13:01:57Z | Apache-2.0 |
| [xmlrunner/unittest-xml-reporting](https://github.com/xmlrunner/unittest-xml-reporting) | 307 | 2026-01-07T16:11:37Z | NOASSERTION |

Pushed timestamps are evidence of repository activity, not proof of response/support quality.
Commit observations for the original research are in [machine-readable evidence](research.json).
Latest PR activity can be dependency automation rather than substantive maintenance.

## User, need and smallest useful capability

QA maintainers comparing two CI test runs across nested suites. Existing failures obscure new failures, silently removed tests and regressions in duration. Compares JUnit runs by nested suite/class/test identity and gates new failures, skips, removals and timing increases.

Read go-junit-report junit/junit.go, documentation and current issue/PR samples. action-junit-report PR #1630 concerns path-like classname mapping, supporting careful identity handling but not a request for our tool. Exact unmet demand remains inferred.

## Fair feature comparison

go-junit-report produces JUnit from Go output; action-junit-report publishes reports/annotations in GitHub; xmlrunner produces JUnit from Python unittest. Our focus is an offline two-inventory change gate, complementary to report generation and CI publishing.

Our install path is a source clone plus Python pip install, with no runtime third-party
dependencies. Alternatives have their documented Go/Node/Python/Rust, hosted platform or
calendar-server workflows; their setup was reviewed in current documentation, not timed.
Our example and failure checks are runnable. Our supported input surface and support are
smaller; mature alternatives have broader documentation, integrations and maintenance history.
License metadata is reported, not legal compatibility advice; no code was reused.

No equivalent cross-tool workload was measured. No speed, reliability or global ranking
superiority is claimed. Synthetic fixtures prove only our documented behavior. Negative
results and unsupported configurations are in [validation](VALIDATION.md).

## Distinctness and discovery

Compared all five candidate briefs with 138 existing README/description briefs.
Existing trace/report/diff tools do not make these five one product: their users, accepted
input contracts and working algorithms differ. The archive-preflight idea was rejected
because it overlapped the existing wheel/path safety tools. JUnit/CI topics and an offline before/after reproduction; no third-party posting.

Acceptance criteria: Handle nested suite identities, classify failure recovery versus new failure/skip, report removals, apply relative plus absolute timing thresholds, preserve unknown times, reject duplicate cases/DTD/nonfinite times, and provide deterministic JSON/exit codes.
