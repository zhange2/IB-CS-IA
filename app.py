from flask import Flask, render_template, request, jsonify, abort
import os
import requests
import time
from itertools import permutations

app = Flask(__name__)
X_RAPIDAPI_KEY = os.environ.get("X_RAPIDAPI_KEY")
# Example
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
            "extratags": 1  # Include extratags in the response for additional info
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        suggestions = []
        for item in data:
            # Get the city and country from the address part of the response
            address = item.get('address', {})
            city = address.get('city', '') or address.get('town', '') or address.get('village', '')
            country = address.get('country', '')
            
            # Latitude and longitude are top-level keys in the response
            lat = item.get('lat', '')
            lon = item.get('lon', '')
        
            # Importance is also a top-level key in the response
            importance = item.get('importance', '')
            
            # Printing to console
            print(f"City: {city}, Country: {country}, Latitude: {lat}, Longitude: {lon}, Importance: {importance}")

            # Append only city and country to suggestions list
            if city:
                suggestions.append({"label": f"{city}, {country}", "lat": lat, "lon": lon, "importance": importance})
    
        return jsonify(suggestions)

    except Exception as e:
        print(e)
        abort(500)


def get_adjacency_matrix(locations):
    n = len(locations)
    adjacency_matrix = [[0 if i == j else 1 for j in range(n)] for i in range(n)]
    osrm_endpoint = 'http://router.project-osrm.org/route/v1/driving/'
    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue
            else:
                coordinates = f'{locations[i]["lon"]},{locations[i]["lat"]};{locations[j]["lon"]},{locations[j]["lat"]}'
                url = osrm_endpoint + coordinates + '?overview=full'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    adjacency_matrix[i][j] = data['routes'][0]['duration']
                    adjacency_matrix[j][i] = data['routes'][0]['duration'] # THIS TOOK ME LIKE 20 MINS TO FIND 
                else:
                    raise ConnectionError(f"Error connecting to OSRM: {response.status_code}")
    print(adjacency_matrix)
    return adjacency_matrix

@app.route('/calculate-route', methods=['POST'])
def calculate_route():
    print("Called calculate route")
    try:
        data = request.get_json()
        locations = data['locations']
        adjacency_matrix = get_adjacency_matrix(locations)
        print("obtained matrix")
        # Solve TSP - Method 1: Brute Force
        n = len(locations)
        print("obtained N")
        best_route = None
        if n <= 5:
            start_city = 0  # Assuming the first city as the starting point
            best_route = None
            min_distance = float('inf')

            for route in permutations(range(1, n)):
                current_route = [start_city] + list(route) + [start_city]
                current_distance = sum(adjacency_matrix[current_route[i]][current_route[i+1]] for i in range(n))

                if current_distance < min_distance:
                    min_distance = current_distance
                    best_route = current_route
        
        # Solve TSP - Method 2: Dynamic Programming
        elif n <= 10:
            dp = {}
            print("entered here")
            for i in range(1, n):
                dp[(1 << i, i)] = (adjacency_matrix[0][i], 0)
            
            for r in range(2, n+1):
                for subset in permutations(range(1, n), r-1):
                    bits = sum(1 << bit for bit in subset)

                    for k in subset:
                        prev = bits & ~(1 << k)
                        res = []

                        for m in range(1, n):
                            if m == k or not (prev & (1 << m)):
                                continue
                            res.append((dp[(prev, m)][0] + adjacency_matrix[m][k], m))

                        if res:  # Ensure res is not empty
                            dp[(bits, k)] = min(res)
                        else:
                            dp[(bits, k)] = (float('inf'), -1)

            bits = (2**n - 1) - 1
            best_route = []
            for city in range(1, n):
                prev_distance, _ = dp[(bits, city)] # do not need the city
                res.append((prev_distance + adjacency_matrix[city][0], city))
                optimal_cost, last_city = min(res)

            # backtrack
            path = [last_city]
            for i in range(n - 2, 0, -1):
                bits, last_city = dp[(bits, last_city)][1], path[-1]
                path.append(last_city)
            path.append(0)
            best_route = list(reversed(path))

        return jsonify({"route": best_route})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/filter', methods=['POST'])
def filter_destinations():
    preference = request.form.get('preference')
    filtered_places = [place for place in places if place['type'] == preference]
    return render_template('index.html', places=filtered_places)

@app.route('/log-selected-locations', methods=['POST'])
def log_selected_locations():
    selected_locations = request.json
    print("Current Array", selected_locations)
    print("Adjacency Matrix")
    get_adjacency_matrix(selected_locations)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
