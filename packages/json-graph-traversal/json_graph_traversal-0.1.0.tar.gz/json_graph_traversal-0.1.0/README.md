from json_graph_traversal import JSONGraphTraversal

# Create a JSONGraphTraversal object from a dictionary
data = {
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
            "value": 3
        }
    ]
}

traversal = JSONGraphTraversal(data)

# Perform BFS traversal
print("BFS Traversal:")
for path, value in traversal.bfs():
    print(f"Path: {path}, Value: {value}")

# Perform DFS traversal
print("\nDFS Traversal:")
for path, value in traversal.dfs():
    print(f"Path: {path}, Value: {value}")