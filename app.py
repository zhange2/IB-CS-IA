from flask import Flask, render_template, request, jsonify, abort
import os
import requests

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
        city_names = []
        country_names = []

        url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities"
        headers = {
            "X-RapidAPI-Key": "c0c2759532msh8d152b57f44bf8ep1ac8c4jsn74b8c5e82525",
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }

        querystring = {
            "namePrefix": input_text,
            "limit": "5",
            "sort": "-population"
        }

        response = requests.get(url, headers=headers, params=querystring)
        print(response.text)
        data = response.json()

        if 'data' in data:
            city_names = [city['name'] for city in data['data']]
            country_names = [city['country'] for city in data['data']]
        ret = []
        for i in range(len(city_names)):
            ret.append(city_names[i] + ", " + country_names[i])
        return jsonify(ret)
    except Exception as e:
        print(e)
        abort(500)

@app.route('/filter', methods=['POST'])
def filter_destinations():
    preference = request.form.get('preference')
    filtered_places = [place for place in places if place['type'] == preference]
    return render_template('index.html', places=filtered_places)

if __name__ == '__main__':
    app.run(debug=True)
