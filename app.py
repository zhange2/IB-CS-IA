from flask import Flask, render_template, request

app = Flask(__name__)

# Example
places = [
    {'name': 'Eiffel Tower', 'type': 'Monument'},
    {'name': 'Louvre Museum', 'type': 'Museum'},
    {'name': 'Central Park', 'type': 'Park'},
]

@app.route('/')
def index():
    return render_template('index.html', places=places)

@app.route('/filter', methods=['POST'])
def filter_destinations():
    preference = request.form.get('preference')
    filtered_places = [place for place in places if place['type'] == preference]
    return render_template('index.html', places=filtered_places)

if __name__ == '__main__':
    app.run(debug=True)
