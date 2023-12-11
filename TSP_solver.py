def find_min_cost_path(cost):
    n = len(cost)
    # Maximum possible integer value based on number of cities (2^n)
    MAX_INT = 1 << n

    # Initializing dynamic programming table
    dp = [[float('inf')] * n for _ in range(MAX_INT)]
    dp[1][0] = 0  # Starting at node 0

    # Populating the table
    for mask in range(1, MAX_INT):
        for u in range(n):
            # Continue only if u is part of the current set (mask)
            if mask & (1 << u):
                for v in range(n):
                    if mask & (1 << v) and u != v:
                        dp[mask][u] = min(dp[mask][u], dp[mask ^ (1 << u)][v] + cost[v][u])

    # Finding the minimum cost
    min_cost = min(dp[MAX_INT - 1])
    end_node = dp[MAX_INT - 1].index(min_cost)

    # Reconstructing the path
    mask = MAX_INT - 1
    path = [end_node]

    while mask and end_node != 0:
        for v in range(n):
            if mask & (1 << v) and dp[mask][end_node] == dp[mask ^ (1 << end_node)][v] + cost[v][end_node]:
                path.append(v)
                mask ^= (1 << end_node)
                end_node = v
                break

    return min_cost, list(reversed(path))

# Example cost matrix
cost_matrix = [
    [0, 9198, 4689, 12686, 5989, 6134, 8642],
    [9198, 0, 6922, 14571, 11077, 9254, 6818],
    [4689, 6922, 0, 8641, 4997, 3173, 4598],
    [12686, 14571, 8641, 0, 9193, 7813, 8643],
    [5989, 11077, 4997, 9193, 0, 2837, 7909],
    [6134, 9254, 3173, 7813, 2837, 0, 6071],
    [8642, 6818, 4598, 8643, 7909, 6071, 0]
]

print(find_min_cost_path(cost_matrix))



