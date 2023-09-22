from flask import Flask, jsonify

app = Flask(__name__)

graph = {
    'Eiffel Tower': {
        'Louvre Museum': {'distance': 2, 'cost': 5},
        'Central Park': {'distance': 7, 'cost': 20}
    },
    'Louvre Museum': {
        'Eiffel Tower': {'distance': 2, 'cost': 5},
        'Central Park': {'distance': 6, 'cost': 15}
    },
    'Central Park': {
        'Eiffel Tower': {'distance': 7, 'cost': 20},
        'Louvre Museum': {'distance': 6, 'cost': 15}
    }
}

preferences = [1, 2]  # modify preferences later

def create_graph(graph, preferences):
    for start, destinations in graph.items():
        for end, values in destinations.items():
            weight = sum(preference * values[factor] for preference, factor in zip(preferences, values.keys()))
            graph[start][end]['weight'] = weight

create_graph(graph, preferences)

@app.route('/dijkstra/<start>/<end>')

def dijkstra(start, end):
    priority_queue = []
    priority_queue.append((0, start))
    dist = {}
    prev = {}
    dist[start] = 0
    prev[start] = None

    while priority_queue:
        curr_weight, curr = min(priority_queue)
        priority_queue.remove((curr_weight, curr))

        if curr == end:
            break

        for neighbor, values in graph[curr].items():
            weight = sum(preference * values[factor] for preference, factor in zip(preferences, values.keys()))
            distance = dist[curr] + weight

            if neighbor not in dist or distance < dist[neighbor]:
                dist[neighbor] = distance
                prev[neighbor] = curr
                priority_queue.append((distance, neighbor))

    route = []
    curr = end
    while curr:
        route.append(curr)
        curr = prev[curr]
    route.reverse()

    return jsonify(route)



if __name__ == '__main__':
    app.run()
