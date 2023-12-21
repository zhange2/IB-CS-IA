const colors = ['#FF0000', '#008000', '#FFC0CB', '#800080', '#FFA500', '#0000FF', '#FFFF00'];

let colorIndex = 0;
let selectedLocations = [];
let map;
let debounceTimeout;
let selectedEndLocation = null;
function fetchCitySuggestions(input) {
    console.log("Function triggered");
    var suggestionDivId = input.id === 'endLocation' ? 'endLocationSuggestions' : 'citySuggestions';
    var suggestionDiv = document.getElementById(suggestionDivId);

    // Clear any existing timeout to debounce the input
    if (debounceTimeout) {
        clearTimeout(debounceTimeout);
    }

    debounceTimeout = setTimeout(() => {
        var inputValue = input.value.trim();
        var isEndLocation = input.id === 'endLocation'; // Check if this is the end location input

        // Check if input value is already in selectedLocations
        var isAlreadySelected = selectedLocations.some(location => location.label.trim().toLowerCase() === inputValue.toLowerCase());

        // Only proceed with fetch if input value is not already selected
        if (!isAlreadySelected && inputValue.length > 0) {
            fetch(`/get-city-suggestions/${inputValue}`)
                .then(response => response.json())
                .then(data => {
                    if (isEndLocation) {
                        populateSuggestions(document.getElementById('endLocationSuggestions'), data, true);
                    } else {
                        populateSuggestions(input.nextElementSibling, data, false);
                    }
                })
                .catch(error => {
                    console.error(error);
                });
        } else {
            // Clear suggestions if input value is already selected or empty
            if (isEndLocation) {
                document.getElementById('endLocationSuggestions').innerHTML = "";
            } else {
                suggestionDiv.innerHTML = "";
            }
        }
    }, 1000);
}



function addLocationInput() {
    // Create new input element
    var newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "location";
    newInput.className = "locationInput";
    newInput.required = true;
    newInput.addEventListener("input", function () {
        fetchCitySuggestions(this);
    });

    // Create new suggestions div
    var newSuggestionsDiv = document.createElement("div");
    newSuggestionsDiv.className = "citySuggestions";

    // Create a new group div to hold both input and suggestions
    var inputGroup = document.createElement("div");
    inputGroup.className = "locationInputGroup";
    inputGroup.appendChild(newInput);
    inputGroup.appendChild(newSuggestionsDiv);

    // Append the group div to the container
    var container = document.getElementById("locationContainer");
    container.appendChild(inputGroup);
}

function populateSuggestions(suggestionDiv, suggestions, isEndLocation) {
    suggestionDiv.innerHTML = ""; // Clear previous suggestions

    suggestions.forEach(function (suggestionObj) {
        var suggestion = document.createElement("div");
        suggestion.textContent = suggestionObj.label; // Use the 'label' property of the suggestion object
        suggestion.classList.add("suggestion");
        suggestion.addEventListener("click", function () {
            if (isEndLocation) {
                selectEndLocationSuggestion(this);
            } else {
                selectSuggestion(this);
            }
            suggestionDiv.innerHTML = ''; // Clear the suggestions after a click
        });
        // Store the additional data as data attributes
        suggestion.setAttribute("data-lat", suggestionObj.lat);
        suggestion.setAttribute("data-lon", suggestionObj.lon);
        suggestion.setAttribute("data-importance", suggestionObj.importance);
        suggestionDiv.appendChild(suggestion);
    });
}


function selectSuggestion(suggestionElement) {
    var inputField = suggestionElement.parentElement.previousElementSibling;

    var locationData = {
        label: suggestionElement.textContent,
        lat: suggestionElement.getAttribute('data-lat'),
        lon: suggestionElement.getAttribute('data-lon'),
        importance: suggestionElement.getAttribute('data-importance')
    };
    fetch('/log-selected-locations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(selectedLocations)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
        })
        .catch(errorResponse => {
            errorResponse.json().then(error => {
                displayError(error.message); // Assuming the error object has a 'message' property
            }).catch(() => {
                displayError("An unexpected error occurred."); // Fallback error message
            });
        });

    // Add the location data object to the selectedLocations array
    selectedLocations.push(locationData);
    addMarker(locationData.lat, locationData.lon, locationData.label);
    console.log(selectedLocations)

    // Clear the input field and suggestions
    var suggestionsDiv = suggestionElement.parentElement;
    suggestionsDiv.innerHTML = '';

    // make sure that updated array is sent to server
    fetch('/log-selected-locations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(selectedLocations)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
        })
        .catch(errorResponse => {
            errorResponse.json().then(error => {
                displayError(error.message); // Assuming the error object has a 'message' property
            }).catch(() => {
                displayError("An unexpected error occurred."); // Fallback error message
            });
        });


    // Update the UI to show the selected locations
    updateSelectedLocationsUI();

    inputField.value = '';
    suggestionElement.parentElement.innerHTML = '';
}

function updateSelectedLocationsUI() {
    var locationsList = document.getElementById('selectedLocationsList');

    // clear existing list items
    locationsList.innerHTML = '';

    // add all selected locations to the list
    selectedLocations.forEach(function (location) {
        var listItem = document.createElement('li');
        listItem.className = 'selected-location';
        listItem.textContent = location.label;  // Set the text to the location label
        locationsList.appendChild(listItem);
    });
}


function addLocationInput() {
    // create new input element
    var newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "location";
    newInput.className = "locationInput";
    newInput.required = true;
    newInput.addEventListener("input", function () {
        fetchCitySuggestions(this);
    });

    // create a container for the new input element and suggestions div
    var inputGroup = document.createElement("div");
    inputGroup.className = "locationInputGroup";
    inputGroup.appendChild(newInput);
    inputGroup.appendChild(document.createElement("div")); // Placeholder for suggestions div

    var container = document.getElementById("locationContainer");
    container.appendChild(inputGroup);
}

document.addEventListener("DOMContentLoaded", function () {
    initMap();
    document.getElementsByName("location").forEach(input => input.addEventListener("input", () => fetchCitySuggestions(input)));
    document.getElementById('planRouteButton').addEventListener('click', (event) => {
        event.preventDefault();
        calculateOptimalRoute();
    });
});

document.getElementById('planRouteButton').addEventListener('click', function (event) {
    event.preventDefault();
    calculateOptimalRoute();
});

function calculateOptimalRoute() {
    console.log("calculateOptimalRoute function called");
    fetch('/calculate-route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locations: selectedLocations })
    })
        .then(response => response.ok ? response.json() : Promise.reject(response))
        .then(data => {
            if (data.error) throw new Error(data.error);
            displayRoute(data.route); // Assume this is an ordered list of location indices
        })
        .catch(errorResponse => {
            errorResponse.json().then(displayError).catch(() => displayError("An unexpected error occurred."));
        });
}

function displayError(message) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<p class="error-message">${message}</p>`;
}


function initMap() {
    map = L.map('map').setView([48.8566, 2.3522], 5); // Default to Paris, zoom level 5
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

// At the bottom of the main.js file
document.getElementById('setEndLocation').addEventListener('change', function () {
    var endLocationInput = document.getElementById('endLocationInputGroup');
    endLocationInput.style.display = this.checked ? 'block' : 'none';
});


function uncheckEndLocation() {
    if (document.getElementById('returnToStart').checked) {
        document.getElementById('setEndLocation').checked = false;
    }
}

function uncheckReturnToStart() {
    if (document.getElementById('setEndLocation').checked) {
        document.getElementById('returnToStart').checked = false;
    }
}

function selectEndLocationSuggestion(suggestionElement) {
    var inputField = document.getElementById('endLocation');
    inputField.value = suggestionElement.textContent; // Set the input field value to the text content
    var data = {
        label: suggestionElement.textContent,
        lat: suggestionElement.getAttribute('data-lat'),
        lon: suggestionElement.getAttribute('data-lon'),
        importance: suggestionElement.getAttribute('data-importance')
    };
    // You can add the selected end location to a global variable or handle it as needed
    selectedEndLocation = data;
    document.getElementById('endLocationSuggestions').innerHTML = '';
}

function debounce(func, wait) {
    let timeout;
    return function () {
        const context = this;
        const args = arguments;
        const later = function () {
            timeout = null;
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function addMarker(lat, lon, label) {
    var marker = L.marker([lat, lon]).addTo(map);
    marker.bindPopup(`<strong>${label}</strong>`, { className: 'custom-popup' }); // Add a class for custom styling
    marker.on('mouseover', function (e) {
        this.openPopup();
    });
    marker.on('mouseout', function (e) {
        this.closePopup();
    });
}

function displayRoute(routeIndices) {
    const routeText = routeIndices.map(index => selectedLocations[index].label).join(' -> ');
    document.getElementById('result').innerHTML = `<strong>Optimal Route:</strong> ${routeText}`;

    // Remove existing polylines
    if (map.hasOwnProperty('routePolyline')) {
        map.routePolyline.forEach(polyline => map.removeLayer(polyline));
    }
    map.routePolyline = [];

    // Display each segment of the route
    for (let i = 0; i < routeIndices.length - 1; i++) {
        const startLocation = selectedLocations[routeIndices[i]];
        const endLocation = selectedLocations[routeIndices[i + 1]];
        fetchAndDisplaySegment(startLocation, endLocation, i);
    }
}
// Adjust the map initialization to include a touch of animation
function initMap() {
    map = L.map('map').setView([48.8566, 2.3522], 5, { animation: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

// Call initMap when the DOM is loaded
document.addEventListener("DOMContentLoaded", initMap);


function fetchAndDisplaySegment(startLocation, endLocation, segmentIndex) {
    const apiKey = '1981c018315840e1b4111d0e9ec78a6b';
    const waypoints = `${startLocation.lat},${startLocation.lon}|${endLocation.lat},${endLocation.lon}`;
    const url = `https://api.geoapify.com/v1/routing?waypoints=${waypoints}&mode=drive&apiKey=${apiKey}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const routeLayer = L.geoJSON(data, {
                // color: colors[colorIndex % colors.length],
                color: 'blue',
                onEachFeature: function (feature, layer) {
                    const time = feature.properties.time / 3600; // Convert time to hours
                    const distance = feature.properties.distance / 1000; // Convert distance to kilometers
                    const popupContent = `Segment ${segmentIndex + 1}: ${startLocation.label} to ${endLocation.label}<br>Time: ${time.toFixed(2)} hours<br>Distance: ${distance.toFixed(2)} km`;
                    layer.bindPopup(popupContent);
                }
            }).addTo(map);

            // Bind mouseover and mouseout events to each segment
            routeLayer.on('mouseover', function (e) {
                e.layer.openPopup();
            });
            routeLayer.on('mouseout', function (e) {
                e.layer.closePopup(); 
            });

            colorIndex++;
        })
        .catch(error => console.error('Error fetching route:', error));
}
