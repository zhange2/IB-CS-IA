import itertools

def tsp_brute_force(distance_matrix):
    n = len(distance_matrix)
    cities = range(n)

    # Generate all possible tours
    all_tours = itertools.permutations(cities)
    
    # Initialize minimum distance and corresponding path
    min_distance = float('inf')
    min_path = None

    # Check each possible tour and find the one with the smallest total distance
    for tour in all_tours:
        current_distance = sum(distance_matrix[tour[i]][tour[i+1]] for i in range(n - 1))
        current_distance += distance_matrix[tour[-1]][tour[0]]  # Return to start

        if current_distance < min_distance:
            min_distance = current_distance
            min_path = tour

    return min_distance, min_path
distance_matrix = [
    [0, 9198, 4689, 12686, 5989, 6134, 8642],
    [9198, 0, 6922, 14571, 11077, 9254, 6818],
    [4689, 6922, 0, 8641, 4997, 3173, 4598],
    [12686, 14571, 8641, 0, 9193, 7813, 8643],
    [5989, 11077, 4997, 9193, 0, 2837, 7909],
    [6134, 9254, 3173, 7813, 2837, 0, 6071],
    [8642, 6818, 4598, 8643, 7909, 6071, 0]
]

# Using the same example distance matrix as before
print(tsp_brute_force(distance_matrix))
