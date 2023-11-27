from flask import Flask, jsonify, request
from scipy.spatial.distance import pdist, squareform
from scipy.optimize import linear_sum_assignment
import numpy as np

app = Flask(__name__)

def solve_tsp(distances):
    # assign id to each location
    
    # construct adjacency matrix
    
    # if n < 12 - can brute force
    # if n < 22 - can use dynamic programming
    # else - use heuristics
    
    return list(range(len(distances)))

@app.route('/solve-tsp', methods=['POST'])
def tsp_route():
    locations = request.json['locations']
    # Convert locations to a distance matrix
    distances = squareform(pdist(locations, 'euclidean'))
    # Solve TSP
    route_indices = solve_tsp(distances)
    # Create a route based on the indices
    optimized_route = [locations[i] for i in route_indices]
    return jsonify(optimized_route)

if __name__ == '__main__':
    app.run(debug=True)
