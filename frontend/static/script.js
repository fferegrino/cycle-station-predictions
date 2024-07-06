// Initialize the map
const map = L.map('map').setView([0, 0], 2);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Array to store markers
const markers = [];

// Function to add a marker
function addMarker(lat, lng, title, description) {
    const marker = L.marker([lat, lng]).addTo(map);
    marker.bindPopup(title);
    
    marker.on('click', function() {
        document.getElementById('marker-info').innerHTML = `
            <h3>${title}</h3>
            <p>${description}</p>
        `;
    });
    
    markers.push(marker);
}



// Fetch stations and add markers
function fetchStationsAndAddMarkers() {
    fetch('/stations')
        .then(response => response.json())
        .then(stations => {
            stations.forEach(station => {
                addMarker(station.lat, station.lon, station.common_name, station.description);
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
