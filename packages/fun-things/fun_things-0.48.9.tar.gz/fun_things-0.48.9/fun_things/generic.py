def merge_dict(
    *dicts: dict,
    **kwargs,
):
    """
    Merge multiple dictionaries into a single dictionary.
    
    Args:
        *dicts: Variable number of dictionaries to merge.
        **kwargs: Additional key-value pairs to include in the merged dictionary.
        
    Returns:
        dict: A new dictionary containing all key-value pairs from all input dictionaries.
              If keys conflict, later dictionaries will override earlier ones.
    
    Examples:
        >>> merge_dict({'a': 1}, {'b': 2}, c=3)
        {'a': 1, 'b': 2, 'c': 3}
    """
    result = {}

    for dict in dicts:
        result.update(dict)

    result.update(kwargs)

    return result
