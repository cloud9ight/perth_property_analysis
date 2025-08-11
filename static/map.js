document.addEventListener("DOMContentLoaded", function () {
  // --- 1. Initialize the map and base layers ---
  const map = L.map("map").setView([-31.9523, 115.8605], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // --- 2. Display the initial property data ---
  const propertyMarkers = L.markerClusterGroup();
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
                    <strong>Sold on:</strong> ${p.date_sold}<br>
                    <strong>Price:</strong> $${new Intl.NumberFormat().format(
                      p.price
                    )}<br>
                    <strong>Type:</strong> ${
                      p.property_type
                        ? p.property_type.charAt(0).toUpperCase() +
                          p.property_type.slice(1)
                        : "N/A"
                    }<br>
                    <strong>Layout:</strong> ${p.layout_name || "N/A"}<br>
                    <strong>Land Size:</strong> ${
                      p.land_size ? p.land_size + " sqm" : "N/A"
                    }<br>
                    <strong>Postcode:</strong> ${p.postcode || "N/A"}<br>
                    <strong>Distance to CBD:</strong> ${
                      p.distance_to_cbd
                        ? (p.distance_to_cbd / 1000).toFixed(1) + " km"
                        : "N/A"
                    }
                `;
        marker.bindPopup(popupContent);
        propertyMarkers.addLayer(marker);
      }
    });
    map.addLayer(propertyMarkers);
  }

  // --- 3. Logic for on-demand school layer loading ---

  // Create layer groups to hold our school markers. They start empty.
  const primarySchoolLayer = L.layerGroup();
  const secondarySchoolLayer = L.layerGroup();

  // Define a custom icon for schools
  const schoolIcon = L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/8074/8074788.png", // A "school building" icon
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -40],
  });

  // A generic function to fetch and toggle a school layer
  const toggleSchoolLayer = (schoolType, button, layer) => {
    // If the layer is already on the map, remove it and reset the button.
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
      button.classList.remove("active");
      button.innerText = `Show ${schoolType} Schools`;
      return;
    }

    // If the layer is currently empty, it means we need to fetch the data from our API.
    if (layer.getLayers().length === 0) {
      button.innerText = "Loading...";
      button.disabled = true;

      fetch(`/api/schools/${schoolType.toLowerCase()}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              `Network response was not ok: ${response.statusText}`
            );
          }
          return response.json();
        })
        .then((schools) => {
          button.disabled = false; // Always re-enable the button
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
          button.innerText = `Hide ${schoolType} Schools`;
        })
        .catch((error) => {
          console.error(`Fetch error for ${schoolType} schools:`, error);
          alert(
            `Could not load ${schoolType} school data. Please check the console.`
          );
          button.innerText = `Show ${schoolType} Schools`; // Reset button on error
        });
    } else {
      // If the layer already has data (we've fetched it before), just add it back to the map.
      map.addLayer(layer);
      button.classList.add("active");
      button.innerText = `Hide ${schoolType} Schools`;
    }
  };

  // --- 4. Bind events to our toggle buttons ---
  const primaryBtn = document.getElementById("toggle-primary-schools");
  const secondaryBtn = document.getElementById("toggle-secondary-schools");

  if (primaryBtn) {
    primaryBtn.addEventListener("click", () => {
      toggleSchoolLayer("Primary", primaryBtn, primarySchoolLayer);
    });
  }
  if (secondaryBtn) {
    secondaryBtn.addEventListener("click", () => {
      toggleSchoolLayer("Secondary", secondaryBtn, secondarySchoolLayer);
    });
  }
});
