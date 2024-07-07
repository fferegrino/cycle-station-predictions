// Initialize the map
const map = L.map('map').setView([0, 0], 2);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Array to store markers
const markers = [];

// Function to add a marker
function addMarker(place_id, lat, lng, title, description) {
    const marker = L.marker([lat, lng]).addTo(map);
    marker.bindPopup(title);
    
    marker.on('click', function() {

        // Fetch the prediction times for the station
        current_time_in_iso_format = new Date().toISOString();
        fetch(`/proxy/predictions?place_id=${place_id}&time=${current_time_in_iso_format}`)
            .then(response => response.json())
            .then(prediction => {
                const predictionsContainer = document.getElementById('marker-info'); // Step 1: Assume there's an element with this ID in your HTML


                    // Step 2: Create a new div element to hold the prediction details
                    predictionsContainer.innerHTML = ''; // Clear previous predictions

                    const predictionElement = document.createElement('div'); // Step 3
                    predictionElement.className = 'prediction'; // Optional: for styling
            
                    // Adding place ID, model version, and run ID
                    predictionElement.innerHTML = `
                        <h3>Place ID: ${prediction.place_id}</h3>
                        <p>Model Version: ${prediction.model_info.version}, Run ID: ${prediction.model_info.run_id}</p>
                    `;
            
                    // Step 4: Iterate over each prediction detail and add it to the predictionElement
                    prediction.predictions.forEach(pred => {
                        predictionElement.innerHTML += `
                            <div>
                                <p>Time: ${pred.time}</p>
                                <p>Occupancy Ratio: ${pred.occupancy_ratio.toFixed(2)}</p>
                                <p>Range: [${pred.occupancy_ratio_lower.toFixed(2)}, ${pred.occupancy_ratio_upper.toFixed(2)}]</p>
                            </div>
                        `;
                    });
            
                    predictionsContainer.appendChild(predictionElement); // Step 5

        });
    });
    
    markers.push(marker);
}



// Fetch stations and add markers
function fetchStationsAndAddMarkers() {
    fetch('/stations')
        .then(response => response.json())
        .then(stations => {
            stations.forEach(station => {
                addMarker(
                    station.place_id, station.lat, 
                    station.lon, station.common_name, station.description);
            });

            // Fit map to bounds
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds());
        })
        .catch(error => console.error('Error fetching stations:', error));
}

// Call the function to fetch stations and add markers
fetchStationsAndAddMarkers();

// Add click event to add new markers
map.on('click', function(e) {
    // const title = prompt('Enter marker title:');
    // if (title) {
    //     const description = prompt('Enter marker description:');
    //     addMarker(e.latlng.lat, e.latlng.lng, title, description);
    // }
});
