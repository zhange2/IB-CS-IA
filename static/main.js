function fetchCitySuggestions(input) {
    console.log("Function triggered");  // Just for debugging
    var suggestionDiv = input.nextElementSibling;  // Get the corresponding suggestion div (no need for double nextElementSibling)
    var inputValue = input.value.trim();

    if (inputValue.length > 0) {
        fetch(`/get-city-suggestions/${inputValue}`)
            .then(response => {
                if (!response.ok) {
                    // Return a rejected promise to jump to the .catch() block
                    return Promise.reject('Network response DOESNT WORK');
                }
                return response.json();
            })
            .then(data => {
                populateSuggestions(suggestionDiv, data);
            })
            .catch(error => {
                console.error('error:', error);
            });
    } else {
        suggestionDiv.innerHTML = "";  // Clear the suggestions if input is empty
    }
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