def flatten(nested):
    """
    Takes a nested dictionary and flattens it into a single level dictionary.
    The flattening follows the JSONPath standard.

    Args:
        nested (dict): A nested dictionary, typically from JSON data

    Returns:
        dict: A flattened dictionary with JSONPath-style keys
    """
    # Handle different acceptable root types
    if isinstance(nested, dict):
        flattened = {}
        for child_key, child_value in nested.items():
            root_key = f"$.{child_key}"
            set_children(flattened, root_key, child_value)
        return flattened
    elif isinstance(nested, list):
        flattened = {}
        for child_index, child_value in enumerate(nested):
            root_key = f"$[{child_index}]"
            set_children(flattened, root_key, child_value)
        return flattened
    else:
        raise ValueError("Input must be a dictionary or list")


def set_children(flattened, parent_key, parent_value):
    """
    Helper function for flatten. Recursively processes nested values.

    Args:
        flattened (dict): The result dictionary being built
        parent_key (str): The current key path
        parent_value: The value to process
    """
    new_key = f".{parent_key}"

    # Handle the special case for root level keys
    if len(parent_key) > 1 and (parent_key[0:2] == "$." or parent_key[0:2] == "$["):
        new_key = parent_key

    # Handle None value
    if parent_value is None:
        flattened[new_key] = parent_value
        return

    # Handle dictionary
    if isinstance(parent_value, dict):
        for child_key, child_value in parent_value.items():
            new_key = f"{parent_key}.{child_key}"
            set_children(flattened, new_key, child_value)
        return

    # Handle list
    if isinstance(parent_value, list):
        if len(parent_value) == 0:
            flattened[new_key] = parent_value
            return

        for child_index, child_value in enumerate(parent_value):
            new_key = f"{parent_key}[{child_index}]"
            set_children(flattened, new_key, child_value)
        return

    # Handle primitive values
    flattened[new_key] = parent_value
