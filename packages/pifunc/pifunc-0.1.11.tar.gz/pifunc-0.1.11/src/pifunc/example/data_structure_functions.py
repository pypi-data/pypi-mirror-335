from typing import List, Dict, Any, TypeVar, Optional
from collections import defaultdict, Counter
from heapq import heappush, heappop, nlargest

T = TypeVar('T')

def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Flatten a nested list using recursion."""
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def group_by(items: List[T], key_func) -> Dict[Any, List[T]]:
    """Group items by a key function."""
    groups = defaultdict(list)
    for item in items:
        groups[key_func(item)].append(item)
    return dict(groups)

def find_duplicates(items: List[Any]) -> List[Any]:
    """Find all duplicate items in a list."""
    counter = Counter(items)
    return [item for item, count in counter.items() if count > 1]

def merge_dicts(dict1: Dict, dict2: Dict, combine_func=lambda x, y: y) -> Dict:
    """Merge two dictionaries with a custom combine function for duplicate keys."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            result[key] = combine_func(result[key], value)
        else:
            result[key] = value
    return result

def rotate_list(items: List[Any], k: int) -> List[Any]:
    """Rotate a list by k positions."""
    if not items:
        return items
    k = k % len(items)
    return items[-k:] + items[:-k]

def find_top_n(items: List[Any], n: int, key=None) -> List[Any]:
    """Find top n items in a list using a heap."""
    return nlargest(n, items, key=key)

class LRUCache:
    """Implement a Least Recently Used (LRU) cache."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key: Any) -> Optional[Any]:
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

def deep_update(d: Dict, u: Dict) -> Dict:
    """Recursively update a dictionary."""
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def find_common_elements(*lists: List[Any]) -> List[Any]:
    """Find common elements in multiple lists."""
    if not lists:
        return []
    result = set(lists[0])
    for lst in lists[1:]:
        result.intersection_update(lst)
    return list(result)

class PriorityQueue:
    """Implement a priority queue using heapq."""
    def __init__(self):
        self._queue = []
        self._index = 0

    def push(self, item: Any, priority: int):
        heappush(self._queue, (-priority, self._index, item))
        self._index += 1

    def pop(self) -> Any:
        return heappop(self._queue)[-1] if self._queue else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0
