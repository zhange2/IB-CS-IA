from flask import Flask, render_template, request, jsonify, json, abort
import os
import requests
from requests.structures import CaseInsensitiveDict
import time
from itertools import permutations

app = Flask(__name__)
X_RAPIDAPI_KEY = os.environ.get("X_RAPIDAPI_KEY")
places = [
    {'name': 'Eiffel Tower', 'type': 'Monument'},
    {'name': 'Louvre Museum', 'type': 'Museum'},
    {'name': 'Central Park', 'type': 'Park'},
]

@app.route('/')
def index():
    return render_template('index.html', places=places)

@app.route('/get-city-suggestions/<input_text>')
def get_city_suggestions(input_text):
    try:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": input_text,
            "format": "json",
            "limit": 5,
            "addressdetails": 1,
            "extratags": 1  
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        suggestions = []
        for item in data:
            # extract city and country 
            address = item.get('address', {})
            city = address.get('city', '') or address.get('town', '') or address.get('village', '')
            country = address.get('country', '')
            
            # lat + lon
            lat = item.get('lat', '')
            lon = item.get('lon', '')
        
            importance = item.get('importance', '')
            
            print(f"City: {city}, Country: {country}, Latitude: {lat}, Longitude: {lon}, Importance: {importance}")

            if city:
                suggestions.append({"label": f"{city}, {country}", "lat": lat, "lon": lon, "importance": importance})
    
        return jsonify(suggestions)

    except Exception as e:
        print(e)
        abort(500)
    
@app.route('/get-adjacency-matrix', methods=['POST'])
def get_adjacency_matrix(input_text):
    print(f"Input text: {input_text}")
    if not input_text:
        print("input text is empty")
        return []
    locations = json.loads(input_text)
    geoapify_url = "https://api.geoapify.com/v1/routematrix?apiKey=1981c018315840e1b4111d0e9ec78a6b"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    # make api call
    sources = [{"location": [loc["lon"], loc["lat"]]} for loc in locations]

    data = {
        "mode": "drive",
        "sources": sources,
        "targets": sources  
    }
  
    n = len(locations)
    adjacency_matrix = [[0 if i == j else None for j in range(n)] for i in range(n)]
    response = requests.post(geoapify_url, headers=headers, data=json.dumps(data))
    print(response)
    if response.status_code == 200:
        matrix_data = response.json()
        print(matrix_data)
        for i in range(n):
            for j in range(i+1, n):
                distance = matrix_data['sources_to_targets'][i][j]['time']
                if distance < 3000000:  # threshold for an impossible route
                    adjacency_matrix[i][j] = distance
                    adjacency_matrix[j][i] = distance
                else:
                    adjacency_matrix[i][j] = float('inf')
                    adjacency_matrix[j][i] = float('inf')
    elif response.status_code == 400:
        # Raise a ValueError if locations are unreachable
        error_details = response.json()
        raise ValueError(f"Route not found between some locations. Make sure all your locations are reachable by drive. Details: {error_details}")
    else:
        # For other errors, raise a generic connection error
        raise ConnectionError(f"Error with Geoapify API: {response.status_code}")

    print(adjacency_matrix)
    return adjacency_matrix



def find_min_cost_path(cost):
    n = len(cost)
    MAX_INT = 1 << n
    dp = [[float('inf')] * n for _ in range(MAX_INT)]
    dp[1][0] = 0

    for mask in range(1, MAX_INT):
        for u in range(n):
            if mask & (1 << u):
                for v in range(n):
                    if mask & (1 << v) and u != v:
                        dp[mask][u] = min(dp[mask][u], dp[mask ^ (1 << u)][v] + cost[v][u])

    min_cost = min(dp[MAX_INT - 1])
    end_node = dp[MAX_INT - 1].index(min_cost)

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

MAX_LOCATIONS = 25 # Maximum number of locations allowed

@app.route('/calculate-route', methods=['POST'])
def calculate_route():
    try:
        data = request.get_json()

        # Check for empty input
        if not data or 'locations' not in data or not data['locations']:
            return jsonify({"error": "No locations provided"}), 400

        # Check for the number of locations
        if len(data['locations']) > MAX_LOCATIONS:
            return jsonify({"error": f"Too many locations. The maximum allowed is {MAX_LOCATIONS}."}), 400

        locations = data['locations']
        distance_matrix = get_adjacency_matrix(json.dumps(locations))

        # Check for unreachable locations within the distance matrix
        if any(float('inf') in row for row in distance_matrix):
            return jsonify({"error": "One or more locations are unreachable."}), 400

        min_path_cost, shortest_path = find_min_cost_path(distance_matrix)

        if not shortest_path:
            return jsonify({"error": "Could not calculate the route."}), 500
        print("Route:", shortest_path, "cost:", min_path_cost)
        return jsonify({"route": shortest_path, "cost": min_path_cost})

    except ValueError as e:
        # Catch the ValueError raised when there is a 400 status code from Geoapify
        return jsonify({"error": str(e)}), 400
    except ConnectionError as e:
        # Catch other connection-related errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Catch all other exceptions
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/log-selected-locations', methods=['POST'])
def log_selected_locations():
    data_string = request.data.decode('utf-8')
    selected_locations = json.loads(data_string)
    # print("Current Array", selected_locations)
    # print("Adjacency Matrix")
    # get_adjacency_matrix(json.dumps(selected_locations))
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
