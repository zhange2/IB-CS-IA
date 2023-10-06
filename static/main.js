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

    suggestions.forEach(function (city) {
        var suggestion = document.createElement("div");
        suggestion.textContent = city;
        suggestion.classList.add("suggestion");
        suggestion.addEventListener("click", function () {
            selectSuggestion(this);
        });
        suggestionDiv.appendChild(suggestion);
    });
}

function selectSuggestion(suggestion) {
    var inputField = suggestion.parentElement.previousElementSibling;
    inputField.value = suggestion.textContent;
    suggestion.parentElement.innerHTML = ""; // Clear the suggestions
}

document.addEventListener("DOMContentLoaded", function () {
    var locationInputs = document.getElementsByName("location");

    locationInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            fetchCitySuggestions(this);
        });
    });
});