"""Bounded captured comparison with independent domain and scoped witnesses."""

from kaleion.comparison import compare_keyed_values, keyed_indices, keyed_items
from kaleion.model import Snapshot

from .views import exact_wire


def captured_comparison(left, left_by, left_value, right, right_by, right_value,
                        expected, expected_by):
    for result in (left, right, expected):
        if not isinstance(result, Snapshot):
            raise ValueError("Compare captured collections or arrangements; select an incidence explicitly first")
        if len(result) > 2000:
            raise ValueError("Comparison exceeds the 2000-item study budget")
    domain = keyed_indices(expected, keys=expected_by)
    if len(expected_by) != len(left_by):
        raise ValueError("Expected keys need the same number of fields, in matching order")
    report = compare_keyed_values(left, right, left_keys=left_by, right_keys=right_by,
                                  left_value=left_value, right_value=right_value,
                                  domain=tuple(domain))
    left_items = keyed_items(left, keys=left_by, value=left_value)
    right_items = keyed_items(right, keys=right_by, value=right_value)
    differences = {item.key: item.residual for item in report.differences}
    outside = tuple(dict.fromkeys((*report.unexpected_left, *report.unexpected_right)))

    def ref(source, items, key):
        return None if key not in items else [source.node, source.ids[items[key][0]]]

    def row(key, unexpected=False):
        a, b = left_items.get(key), right_items.get(key)
        residual = differences.get(key)
        status = ("outside" if unexpected else "missing" if a is None or b is None
                  else "equal" if residual == 0 else "different")
        return dict(key=list(key), status=status,
                    left=None if a is None else a[1], right=None if b is None else b[1],
                    residual=residual, left_ref=ref(left, left_items, key),
                    right_ref=ref(right, right_items, key),
                    expected_ref=None if key not in domain else [expected.node, expected.ids[domain[key]]])

    return exact_wire(dict(
        passed=report.holds, empty=not report.domain,
        left_capture=left.node, right_capture=right.node, expected_capture=expected.node,
        summary=dict(expected=len(domain), equal=len(report.differences)-len(report.nonzero),
                     different=len(report.nonzero), missing_left=len(report.missing_left),
                     missing_right=len(report.missing_right), outside_left=len(report.unexpected_left),
                     outside_right=len(report.unexpected_right)),
        rows=[row(key) for key in domain]+[row(key, True) for key in outside],
        claim="Equal integer fields with exactly the declared key domain",
        residual="left - right",
    ))
