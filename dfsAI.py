def dfs_iterative(graph, start):
    visited = set()
    stack = [start]

    while stack:
        node = stack.pop()
        
        if node not in visited:
            visited.add(node)
            print(node, end=" ")
            
            # Add neighbors in reverse (to maintain order)
            stack.extend(reversed(graph[node]))

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': [],
    'F': []
}

print("DFS Traversal (Iterative):")
dfs_iterative(graph, 'A')