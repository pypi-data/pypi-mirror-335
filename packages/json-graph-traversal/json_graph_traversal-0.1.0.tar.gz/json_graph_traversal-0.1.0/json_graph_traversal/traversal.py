import json
from collections import deque
from typing import Any, Dict, List, Set, Union, Callable, Optional, Iterator, Tuple


class JSONGraphTraversal:
    """
    A class to traverse nested JSON data structures using BFS or DFS algorithms.
    """
    
    def __init__(self, data: Union[Dict, List]):
        """
        Initialize with JSON data
        
        Args:
            data: A JSON object (dict or list) to traverse
        """
        self.data = data
    
    def bfs(self, 
            start_key: Optional[str] = None, 
            filter_func: Optional[Callable] = None) -> Iterator[Tuple]:
        if start_key is not None:
            # Find the start node
            for path, value in self.bfs():
                if path and path[-1] == start_key:
                    queue = deque([(path, value)])
                    break
            else:
                raise ValueError(f"Start key '{start_key}' not found in the data")
        else:
            queue = deque([((), self.data)])  
        
        visited = set()
        
        while queue:
            path, current = queue.popleft()
            
            
            node_id = id(current)
            if node_id in visited:
                continue
            visited.add(node_id)
            
            
            if filter_func is None or filter_func(path[-1] if path else None, current):
                yield path, current
            
            
            if isinstance(current, dict):
                for key, value in current.items():
                    new_path = path + (key,)
                    if isinstance(value, (dict, list)):
                        queue.append((new_path, value))
                    else:
                        if filter_func is None or filter_func(key, value):
                            yield new_path, value
            elif isinstance(current, list):
                for i, value in enumerate(current):
                    new_path = path + (i,)
                    if isinstance(value, (dict, list)):
                        queue.append((new_path, value))
                    else:
                        if filter_func is None or filter_func(i, value):
                            yield new_path, value
    
    def dfs(self, 
            start_key: Optional[str] = None, 
            filter_func: Optional[Callable] = None) -> Iterator[Tuple]:
        
        if start_key is not None:
            # Find the start node
            for path, value in self.dfs():
                if path and path[-1] == start_key:
                    stack = [(path, value)]
                    break
            else:
                raise ValueError(f"Start key '{start_key}' not found in the data")
        else:
            
            stack = [((), self.data)]  
        
        visited = set()
        
        while stack:
            path, current = stack.pop()
            node_id = id(current)
            if node_id in visited:
                continue
            visited.add(node_id)
            
            
            if filter_func is None or filter_func(path[-1] if path else None, current):
                yield path, current
            
            
            if isinstance(current, dict):
                items = list(current.items())
                # Reverse to maintain the original order when popping from the stack
                for key, value in reversed(items):
                    new_path = path + (key,)
                    if isinstance(value, (dict, list)):
                        stack.append((new_path, value))
                    else:
                        if filter_func is None or filter_func(key, value):
                            yield new_path, value
            elif isinstance(current, list):
                # Reverse to maintain the original order when popping from the stack
                for i in range(len(current) - 1, -1, -1):
                    value = current[i]
                    new_path = path + (i,)
                    if isinstance(value, (dict, list)):
                        stack.append((new_path, value))
                    else:
                        if filter_func is None or filter_func(i, value):
                            yield new_path, value
    
    def find_values(self, search_value: Any, search_method: str = 'bfs') -> List[Tuple]:
        """
        Find all occurrences of a specific value in the JSON data
        
        Args:
            search_value: The value to search for
            search_method: The search method to use ('bfs' or 'dfs')
        
        Returns:
            List of (path, value) tuples where the value matches the search value
        """
        def filter_func(key, value):
            return value == search_value
        
        traversal_method = self.bfs if search_method.lower() == 'bfs' else self.dfs
        return list(traversal_method(filter_func=filter_func))
    
    def find_keys(self, search_key: Any, search_method: str = 'bfs') -> List[Tuple]:
        """
        Find all occurrences of a specific key in the JSON data
        
        Args:
            search_key: The key to search for
            search_method: The search method to use ('bfs' or 'dfs')
        
        Returns:
            List of (path, value) tuples where the key matches the search key
        """
        def filter_func(key, value):
            return key == search_key
        
        traversal_method = self.bfs if search_method.lower() == 'bfs' else self.dfs
        return list(traversal_method(filter_func=filter_func))
    
    def get_path(self, path: List[Union[str, int]]) -> Any:
        """
        Get the value at a specific path in the JSON data
        
        Args:
            path: A list of keys representing the path to the value
        
        Returns:
            The value at the specified path
        """
        current = self.data
        for key in path:
            try:
                current = current[key]
            except (KeyError, IndexError):
                raise ValueError(f"Invalid path: {path}")
        return current
    
    @classmethod
    def from_file(cls, file_path: str):
        """
        Create a JSONGraphTraversal object from a JSON file
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            A JSONGraphTraversal object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)
    
    @classmethod
    def from_string(cls, json_string: str):
        """
        Create a JSONGraphTraversal object from a JSON string
        
        Args:
            json_string: A JSON string
        
        Returns:
            A JSONGraphTraversal object
        """
        data = json.loads(json_string)
        return cls(data)