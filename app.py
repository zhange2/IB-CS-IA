from flask import Flask, render_template, request, jsonify, abort
import os
import requests
import time

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
                else:
                    raise ConnectionError(f"Error connecting to OSRM: {response.status_code}")
    print(adjacency_matrix)
    return adjacency_matrix

@app.route('/calculate-route', methods=['POST'])
def solve_tsp(locations):
    # This assumes you are sending the data as JSON in the body of the POST request
    adjacency_matrix = get_adjacency_matrix(locations)
    # Solve TSP - Method 1: Brute Force
    
    return jsonify({"status": "success"})

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