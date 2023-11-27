import requests
import polyline

def get_osrm_route_geometry(start, end):
    # Define the OSRM API endpoint
    osrm_endpoint = 'http://router.project-osrm.org/route/v1/driving/'
    # Format the start and end points into 'longitude,latitude'
    coordinates = f'{start[0]},{start[1]};{end[0]},{end[1]}'
    # Complete the request URL with the additional parameter 'overview=full' to get the full route geometry
    url = osrm_endpoint + coordinates + '?overview=full'
    
    # Send the GET request to the OSRM API
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Extract the encoded polyline from the first route
        route_polyline = data['routes'][0]['geometry']
        
        # Decode the polyline to get the list of coordinates
        route_coordinates = polyline.decode(route_polyline)
        route_duration = data['routes'][0]['duration'] 
        print(route_duration)
        print(url)
        return route_coordinates
    else:
        raise ConnectionError(f"Error connecting to OSRM: {response.status_code}")

# Replace with actual longitude and latitude of start and end locations
start_coords = (-122.423771, 37.774929)  # Example: San Francisco
end_coords = (-118.243683, 34.052235)  # Example: Los Angeles

try:
    route_coordinates = get_osrm_route_geometry(start_coords, end_coords)

    # You can now use 'route_coordinates' to plot the route on a map
except Exception as e:
    print(e)
