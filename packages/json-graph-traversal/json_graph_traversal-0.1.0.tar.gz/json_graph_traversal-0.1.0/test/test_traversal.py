"""
Tests for the json_graph_traversal package.
"""

import unittest
import json
from json_graph_traversal import JSONGraphTraversal


class TestJSONGraphTraversal(unittest.TestCase):
    """Test cases for JSONGraphTraversal class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = {
            "name": "root",
            "children": [
                {
                    "name": "child1",
                    "children": [
                        {"name": "grandchild1", "value": 1},
                        {"name": "grandchild2", "value": 2}
                    ]
                },
                {
                    "name": "child2",
                    "value": 3,
                    "metadata": {
                        "created_at": "2023-01-01",
                        "tags": ["important", "verified"]
                    }
                }
            ],
            "metadata": {
                "version": "1.0",
                "author": "Test Author"
            }
        }
        self.traversal = JSONGraphTraversal(self.test_data)
        
        # Create a temp file for testing file loading
        with open('test_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f)

    def test_bfs_traversal(self):
        """Test BFS traversal."""
        results = list(self.traversal.bfs())
        
        # Check if the root node is first
        self.assertEqual(results[0][0], ())
        self.assertEqual(results[0][1], self.test_data)
        
        # Check if the traversal visits all nodes
        self.assertTrue(any(path == ('name',) for path, _ in results))
        self.assertTrue(any(path == ('children',) for path, _ in results))
        self.assertTrue(any(path == ('children', 0, 'name') for path, _ in results))
        
        # Check leaf nodes
        leaf_values = [value for path, value in results if path == ('children', 0, 'children', 0, 'value')]
        self.assertEqual(leaf_values, [1])

    def test_dfs_traversal(self):
        """Test DFS traversal."""
        results = list(self.traversal.dfs())
        
        # Check if the root node is first
        self.assertEqual(results[0][0], ())
        self.assertEqual(results[0][1], self.test_data)
        
        # Check if the traversal visits all nodes
        self.assertTrue(any(path == ('name',) for path, _ in results))
        self.assertTrue(any(path == ('children',) for path, _ in results))
        self.assertTrue(any(path == ('children', 0, 'name') for path, _ in results))
        
        # Check leaf nodes
        leaf_values = [value for path, value in results if path == ('children', 0, 'children', 0, 'value')]
        self.assertEqual(leaf_values, [1])

    def test_find_values(self):
        """Test finding values."""
        results = self.traversal.find_values("important")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], ('children', 1, 'metadata', 'tags', 0))
        self.assertEqual(results[0][1], "important")
        
        # Test with different values
        results = self.traversal.find_values(2)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], ('children', 0, 'children', 1, 'value'))
        self.assertEqual(results[0][1], 2)

    def test_find_keys(self):
        """Test finding keys."""
        results = self.traversal.find_keys("name")
        self.assertEqual(len(results), 4)  # root, child1, grandchild1, grandchild2
        
        # Check if all expected paths are present
        paths = [path for path, _ in results]
        self.assertIn(('name',), paths)
        self.assertIn(('children', 0, 'name'), paths)
        self.assertIn(('children', 0, 'children', 0, 'name'), paths)
        self.assertIn(('children', 0, 'children', 1, 'name'), paths)

    def test_custom_filter(self):
        """Test custom filter."""
        def custom_filter(key, value):
            return isinstance(value, int) and value > 1
            
        results = list(self.traversal.bfs(filter_func=custom_filter))
        self.assertEqual(len(results), 2)  # values 2 and 3
        
        values = [value for _, value in results]
        self.assertIn(2, values)
        self.assertIn(3, values)

    def test_start_key(self):
        """Test starting from a specific key."""
        results = list(self.traversal.bfs(start_key="child1"))
        
        # Check if the first node is "child1"
        self.assertEqual(results[0][0], ('children', 0))
        self.assertEqual(results[0][1]['name'], "child1")
        
        # Check if it traverses the children of "child1"
        self.assertTrue(any(path == ('children', 0, 'children', 0, 'name') for path, _ in results))
        self.assertTrue(any(path == ('children', 0, 'children', 1, 'name') for path, _ in results))
        
        # Check if it doesn't traverse siblings or parents
        self.assertFalse(any(path == ('name',) for path, _ in results))
        self.assertFalse(any(path == ('children', 1, 'name') for path, _ in results))

    def test_invalid_start_key(self):
        """Test starting from a non-existent key."""
        with self.assertRaises(ValueError):
            list(self.traversal.bfs(start_key="non_existent_key"))

    def test_get_path(self):
        """Test getting a value at a specific path."""
        value = self.traversal.get_path(['children', 0, 'children', 1, 'value'])
        self.assertEqual(value, 2)
        
        with self.assertRaises(ValueError):
            self.traversal.get_path(['non', 'existent', 'path'])

    def test_from_file(self):
        """Test creating a JSONGraphTraversal from a file."""
        traversal = JSONGraphTraversal.from_file('test_data.json')
        self.assertEqual(traversal.data, self.test_data)

    def test_from_string(self):
        """Test creating a JSONGraphTraversal from a string."""
        json_string = json.dumps(self.test_data)
        traversal = JSONGraphTraversal.from_string(json_string)
        self.assertEqual(traversal.data, self.test_data)

    def test_cycle_detection(self):
        """Test cycle detection."""
        # Create a data structure with a cycle
        cyclic_data = {"a": 1}
        cyclic_data["b"] = cyclic_data  # Create a cycle
        
        traversal = JSONGraphTraversal(cyclic_data)
        
        # This should not cause an infinite loop
        results = list(traversal.bfs())
        self.assertTrue(len(results) > 0)
        
        results = list(traversal.dfs())
        self.assertTrue(len(results) > 0)

    def tearDown(self):
        """Clean up after tests."""
        import os
        if os.path.exists('test_data.json'):
            os.remove('test_data.json')


if __name__ == '__main__':
    unittest.main()