"""Compare two JUnit XML inventories without executing tests or exposing logs."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

MAX_BYTES = 20_000_000
MAX_CASES = 100_000


def load(path: Path) -> dict[tuple[str, ...], dict]:
    with path.open('rb') as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('XML exceeds 20 MB limit')
    # Decode first: checking bytes alone misses UTF-16 entity declarations.
    if b'\x00' in raw:
        raise ValueError('only UTF-8 XML is supported')
    text = raw.decode('utf-8-sig')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD and entity declarations are not supported')
    root = ET.fromstring(text)
    if root.tag not in {'testsuite', 'testsuites'}:
        raise ValueError('expected testsuite or testsuites root without namespaces')
    result: dict[tuple[str, ...], dict] = {}

    def visit(node: ET.Element, suites: tuple[str, ...], depth: int) -> None:
        if depth > 64:
            raise ValueError('suite nesting exceeds 64')
        if node.tag == 'testsuite':
            name = node.get('name')
            if not name:
                raise ValueError('every testsuite requires a name')
            suites += (name,)
        for child in node:
            if child.tag in {'testsuite', 'testsuites'}:
                visit(child, suites, depth + 1)
            elif child.tag == 'testcase':
                if not suites or not child.get('name'):
                    raise ValueError('testcase requires suite and name')
                key = suites + (child.get('classname', ''), child.get('name', ''))
                if key in result:
                    raise ValueError('duplicate testcase identity; aggregate retries before comparison')
                states = [c.tag for c in child if c.tag in {'failure', 'error', 'skipped'}]
                if len(states) > 1:
                    raise ValueError('testcase has ambiguous multiple outcomes')
                duration = child.get('time')
                seconds = None if duration is None else float(duration)
                if seconds is not None and (not math.isfinite(seconds) or seconds < 0):
                    raise ValueError('testcase time must be finite nonnegative seconds')
                result[key] = {'state': states[0] if states else 'passed', 'seconds': seconds}
                if len(result) > MAX_CASES:
                    raise ValueError('case count exceeds 100000')
            elif child.tag not in {'properties', 'system-out', 'system-err'}:
                raise ValueError(f'unsupported suite element: {child.tag}')
    visit(root, (), 0)
    return result


def compare(before: dict, after: dict, slowdown: float = 0.5, minimum: float = 0.1) -> dict:
    if not math.isfinite(slowdown) or slowdown < 0 or not math.isfinite(minimum) or minimum < 0:
        raise ValueError('slowdown and minimum must be finite and nonnegative')
    changes = []
    regressions = 0
    for key in sorted(before.keys() | after.keys()):
        old, new = before.get(key), after.get(key)
        reasons = []
        if new is None:
            reasons.append('removed')
        elif old is None:
            reasons.append('added')
        elif old['state'] != new['state']:
            reasons.append('outcome-changed')
        bad = new is not None and new['state'] in {'failure', 'error'} and (
            old is None or old['state'] not in {'failure', 'error'})
        if bad:
            reasons.append('new-failure')
        elif new is not None and new['state'] == 'skipped' and (old is None or old['state'] != 'skipped'):
            reasons.append('new-skip')
            bad = True
        if old is not None and new is not None:
            a, b = old['seconds'], new['seconds']
            if a is not None and b is not None and b - a >= minimum and b > a * (1 + slowdown):
                reasons.append('slower')
                bad = True
        if bad:
            regressions += 1
        if reasons:
            changes.append({'identity': list(key), 'reasons': reasons, 'before': old, 'after': new})
    return {'schema': 1, 'before_cases': len(before), 'after_cases': len(after),
            'regressions': regressions, 'removed': len(before.keys() - after.keys()),
            'missing_times': sum(v['seconds'] is None for v in after.values()), 'changes': changes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--slowdown', type=float, default=0.5, help='relative increase, default 0.5 = 50%%')
    parser.add_argument('--minimum', type=float, default=0.1, help='minimum absolute increase in seconds')
    parser.add_argument('--allow-removed', action='store_true', help='permit cases missing from the new run')
    args = parser.parse_args(argv)
    try:
        report = compare(load(args.before), load(args.after), args.slowdown, args.minimum)
        print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))
        return int(bool(report['regressions'] or (report['removed'] and not args.allow_removed)))
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f'junit-delta: invalid input: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
