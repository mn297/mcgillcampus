<script lang="ts">
  import { onMount } from "svelte";
  import { MarkerClusterer } from "@googlemaps/markerclusterer";

  let container: HTMLElement | null;

  let map: google.maps.Map | undefined;
  let zoom = 16;
  let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
  let markerPosition: google.maps.LatLngLiteral | undefined;
  let markers = []; // Global array to hold markers
  let markerCluster: MarkerClusterer | undefined;

  let searchQuery = "";
  let timeValue = 515; // Slider value
  let selectedDay = "Monday"; // Default value

  // Function to convert slider value to time string
  // function formatTime(minutes: number) {
  // 	let hour = Math.floor(minutes / 60);
  // 	let newMinutes = minutes - hour * 60;
  // 	let afternoon = hour >= 12;
  // 	if (hour == 0) hour = 12;
  // 	return (
  // 		(hour > 12 ? hour - 12 : hour) +
  // 		":" +
  // 		newMinutes +
  // 		(newMinutes < 10 ? "0" : "") +
  // 		(afternoon == true ? " PM" : " AM")
  // 	);
  // }
  function formatTime(minutes: number) {
    let hour = Math.floor(minutes / 60);
    let newMinutes = minutes % 60; // Simpler way to get remaining minutes

    // Formatting for single-digit minutes
    let formattedMinutes =
      newMinutes < 10 ? "0" + newMinutes : newMinutes.toString();

    // Return the time in 24-hour format
    return `${hour}:${formattedMinutes}`;
  }

  // Hardcoded values for day and time
  // const day = "Monday";
  // const time = "10:30 AM";
  onMount(async () => {
    if (container) {
      map = new google.maps.Map(container, {
        zoom,
        center,
        mapId: "a25abe7f61616f26",
      });
      const { AdvancedMarkerElement } = (await google.maps.importLibrary(
        "marker"
      )) as google.maps.MarkerLibrary;

      // test marker position
      try {
        const response = await fetch("http://127.0.0.1:8000/get_lat_long");
        if (response.ok) {
          markerPosition = await response.json();
          console.log("Marker Position:", markerPosition);
        } else {
          console.error("Failed to get marker position:", response.statusText);
        }
      } catch (error) {
        console.error("Error:", error);
      }

      // Fetch course data
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/get_data?day=${encodeURIComponent(
            selectedDay
          )}&time=${encodeURIComponent(formattedTime)}`
        );
        if (response.ok) {
          const courseData = await response.json();
          console.log("courseData:", courseData);
          // Process courseData to display on the map
          // Add some markers to the map.
        } else {
          console.error("Failed to get courseData:", response.statusText);
        }
      } catch (error) {
        console.error("Error:", error);
      }

      const marker = new AdvancedMarkerElement({
        position: markerPosition,
        map: map,
      });
    }
  });
  function handleSearch() {
    console.log("Search query:", searchQuery);
    // Future implementation: Use searchQuery to perform a search
  }

  // Rerender slider value in GUI
  function updateTime() {
    const formattedTime = formatTime(timeValue);
    console.log("Selected Time:", formattedTime);
    // Call the API with the selected time
    // Replace this with your API call
  }

  // Sets the map on all markers in the array.
  function setMapOnAll(map) {
    for (let i = 0; i < markers.length; i++) {
      markers[i].setMap(map);
    }
  }

  // Removes the markers from the map, but keeps them in the array.
  function hideMarkers() {
    setMapOnAll(null);
  }

  // Shows any markers currently in the array.
  function showMarkers() {
    setMapOnAll(map);
  }

  function cleanUp() {
    hideMarkers();
    markers = [];
    if (markerCluster) {
      markerCluster.clearMarkers();
    }
  }

  // Deletes all markers in the array by removing references to them.
  function deleteMarkers() {
    hideMarkers();
    markers = [];
  }

  // Button event handler
  async function handleUpdate() {
    // Clear existing markers
    cleanUp();

    const { AdvancedMarkerElement } = (await google.maps.importLibrary(
      "marker"
    )) as google.maps.MarkerLibrary;
    const formattedTime = formatTime(timeValue);
    console.log("Selected Day:", selectedDay, "Selected Time:", formattedTime);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/get_data?day=${encodeURIComponent(
          selectedDay
        )}&time=${encodeURIComponent(formattedTime)}`
      );
      if (response.ok) {
        const courseData = await response.json();
        console.log("Updated courseData:", courseData);
        // Process courseData to display on the map
        const infoWindow = new google.maps.InfoWindow({
          content: "",
          disableAutoPan: true,
        });

        const newMarkers = courseData.map((data, i) => {
          const label = `${data.subject.substring(0, 2)}${data.course.substring(
            0,
            2
          )}`;
          const pinGlyph = new google.maps.marker.PinElement({
            glyph: label,
            glyphColor: "white",
          });

          // Ensure latitude and longitude are parsed as numbers
          const lat = parseFloat(data.latitude);
          const lng = parseFloat(data.longitude);

          // Debugging: Log the values and their types
          //   console.log(`Latitude: ${lat}, Longitude: ${lng}`);
          //   console.log(
          //     `Type of Latitude: ${typeof lat}, Type of Longitude: ${typeof lng}`
          //   );

          // Check if lat and lng are valid numbers
          if (isNaN(lat) || isNaN(lng)) {
            console.error("Invalid latitude or longitude");
            return null; // Skip this iteration
          }

          const position = { lat, lng };

          const marker = new AdvancedMarkerElement({
            position, // Using the transformed position
            map: map,
            content: pinGlyph.element,
          });

          // Format the content to display in the InfoWindow
          const infoContent = `

						<div>
						<h3>${data.subject} ${data.course}</h3>
						<p>Location: ${data.location_name}</p>
                        <p>Time: ${data.time}</p>
                        <p>Instructor: ${data.instructor}</p>
                        <p>Capacity: ${data.capacity}</p>
                        <p>CRN: ${data.crn}</p>
						<p>Additional Info: <a href="https://www.mcgill.ca/study/2023-2024/courses/${data.subject}-${data.course}" target="_blank">Course Information</a></p>
						<!-- Add more fields as necessary -->
						</div>
					`;

          // Set the content of the InfoWindow on marker click
          marker.addListener("click", () => {
            infoWindow.setContent(infoContent);
            // 	infoWindow.setContent(`${lat}, ${lng}`);
            infoWindow.open(map, marker);
          });

          return marker;
        });

        // Update global markers array with new markers
        markers = newMarkers;

        // Add a marker clusterer to manage the markers.
        markerCluster = new MarkerClusterer({ markers, map });
        // new MarkerClusterer({ newMarkers, map });
      } else {
        console.error("Failed to get courseData:", response.statusText);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }
</script>

<div class="container">
  <div class="date-selector">
    <select class="select" bind:value={selectedDay}>
      <option value="Monday">Monday</option>
      <option value="Tuesday">Tuesday</option>
      <option value="Wednesday">Wednesday</option>
      <option value="Thursday">Thursday</option>
      <option value="Friday">Friday</option>
      <option value="Saturday">Saturday</option>
      <option value="Sunday">Sunday</option>
    </select>
  </div>

  <button class="button" on:click={handleUpdate}>Update</button>
  <div class="time-slider">
    <input
      type="range"
      min="0"
      max="1440"
      step="15"
      bind:value={timeValue}
      on:change={updateTime}
    />
    <p class="time-slider-text">Selected Time: {formatTime(timeValue)}</p>
  </div>
  <div class="search-container">
    <input
      type="text"
      placeholder="Search location..."
      bind:value={searchQuery}
      on:input={handleSearch}
    />
  </div>
</div>
<div class="date-selector">
  <select bind:value={selectedDay}>
    <option value="Monday">Monday</option>
    <option value="Tuesday">Tuesday</option>
    <option value="Wednesday">Wednesday</option>
    <option value="Thursday">Thursday</option>
    <option value="Friday">Friday</option>
    <option value="Saturday">Saturday</option>
    <option value="Sunday">Sunday</option>
  </select>
</div>

<div class="search-container">
  <input
    type="text"
    placeholder="Search location..."
    bind:value={searchQuery}
    on:input={handleSearch}
  />
</div>
<div class="full-screen" bind:this={container}></div>

<style>
  .search-container {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
  }

  .search-container input[type="text"] {
    padding: 10px;
    width: 300px;
    font-size: 1rem;
  }

  .time-slider {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
  }
  .full-screen {
    width: 97vw;
    height: 90vh;
  }
  .search-container {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
  }

  .search-container input[type="text"] {
    padding: 10px;
    width: 300px;
    font-size: 1rem;
  }
  .button {
    background-color: #4caf50;
    /* Green */
    border: none;
    color: white;
    padding: 15px 32px;
    text-align: center;
    text-decoration: none;
    /* display: inline-block; */
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 100px;
  }
  .select {
    background-color: blue;
    /* Green */
    border: none;
    color: white;
    padding: 15px 32px;
    /* text-align: center; */
    text-decoration: none;
    /* display: inline-block; */
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 100px;
  }
  .container {
    display: flex;
    gap: 10px; /* Adjust the gap between elements */
  }
  .time-slider-text {
    font-family: Arial, Helvetica, sans-serif;
    color: blue;
  }
</style>
