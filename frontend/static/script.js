// Initialize the map
const map = L.map("map").setView([0, 0], 2);

// Add OpenStreetMap tile layer
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Array to store markers
const markers = [];

// Function to add a marker
function addMarker(place_id, lat, lng, title, description) {
  const marker = L.marker([lat, lng]).addTo(map);
  marker.bindPopup(title);

  marker.on("click", function () {
    // Fetch the prediction times for the station
    current_time_in_iso_format = new Date().toISOString();
    fetch(
      `/proxy/predictions?place_id=${place_id}&time=${current_time_in_iso_format}&horizon=50`
    )
      .then((response) => response.json())
      .then((prediction) => {
        const predictionsContainer = document.getElementById("marker-info"); // Step 1: Assume there's an element with this ID in your HTML

        console.log(JSON.stringify(prediction));

        // Step 2: Create a new div element to hold the prediction details
        predictionsContainer.innerHTML = ""; // Clear previous predictions

        const predictionElement = document.createElement("div"); // Step 3
        predictionElement.className = "prediction"; // Optional: for styling

        // Create the request paragraph element
        const requestParagraph = document.createElement("p");
        requestParagraph.textContent = `Request: ${prediction.request.request_id}`;

        // Create the model paragraph element
        const modelParagraph = document.createElement("p");
        modelParagraph.textContent = `Model: ${prediction.model.name}@${prediction.model.version}`;

        // Append the paragraphs to the predictionElement
        predictionElement.appendChild(requestParagraph);
        predictionElement.appendChild(modelParagraph);

        // Create the div element
        const barChartContainer = document.createElement("div");
        barChartContainer.className = "barChartContainer";

        // Set the id
        barChartContainer.id = "barChartContainer";

        prediction.predictions.forEach((pred) => {
          const bar = document.createElement("div");
          bar.classList.add("bar");
          bar.style.height = `${pred.occupancy_ratio * 100}%`; // Scale bar height based on maxTime

          barChartContainer.appendChild(bar);

          const timeLabelContainer = document.createElement("div");
          timeLabelContainer.className = "timeLabel";
          timeLabelContainer.textContent = pred.time.slice(11, 16);

          bar.appendChild(timeLabelContainer);
        });

        // Append the div to the body or another container element
        predictionElement.appendChild(barChartContainer); // Assuming you want to append it to the body

        predictionsContainer.appendChild(predictionElement); // Step 5
      });
  });

  markers.push(marker);
}

// Fetch stations and add markers
function fetchStationsAndAddMarkers() {
  fetch("/stations")
    .then((response) => response.json())
    .then((stations) => {
      stations.forEach((station) => {
        addMarker(
          station.place_id,
          station.lat,
          station.lon,
          station.common_name,
          station.description
        );
      });

      // Fit map to bounds
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds());
    })
    .catch((error) => console.error("Error fetching stations:", error));
}

// Call the function to fetch stations and add markers
fetchStationsAndAddMarkers();

// Add click event to add new markers
map.on("click", function (e) {
  // const title = prompt('Enter marker title:');
  // if (title) {
  //     const description = prompt('Enter marker description:');
  //     addMarker(e.latlng.lat, e.latlng.lng, title, description);
  // }
});
