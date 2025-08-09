// This event listener ensures our script runs only after the entire HTML document is ready.
document.addEventListener("DOMContentLoaded", function () {
  // --- 0. Defensive Check ---
  // First, check if the propertyData variable actually exists.
  // This prevents errors if the map page is loaded without any data.
  if (typeof propertyData === "undefined" || !propertyData) {
    console.warn("No property data found to display on the map.");
    // We can optionally hide the map container if there's no data
    // document.getElementById('map').style.display = 'none';
    return; // Stop the script if there's no data
  }

  // --- 1. Initialize the Map ---
  const map = L.map("map").setView([-31.9523, 115.8605], 11);

  // --- 2. Add the Tile Layer ---
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  // --- 3. Use the 'propertyData' passed from the HTML template ---
  const properties = propertyData;

  // --- 4. Use MarkerCluster to Add Markers ---
  if (properties && properties.length > 0) {
    console.log(
      `Adding ${properties.length} sale records to the map from map.js`
    );

    const markers = L.markerClusterGroup();

    properties.forEach(function (prop) {
      if (
        typeof prop.latitude === "number" &&
        typeof prop.longitude === "number"
      ) {
        const marker = L.marker([prop.latitude, prop.longitude]);

        const popupContent = `
                    <div style="font-family: sans-serif; line-height: 1.5;">
                        <strong style="font-size: 1.1em;">${
                          prop.address
                        }</strong><br>
                        ${prop.suburb_name}<br><hr style="margin: 4px 0;">
                        <strong>Sold on:</strong> ${prop.date_sold}<br>
                        <strong>Price:</strong> $${new Intl.NumberFormat().format(
                          prop.price
                        )}<br>
                        <strong>Type:</strong> ${
                          prop.property_type
                            ? prop.property_type
                                .replace("-", " ")
                                .charAt(0)
                                .toUpperCase() + prop.property_type.slice(1)
                            : "N/A"
                        }<br>
                        <strong>Layout:</strong> ${
                          prop.layout_name || "N/A"
                        }<br>
                        <strong>Land Size:</strong> ${
                          prop.land_size ? prop.land_size + " sqm" : "N/A"
                        }<br>
                        <strong>Postcode:</strong> ${prop.postcode || "N/A"}<br>
                    </div>
                `;

        marker.bindPopup(popupContent);
        markers.addLayer(marker);
      }
    });

    map.addLayer(markers);

    // --- 5. Fit the Map to the Markers ---
    if (markers.getLayers().length > 0) {
      map.fitBounds(markers.getBounds().pad(0.1));
    }
  }
});
