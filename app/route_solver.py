import math

MAX_REACH = 150  # pixels


def distance(a, b):
    return math.sqrt((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2)


def build_graph(holds, max_reach=MAX_REACH):
    graph = {i: [] for i in range(len(holds))}

    for i in range(len(holds)):
        for j in range(len(holds)):
            if i == j:
                continue

            # Image coordinates grow downward, so upward movement goes to smaller y.
            if holds[j]["y"] >= holds[i]["y"]:
                continue

            if distance(holds[i], holds[j]) < max_reach:
                graph[i].append(j)

    return graph


def find_route(graph, holds):
    if not holds:
        return []

    start = max(range(len(holds)), key=lambda i: holds[i]["y"])
    end = min(range(len(holds)), key=lambda i: holds[i]["y"])

    visited = set()

    def dfs(node, path):
        if node == end:
            return path

        visited.add(node)

        for nei in graph[node]:
            if nei not in visited:
                result = dfs(nei, path + [nei])
                if result:
                    return result

        return None

    return dfs(start, [start]) or []
