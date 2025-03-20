"""
Data access functions for dotcat.
"""

from typing import Any, Dict, List

LIST_ACCESS_SYMBOL = "@"
SLICE_SYMBOL = ":"


def access_list(data: Any, key: str, index: str) -> Any:
    """
    Accesses a list within a dictionary using a key and an index or slice.

    Args:
        data: The dictionary containing the list.
        key: The key for the list.
        index: The index or slice to access.

    Returns:
        The accessed list item or slice.

    Raises:
        KeyError: If the index is invalid or the data is not a list.
    """
    try:
        if SLICE_SYMBOL in index:
            start, end = map(lambda x: int(x) if x else None, index.split(SLICE_SYMBOL))
            return data.get(key)[start:end]
        else:
            return data.get(key)[int(index)]
    except (IndexError, TypeError) as e:
        raise KeyError(f"Invalid index '{index}' for key '{key}': {str(e)}")


def from_dotted_path(data: Dict[str, Any], lookup_chain: str) -> Any:
    """
    Accesses a nested dictionary value with an attribute chain encoded by a
    dot-path string.

    Args:
        data: The dictionary to access.
        lookup_chain: The dotted-path string representing the nested keys.

    Returns:
        The value at the specified nested key, or None if the key doesn't exist.
    """
    keys = lookup_chain.split(".")
    found_keys = []

    if data is None:
        chain = keys[0]
        raise KeyError(f"key '{chain}' not found")

    for key in keys:
        if LIST_ACCESS_SYMBOL in key:
            key, index = key.split(LIST_ACCESS_SYMBOL)
            data = access_list(data, key, index)
        else:
            data = data.get(key)
        if data is None:
            full_path = ".".join(found_keys + [key])
            raise KeyError(f"key '{key}' not found in path '{full_path}'")
        found_keys.append(key)
    return data


def get_dotted_path_completions(data: Dict[str, Any], lookup_chain: str) -> List[str]:
    """
    Returns a list of possible completions for a given dotted path.

    Args:
        data: The dictionary to access.
        lookup_chain: The dotted-path string representing the nested keys.

    Returns:
        A list of possible completions.
    """
    keys = lookup_chain.split(".")
    current_data = data
    found_keys = []

    for i, key_part in enumerate(keys):
        if not current_data:
            return []

        if LIST_ACCESS_SYMBOL in key_part:
            key, _ = key_part.split(LIST_ACCESS_SYMBOL)
        else:
            key = key_part

        if isinstance(current_data, dict):
            matching_keys = [k for k in current_data.keys() if k.startswith(key)]
            if not matching_keys:
                return []

            if len(matching_keys) == 1 and key == matching_keys[0]:
                current_data = current_data.get(key)
                found_keys.append(key)
            else:
                if i == len(keys) - 1:
                    return matching_keys
                else:
                    return []
        else:
            return []

    if isinstance(current_data, dict):
        return list(current_data.keys())
    else:
        return []
