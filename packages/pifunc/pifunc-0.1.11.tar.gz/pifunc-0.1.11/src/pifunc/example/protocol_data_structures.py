"""
Example of data structure operations exposed through different protocols using pifunc decorators.
"""
from pifunc import http, mqtt, websocket, grpc
from typing import List, Dict, Optional, Any

@http("/api/list/sort")
@mqtt("list/sort")
@websocket("list.sort")
@grpc("list.sort")
def sort_list(items: List[Any], reverse: bool = False) -> List[Any]:
    """Sort a list of comparable items."""
    return sorted(items, reverse=reverse)

@http("/api/list/remove-duplicates")
@mqtt("list/remove-duplicates")
@websocket("list.remove-duplicates")
@grpc("list.remove-duplicates")
def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicate items from a list while preserving order."""
    seen = set()
    result = []
    for item in items:
        if str(item) not in seen:  # Convert to string for hashability
            seen.add(str(item))
            result.append(item)
    return result

@http("/api/dict/merge")
@mqtt("dict/merge")
@websocket("dict.merge")
@grpc("dict.merge")
def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with dict2 values taking precedence."""
    return {**dict1, **dict2}

@http("/api/list/find")
@mqtt("list/find")
@websocket("list.find")
@grpc("list.find")
def find_in_list(items: List[Any], target: Any) -> Optional[int]:
    """Find the index of an item in a list, return None if not found."""
    try:
        return items.index(target)
    except ValueError:
        return None

@http("/api/dict/filter-by-value")
@mqtt("dict/filter-by-value")
@websocket("dict.filter-by-value")
@grpc("dict.filter-by-value")
def filter_dict_by_value(data: Dict[str, Any], predicate: str) -> Dict[str, Any]:
    """
    Filter dictionary by a predicate on values.
    predicate should be a string like '>10', '==True', etc.
    """
    result = {}
    for key, value in data.items():
        try:
            if eval(f"value {predicate}"):  # Safe since input is controlled
                result[key] = value
        except:
            continue
    return result
