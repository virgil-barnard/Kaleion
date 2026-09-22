"""Coverage against chosen keys, and a guarded assignment authoring recipe.

The report reads captures only. The recipe builds ordinary reductions, bindings,
and requirements; it neither trusts a report as a proof nor adds an evaluator op.
"""

from dataclasses import dataclass

from kaleion import F, Incidence, vector
from kaleion.indexing import align, key_rows
from kaleion.model import Snapshot

from .groups import CapturedGroups, captured_groups


def key_fields(by, expected_by):
    for fields in (by, expected_by):
        if (not isinstance(fields, (list, tuple)) or not fields
                or any(not isinstance(k, str) for k in fields)
                or len(set(fields)) != len(fields)):
            raise ValueError("Choose at least one distinct key field on each side")
    if len(by) != len(expected_by):
        raise ValueError("Source and expected keys need the same number of fields, in matching order")


@dataclass(frozen=True)
class CapturedCoverage:
    groups: CapturedGroups
    expected: Snapshot
    expected_by: tuple
    keys: tuple
    indices: tuple
    unexpected: tuple

    @property
    def counts(self):
        return tuple(0 if i is None else len(self.groups.matches[i]) for i in self.indices)

    @property
    def passed(self):
        return not self.unexpected and all(n == 1 for n in self.counts)


def captured_coverage(source, by, expected, expected_by):
    """Count matches for each unique expected key, including absent source keys.

    Expected occurrence order is display order, never a join. Nonincident
    candidates outside the expected domain are harmless; incident ones are
    reported separately and prevent adoption. Key equality follows the core.
    """
    key_fields(by, expected_by)
    if not isinstance(expected, Snapshot):
        raise ValueError("Choose a collection or arrangement as the expected domain")
    if len(expected) > 2000:
        raise ValueError("Expected domain exceeds the 2000-item study budget")
    context = expected.context()
    keys = key_rows([context[k] for k in expected_by], len(expected))
    try:
        align(keys, keys)
    except ValueError as error:
        raise ValueError("Expected keys must be unique; choose fields that distinguish occurrences") from error
    groups = captured_groups(source, by)
    lookup = {key: i for i, key in enumerate(groups.keys)}
    expected_set = set(keys)
    return CapturedCoverage(
        groups, expected, tuple(expected_by), keys,
        tuple(lookup.get(key) for key in keys),
        tuple(i for i, key in enumerate(groups.keys)
              if key not in expected_set and groups.matches[i]),
    )


def unique_assignment(source, by, expected, expected_by, value, field):
    """Attach each sole match's value as a field on the expected occurrences.

    All checks remain graph dependencies and are reevaluated with the definition.
    Missing bindings fail; they never supply zero. Equal-valued duplicate matches
    still fail. Output identity/placement/labels belong to expected; a keyed read leads
    to the weighted reduction and its original contributors.
    """
    key_fields(by, expected_by)
    source_groups = source.group_by(*(F[k] for k in by))
    expected_groups = expected.group_by(*(F[k] for k in expected_by))
    counts = source_groups.count()
    values = source_groups.sum(value=value)
    multiplicity = expected_groups.count()
    source_key = F[by[0]] if len(by) == 1 else vector(*(F[k] for k in by))
    expected_key = F[expected_by[0]] if len(expected_by) == 1 else vector(*(F[k] for k in expected_by))
    expected_checks = expected.where(counts.bind(on=expected_key, key=source_groups.key) == 1)
    matches = source.select() if isinstance(source, Incidence) else source
    in_domain = matches.where(multiplicity.bind(on=source_key, key=expected_groups.key) == 1)
    guarded = (expected.require(expected_checks, message="Assignment requires exactly one match per expected key")
               .require(in_domain, message="Every match must belong to the expected domain")
               .require(multiplicity.where(F.value == 1), message="Expected keys must be unique"))
    return guarded.annotate(**{field: values.bind(on=expected_key, key=source_groups.key)})
