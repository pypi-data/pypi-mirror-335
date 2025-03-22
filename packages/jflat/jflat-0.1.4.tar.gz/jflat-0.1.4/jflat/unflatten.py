def unflatten(flattened):
    """
    Takes a flattened dictionary with JSONPath-style keys and converts it back to a nested structure.

    Args:
        flattened (dict): A flattened dictionary with JSONPath-style keys

    Returns:
        dict: A nested dictionary
    """
    # Magic key to mark dictionaries that should be converted to lists
    MAGIC_SLICE_KEY = "isSlice"

    # First, convert the flat map to a nested map
    nested = {}
    for key, value in flattened.items():
        p = path_from(key)
        current = nested
        for i, k in enumerate(p):
            key_name = k.key()
            if k.is_slice():
                current[MAGIC_SLICE_KEY] = True

            is_last = i == len(p) - 1
            if is_last:
                current[key_name] = value
                break

            if key_name not in current:
                current[key_name] = {}

            current = current[key_name]

    # Convert dictionaries to lists where appropriate using BFS
    queue = [nested]
    while queue:
        current = queue.pop(0)
        for k, v in list(current.items()):  # Create a copy of items to avoid modification during iteration
            if not isinstance(v, dict):
                # Not a dictionary, we reached the end of the tree
                continue

            if MAGIC_SLICE_KEY not in v:
                # Just a normal dictionary, enqueue
                queue.append(v)
                continue

            # A dictionary that needs to be converted to a list
            del v[MAGIC_SLICE_KEY]
            slice_result = to_slice(v)

            # Enqueue all dictionaries in the list
            for item in slice_result:
                if isinstance(item, dict):
                    queue.append(item)

            current[k] = slice_result

    # Handle case of a top-level list
    if MAGIC_SLICE_KEY in nested:
        del nested[MAGIC_SLICE_KEY]
        nested = to_slice(nested)

    return nested


def to_slice(d):
    """
    Converts a dictionary with numeric keys to a list.

    Args:
        d (dict): Dictionary with numeric keys (as strings)

    Returns:
        list: List with values at the correct indices
    """
    # Find the largest index to determine the slice size
    max_idx = max(int(k) for k in d.keys())
    slice_result = [None] * (max_idx + 1)

    for k, v in d.items():
        idx = int(k)
        if idx < 0 or idx >= len(slice_result):
            raise ValueError(f"Index {idx} out of bounds")
        slice_result[idx] = v

    return slice_result


class PathKey:
    """Represents a component in a JSONPath."""

    def __init__(self, name="", index=-1):
        self.name = name
        self.index = index

    def is_slice(self):
        """Returns True if this path component refers to a list index."""
        return self.index != -1

    def key(self):
        """Returns the key name as a string."""
        if self.is_slice():
            return str(self.index)
        return self.name


def path_from(key):
    """
    Parses a JSONPath-style key into a list of PathKey objects.

    Args:
        key (str): JSONPath-style key (e.g., "$.users[0].name")

    Returns:
        list: List of PathKey objects
    """
    # Remove the leading $
    key = key.lstrip("$")

    # Split by . but handle the case where the key starts with a dot
    if key.startswith("."):
        key = key[1:]

    split = key.split(".")
    path = []

    for s in split:
        keys = path_keys_from(s)
        path.extend(keys)

    return path


def path_keys_from(key):
    """
    Parses a single component of a JSONPath-style key.

    Args:
        key (str): Key component (e.g., "users[0]")

    Returns:
        list: List of PathKey objects
    """
    if "[" in key:
        start = key.index("[")
        end = key.index("]")
        index = int(key[start + 1 : end])

        # If there's a name part before the brackets
        if start > 0:
            return [PathKey(name=key[:start]), PathKey(index=index)]
        else:
            return [PathKey(index=index)]

    return [PathKey(name=key)]
