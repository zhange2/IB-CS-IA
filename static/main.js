let debounceTimeout;
function fetchCitySuggestions(input) {
    console.log("Function triggered");  
    var suggestionDiv = input.nextElementSibling;
    var inputValue = input.value.trim();

    if (debounceTimeout) {
        clearTimeout(debounceTimeout);
    }

    debounceTimeout = setTimeout(() => {
        var inputValue = input.value.trim();

        if (inputValue.length > 0) {
            fetch(`/get-city-suggestions/${inputValue}`)
                .then(response => response.json())
                .then(data => {
                    populateSuggestions(suggestionDiv, data);
                })
                .catch(error => {
                    console.error(error);
                });
        } else {
            suggestionDiv.innerHTML = "";  // Clear the suggestions if input is empty
        }
    }, 1000);  // 1 second delay
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

function populateSuggestions(suggestionDiv, suggestions) {
    suggestionDiv.innerHTML = ""; // Clear previous suggestions

    suggestions.forEach(function (suggestionObj) {
        var suggestion = document.createElement("div");
        suggestion.textContent = suggestionObj.label; // Use the 'label' property of the suggestion object
        suggestion.classList.add("suggestion");
        suggestion.addEventListener("click", function () {
            selectSuggestion(this);
        });
        // Store the additional data as data attributes
        suggestion.setAttribute("data-lat", suggestionObj.lat);
        suggestion.setAttribute("data-lon", suggestionObj.lon);
        suggestion.setAttribute("data-importance", suggestionObj.importance);
        suggestionDiv.appendChild(suggestion);
    });
}

let selectedLocations = []; 
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
        .catch((error) => {
            console.error('Error:', error);
        });
    // Add the location data object to the selectedLocations array
    selectedLocations.push(locationData);
    console.log(selectedLocations)
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
    .catch((error) => {
        console.error('Error:', error);
    });

    // Update the UI to show the selected locations
    updateSelectedLocationsUI();

    inputField.value = '';
    suggestionElement.parentElement.innerHTML = '';
}

function updateSelectedLocationsUI() {
    var locationsList = document.getElementById('selectedLocationsList');

    // Clear existing list items
    locationsList.innerHTML = '';

    // Add all selected locations to the list
    selectedLocations.forEach(function (location) {
        var listItem = document.createElement('li');
        listItem.className = 'selected-location';
        listItem.textContent = location.label;  // Set the text to the location label
        locationsList.appendChild(listItem);
    });
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

    // Create a container for the new input element and suggestions div
    var inputGroup = document.createElement("div");
    inputGroup.className = "locationInputGroup";
    inputGroup.appendChild(newInput);
    inputGroup.appendChild(document.createElement("div")); // Placeholder for suggestions div

    var container = document.getElementById("locationContainer");
    container.appendChild(inputGroup);
}

document.addEventListener("DOMContentLoaded", function () {
    var locationInputs = document.getElementsByName("location");

    locationInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            fetchCitySuggestions(this);
        });
    });
});

function calculateOptimalRoute() {
    // Assuming selectedLocations is an array of {lat, lon} objects
    fetch('/solve-tsp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ locations: selectedLocations })
    })
        .then(response => response.json())
        .then(optimizedRoute => {
            console.log('Optimized Route:', optimizedRoute);
            // Here you can update the map or the UI with the optimized route
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
