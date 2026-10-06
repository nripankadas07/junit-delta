# junit-delta

Compares JUnit runs by nested suite/class/test identity and gates new failures, skips, removals and timing increases.

Built for qA maintainers comparing two CI test runs across nested suites. Existing failures obscure new failures, silently removed tests and regressions in duration.

## Quickstart

Python 3.11 or later. No runtime dependencies, service account or API key.
Clone the public source, create an isolated environment and install:

```sh
git clone https://github.com/nripankadas07/junit-delta.git
cd junit-delta
python -m venv .venv
. .venv/bin/activate
python -m pip install .
junit-delta before.xml after.xml
```

Expected synthetic demo outcome: 2 cases in each run, zero regressions; retry recovers. JSON goes to stdout.
Use `--help` for options. On Windows, activate with `.venv\Scripts\activate`.
Windows is not locally validated in this launch; remote CI covers Linux Python 3.11/3.12/3.13.

## Contract

Handle nested suite identities, classify failure recovery versus new failure/skip, report removals, apply relative plus absolute timing thresholds, preserve unknown times, reject duplicate cases/DTD/nonfinite times, and provide deterministic JSON/exit codes.

Exit 0 means the supported input has no gated finding; 1 means a finding or gate failure;
2 means malformed or unsupported input/coverage. Read the JSON counts and limitations
before interpreting a zero result as comprehensive validation.

## Limitations

One UTF-8, unnamespaced JUnit XML file per run, 20 MB and 100000 cases each. Suite depth at most 64. Requires suite names and unique identities; aggregate retries first. Multiple outcome elements rejected. Does not use suite aggregate counters or status attributes as evidence of case outcome; direct failure/error/skipped elements determine state. Missing durations remain unknown. Timing changes in supplied reports are not a controlled performance benchmark. Failure text and stdout/stderr omitted, identities retained.

## Verify and contribute

```sh
python -m unittest -v
python -m compileall -q junit_delta.py
python -m pip install build
python -m build
```

The tests exercise successful behavior and meaningful failure cases. See
[validation](VALIDATION.md), [research](RESEARCH.md), [contribution guidance](CONTRIBUTING.md)
and [security guidance](SECURITY.md). Open a reproducible issue with a synthetic fixture;
do not post private exports or credentials. MIT licensed; implementation is original,
with no competitor code or prose copied.
