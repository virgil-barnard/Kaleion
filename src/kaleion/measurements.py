"""Captured measurement evidence, independent of execution and presentation.

Reductions enumerate contributors. Ordered ranks store each group's ordered
occurrences once and one prefix range per result. Queries expand only that range.
"""


def is_measurement(metadata):
    return "contributor_ids" in metadata or "contributor_prefixes" in metadata


def contributors(metadata, key):
    if not is_measurement(metadata):
        raise ValueError(
            "Inspect a measurement or its unchanged placement; value transformations have their own input provenance"
        )
    keys = metadata.get("keys", ())
    key = key if isinstance(key, tuple) else (key,)
    if key not in keys:
        raise KeyError(key)
    if keys.count(key) != 1:
        raise ValueError("This key has repeated occurrences; inspect the source measurement")
    index = keys.index(key)
    if "contributor_ids" in metadata:
        return metadata["contributor_ids"][index]
    prefix = metadata["contributor_prefixes"]
    if prefix.get("version") != 1:
        raise ValueError("Unsupported contributor-prefix version")
    group, stop = prefix["ranges"][index]
    if (not isinstance(group, int) or not isinstance(stop, int)
            or isinstance(group, bool) or isinstance(stop, bool)
            or not 0 <= group < len(prefix["groups"])
            or not 0 <= stop <= len(prefix["groups"][group])):
        raise ValueError("Invalid contributor prefix")
    return prefix["groups"][group][:stop]


def reindex(metadata, addresses):
    """Keep measurement keys and evidence aligned with gathered results."""
    out = dict(metadata)
    if is_measurement(metadata):
        for name in ("keys", "population", "contributor_ids"):
            if name in metadata:
                out[name] = tuple(metadata[name][i] for i in addresses)
        if "contributor_prefixes" in metadata:
            prefix = metadata["contributor_prefixes"]
            out["contributor_prefixes"] = {
                **prefix, "ranges": tuple(prefix["ranges"][i] for i in addresses),
            }
    return out


def changed_values(metadata, source_node):
    """A further value derivation must not claim the former measured quantity."""
    out = dict(metadata)
    if is_measurement(metadata):
        for name in ("reducer", "formula", "contributor_ids", "contributor_prefixes",
                     "keys", "population", "incidence", "universe", "counted"):
            out.pop(name, None)
        out["prior_measurement"] = source_node
    return out
