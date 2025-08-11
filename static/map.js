// static/map.js (v2.5 - Final Version with "Top 20" functionality)

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. Initialize the map and base layers ---
  const map = L.map("map").setView([-31.9523, 115.8605], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // --- 2. Display the initial property data from the "Data Bridge" ---
  const propertyMarkers = L.markerClusterGroup({
    maxClusterRadius: 60,
  });

  if (propertyData && propertyData.length > 0) {
    propertyData.forEach((p) => {
      if (p.latitude && p.longitude) {
        const marker = L.marker([p.latitude, p.longitude]);
        const popupContent = `
                    <div style="font-size: 1.1em; font-weight: bold;">${
                      p.address || "Address not available"
                    }</div>
                    <div style="color: #555;">${p.suburb_name || ""}</div>
                    <hr style="margin: 6px 0;">
                    <strong>Price:</strong> $${new Intl.NumberFormat().format(
                      p.price
                    )}<br>
                    <strong>Layout:</strong> ${p.layout_name || "N/A"}<br>
                    <strong>Sold on:</strong> ${p.date_sold}
                `;
        marker.bindPopup(popupContent);
        propertyMarkers.addLayer(marker);
      }
    });
    map.addLayer(propertyMarkers);
  }

  // --- 3. Setup for on-demand school layer loading ---

  // Create FOUR distinct layer groups to hold our school markers. They start empty.
  const primaryAllLayer = L.layerGroup();
  const primaryTopLayer = L.layerGroup();
  const secondaryAllLayer = L.layerGroup();
  const secondaryTopLayer = L.layerGroup();

  // An array of all school layers for easy management
  const allSchoolLayers = [
    primaryAllLayer,
    primaryTopLayer,
    secondaryAllLayer,
    secondaryTopLayer,
  ];

  // Define a single, reusable custom icon for all schools.
  const schoolIcon = L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/8074/8074788.png", // The professional building icon you chose
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -40],
  });

  // A generic and powerful function to fetch and toggle a school layer
  const toggleSchoolLayer = (schoolType, button, layer, topN = null) => {
    // If the layer is already on the map, we just hide it.
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
      button.classList.remove("active");
      return;
    }

    // --- UX Improvement: When showing a new layer, hide all others first ---
    allSchoolLayers.forEach((l) => map.removeLayer(l));
    document
      .querySelectorAll(".map-control-btn")
      .forEach((btn) => btn.classList.remove("active"));

    // If the layer is empty, we need to fetch the data from our API.
    if (layer.getLayers().length === 0) {
      button.innerText = "Loading...";
      button.disabled = true;

      // Build the API URL dynamically based on whether 'topN' is provided.
      let apiUrl = `/api/schools/${schoolType.toLowerCase()}`;
      if (topN) {
        apiUrl += `?top=${topN}`;
      }

      fetch(apiUrl)
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              `Network response was not ok: ${response.statusText}`
            );
          }
          return response.json();
        })
        .then((schools) => {
          button.disabled = false;
          button.innerText = button.dataset.originalText; // Restore original text
          if (schools.error) {
            throw new Error(schools.error);
          }

          schools.forEach((s) => {
            if (s.latitude && s.longitude) {
              const marker = L.marker([s.latitude, s.longitude], {
                icon: schoolIcon,
              });
              marker.bindPopup(
                `<b>${s.name}</b><br>Type: ${schoolType}<br>ICSEA: ${
                  s.icsea || "N/A"
                }`
              );
              layer.addLayer(marker);
            }
          });

          map.addLayer(layer); // Add the now-populated layer to the map
          button.classList.add("active");
        })
        .catch((error) => {
          console.error(`Fetch error for ${schoolType} schools:`, error);
          alert(
            `Could not load ${schoolType} school data. Please check the console.`
          );
          button.innerText = button.dataset.originalText; // Reset button text on error
        });
    } else {
      // If the layer already has data (fetched before), just add it back to the map.
      map.addLayer(layer);
      button.classList.add("active");
    }
  };

  // --- 4. Bind events to all FOUR buttons ---
  const primaryAllBtn = document.getElementById("toggle-primary-schools");
  const primaryTopBtn = document.getElementById("toggle-top-primary");
  const secondaryAllBtn = document.getElementById("toggle-secondary-schools");
  const secondaryTopBtn = document.getElementById("toggle-top-secondary");

  const allButtons = [
    primaryAllBtn,
    primaryTopBtn,
    secondaryAllBtn,
    secondaryTopBtn,
  ];

  // A small loop to store the original text of each button for later use.
  allButtons.forEach((btn) => {
    if (btn) {
      btn.dataset.originalText = btn.innerText;
    }
  });

  // Add event listeners, checking if the button exists first (?. syntax).
  primaryAllBtn?.addEventListener("click", () =>
    toggleSchoolLayer("Primary", primaryAllBtn, primaryAllLayer)
  );
  primaryTopBtn?.addEventListener("click", () =>
    toggleSchoolLayer("Primary", primaryTopBtn, primaryTopLayer, 50)
  );
  secondaryAllBtn?.addEventListener("click", () =>
    toggleSchoolLayer("Secondary", secondaryAllBtn, secondaryAllLayer)
  );
  secondaryTopBtn?.addEventListener("click", () =>
    toggleSchoolLayer("Secondary", secondaryTopBtn, secondaryTopLayer, 20)
  );
});
