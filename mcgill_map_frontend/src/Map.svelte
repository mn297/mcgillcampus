<script lang="ts">
  import { onMount } from "svelte";
  import { MarkerClusterer } from "@googlemaps/markerclusterer";
  import {
    gaussianRandom,
    createHeatmapPoints,
    createHeatmapPoints_surround,
  } from "./utils.svelte";
  import debounce from "lodash.debounce";
  import courseIcons from "./courseIcons.json";
  import course_names from "./course_names.json";

  let container: HTMLElement | null;

  let map: google.maps.Map | undefined;
  let zoom = 16;
  let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
  let markerPosition: google.maps.LatLngLiteral | undefined;
  let markers = Array<google.maps.Marker>();
  let markerCluster: MarkerClusterer | undefined;
  let heatmap_main: google.maps.visualization.HeatmapLayer | undefined;
  let heatmap_surround: google.maps.visualization.HeatmapLayer | undefined;

  let searchQuery = "";
  let timeValue = 515; // Slider value
  let selectedDay = "Monday"; // Default value
  let courseData = [];
  let svgContent;
  import subjectColors from "./course_colors.json";
  const defaultColor = "#607D8B"; // Default color, e.g., Blue Grey

  // Function to create and add markers
  async function addMarkers() {
    for (const course of courseData) {
      const svgFileName = courseIcons[course.subject];
      if (svgFileName) {
        const svgUrl = `./path/to/svg/${svgFileName}`;
        const svgContent = await fetch(svgUrl).then((res) => res.text());
        createMarker(course, svgContent);
      }
    }
  }

  // TODO refactor to use createMarker
  // function createMarker(course, svgContent) {
  async function createMarker(data) {
    const { AdvancedMarkerElement } = (await google.maps.importLibrary(
      "marker"
    )) as google.maps.MarkerLibrary;

    // Extract label from course data
    const label = `${data.subject.substring(0, 4)}${data.course.substring(
      0,
      4
    )}`;

    // Create pin glyph
    const subjectColor = subjectColors[data.subject] || defaultColor;

    const pinGlyph = new google.maps.marker.PinElement({
      glyph: label,
      glyphColor: "black",
      background: subjectColor,
      borderColor: subjectColor,
    });

    // Parse latitude and longitude as numbers
    const lat = parseFloat(data.latitude);
    const lng = parseFloat(data.longitude);
    const position = { lat, lng };

    // Create and return the marker
    const marker = new AdvancedMarkerElement({
      position,
      map: map,
      content: pinGlyph.element,
    });

    return marker;
  }

  // TODO doesnt work
  async function createMarkerSVG(data) {
    // SVG MARKER
    const response = await fetch("./science.svg");
    svgContent = await response.text();
    const parser = new DOMParser();
    const pinSvg = parser.parseFromString(
      svgContent,
      "image/svg+xml"
    ).documentElement;
    const marker_svg = new google.maps.Marker({
      map,
      position: {
        lat: parseFloat(data.latitude),
        lng: parseFloat(data.longitude),
      },
      icon: {
        url:
          "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svgContent),
        scaledSize: new google.maps.Size(30, 30), // Adjust size as needed
      },
      title: data.subject,
    });
    // markersMap.set(course.id, marker); // Store the marker for later reference
    return marker_svg;
  }

  class CustomMarker extends google.maps.OverlayView {
    private image: string;
    private div?: HTMLElement;
    private label: string;
    private map: google.maps.Map | undefined;
    private position: google.maps.LatLng | undefined;

    constructor(position, label, map) {
      super();
      this.position = position;
      this.label = label;
      this.map = map;
    }

    /**
     * onAdd is called when the map's panes are ready and the overlay has been
     * added to the map.
     */
    onAdd() {
      this.div = document.createElement("div");
      this.div.style.borderStyle = "none";
      this.div.style.borderWidth = "0px";
      this.div.style.position = "absolute";
      this.div.style.cursor = "pointer";
      this.div.style.fontSize = "16px"; // Set your desired font size
      this.div.style.color = "black"; // Set font color
      this.div.innerText = this.label; // Set the label text

      // Add the element to the "overlayLayer" pane.
      const panes = this.getPanes()!;

      panes.overlayLayer.appendChild(this.div);
    }

    draw() {
      const overlayProjection = this.getProjection();

      // Check if the projection is available
      if (!overlayProjection) {
        // If not, defer the drawing
        requestAnimationFrame(() => this.draw());
        return;
      }

      // Proceed with drawing if the projection is available
      const point = overlayProjection.fromLatLngToDivPixel(this.latlng);

      if (point) {
        this.div.style.left = point.x + "px";
        this.div.style.top = point.y + "px";
      }
    }

    /**
     * The onRemove() method will be called automatically from the API if
     * we ever set the overlay's map property to 'null'.
     */
    onRemove() {
      if (this.div) {
        (this.div.parentNode as HTMLElement).removeChild(this.div);
        delete this.div;
      }
    }

    /**
     *  Set the visibility to 'hidden' or 'visible'.
     */
    hide() {
      if (this.div) {
        this.div.style.visibility = "hidden";
      }
    }

    show() {
      if (this.div) {
        this.div.style.visibility = "visible";
      }
    }

    toggle() {
      if (this.div) {
        if (this.div.style.visibility === "hidden") {
          this.show();
        } else {
          this.hide();
        }
      }
    }

    toggleDOM(map: google.maps.Map) {
      if (this.getMap()) {
        this.setMap(null);
      } else {
        this.setMap(map);
      }
    }
  }

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

      // TEST MARKER
      // const marker = new AdvancedMarkerElement({
      // 	position: markerPosition,
      // 	map: map,
      // });
    }
    handleUpdate();
  });
  function handleSearch() {
    console.log("Search query:", searchQuery);
    // Future implementation: Use searchQuery to perform a search
  }

  // Rerender slider value in GUI
  // function updateTime() {
  // 	const formattedTime = formatTime(timeValue);
  // 	console.log("Selected Time:", formattedTime);
  // 	// Call the API with the selected time
  // 	// Replace this with your API call
  // }
  const updateTime = debounce(() => {
    // Your update logic here
    const formattedTime = formatTime(timeValue);
    console.log("Selected Time:", formattedTime);
  }, 200); // Adjust the delay (in milliseconds) as needed

  // Sets the map on all markers in the array.
  async function setMapOnAll(map) {
    const resolvedMarkers = await Promise.all(markers);

    for (const marker of resolvedMarkers) {
      marker.setMap(map);
    }
    // for (let i = 0; i < markers.length; i++) {
    // 	markers[i].setMap(map);
    // }
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
    heatmap_main?.setMap(null);
    heatmap_surround?.setMap(null);
  }

  // Deletes all markers in the array by removing references to them.
  function deleteMarkers() {
    hideMarkers();
    markers = [];
  }
  // Function to update markers based on courseData
  function updateMarkers() {
    // TODO remove marker
  }
  function handleCheckboxChange(course) {
    course.isSelected = !course.isSelected;
    updateMarkers(); // Update markers when a course is selected/unselected
  }
  function selectAllCourses() {
    courseData = courseData.map((course) => ({
      ...course,
      isSelected: true,
    }));
  }

  // Rerender markers
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
        // Courses array
        courseData = []; // Reset courseData
        courseData = await response.json();
        console.log("Updated courseData:", courseData);

        courseData = courseData.filter((data) =>
          (data.subject + " " + data.course + " " + data.location_name)
            .toLowerCase()
            .includes(searchQuery.toLowerCase())
        );
        selectAllCourses();

        // Process courseData to display on the map
        const infoWindow = new google.maps.InfoWindow({
          content: "",
          disableAutoPan: true,
        });

        const newMarkers = courseData.map((data, i) => {
          // PIN GLYPH----------------------------------------------
          const label = `${data.subject.substring(0, 4)}${data.course.substring(
            0,
            4
          )}`;

          const subjectColor = subjectColors[data.subject] || defaultColor;

          const pinGlyph = new google.maps.marker.PinElement({
            glyph: label,
            glyphColor: "black",
            background: subjectColor,
            borderColor: "black",
          });

          // Ensure latitude and longitude are parsed as numbers
          const lat = parseFloat(data.latitude);
          const lng = parseFloat(data.longitude);
          const position = { lat, lng };

          // DEFAULT MARKER----------------------------------------------
          // TODO refector to use createMarker
          const marker = new AdvancedMarkerElement({
            position, // Using the transformed position
            map: map,
            content: pinGlyph.element,
          });

          // CUSTOM MARKER (TODO)----------------------------------------------
          // const temp_lat = Number.parseFloat(data.latitude);
          // const temp_lng = Number.parseFloat(data.longitude);
          // if (!isNaN(temp_lat) && !isNaN(temp_lng)) {
          // 	const position = new google.maps.LatLng(
          // 		temp_lat,
          // 		temp_lat,
          // 	);

          // 	const custom_marker = new CustomMarker(
          // 		position,
          // 		map,
          // 		label,
          // 	);
          // 	custom_marker.setMap(map);

          // 	console.log("custom_marker:", custom_marker);
          // 	custom_marker.draw();
          // }

          // // Debugging: Log the values and their types
          // //   console.log(`Latitude: ${lat}, Longitude: ${lng}`);
          // //   console.log(
          // //     `Type of Latitude: ${typeof lat}, Type of Longitude: ${typeof lng}`
          // //   );

          // // Check if lat and lng are valid numbers
          // if (isNaN(lat) || isNaN(lng)) {
          // 	console.error("Invalid latitude or longitude");
          // 	return null; // Skip this iteration
          // }
          // INFO WINDOW----------------------------------------------
          // Format the content to display in the InfoWindow
          const course_name = course_names[data.subject];
          const infoContent = `
						<div>
							<b>
						<h3>${data.subject} ${data.course} - ${course_name} - (${data.type})</h3>
						<p><u>Location</u>: ${data.location_name}</p>
                        <p><u>Time</u>: ${data.time}</p>
                        <p><u>Instructor</u>: ${data.instructor}</p>
                        <p><u>Capacity</u>: ${data.capacity}</p>
                        <p><u>CRN</u>: ${data.crn}</p>
                        <p><u>Instructor Rating</u>: ${data.rating}/5</p>
						<p><u>Additional Info</u>: <a href="https://www.mcgill.ca/study/2023-2024/courses/${data.subject}-${data.course}" target="_blank">Course Information</a></p>
						</b>
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
        // Clear previous markers array
        markers = [];

        // for (const data of courseData) {
        // 	if (
        // 		`${data.subject} ${data.course} ${data.location_name}`
        // 			.toLowerCase()
        // 			.includes(searchQuery.toLowerCase())
        // 	) {
        // 		const marker = await createMarker(data, map);
        // 		const infoContent = `
        // 			<div>
        // 			<h3>${data.subject} ${data.course}</h3>
        // 			<p>Location: ${data.location_name}</p>
        // 			<p>Time: ${data.time}</p>
        // 			<p>Instructor: ${data.instructor}</p>
        // 			<p>Capacity: ${data.capacity}</p>
        // 			<p>CRN: ${data.crn}</p>
        // 			<p>Instructor Rating: ${data.rating}/5</p>
        // 			<p>Additional Info: <a href="https://www.mcgill.ca/study/2023-2024/courses/${data.subject}-${data.course}" target="_blank">Course Information</a></p>
        // 			<!-- Add more fields as necessary -->
        // 			</div>
        // 			`;
        // 		// Add click listener to the marker
        // 		marker.addListener("click", () => {
        // 			infoWindow.setContent(infoContent);
        // 			infoWindow.open(map, marker);
        // 		});

        // 		markers.push(marker);
        // 	}
        // }
        // Update global markers array with new markers
        markers = newMarkers;

        // Add a marker clusterer to manage the markers.
        markerCluster = new MarkerClusterer({ markers, map });
        // new MarkerClusterer({ newMarkers, map });

        // HEATMAP
        const heatmapData_main = createHeatmapPoints(courseData);
        console.log("heatmapData:", heatmapData_main);
        heatmap_main = new google.maps.visualization.HeatmapLayer({
          data: heatmapData_main,
          map: map,
        });
        heatmap_main.set("opacity", 0.7);
        heatmap_main.set("radius", 60);

        const heatmapData_surround = createHeatmapPoints_surround(courseData);
        heatmap_surround = new google.maps.visualization.HeatmapLayer({
          data: heatmapData_surround,
          map: map,
        });
        heatmap_surround.set("opacity", 0.3);
        heatmap_surround.set("radius", 70);
      } else {
        console.error("Failed to get courseData:", response.statusText);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }
  function setCurrentTime() {
    const now = new Date();
    const hour = now.getHours();
    const minutes = now.getMinutes();
    timeValue = hour * 60 + minutes;

    const daysOfWeek = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ];
    const currentDate = new Date();
    const currentDayIndex = currentDate.getDay(); // 0 for Sunday, 1 for Monday, etc.

    // Set selectedDay to the current day
    selectedDay = daysOfWeek[currentDayIndex];
  }
</script>

<div class="container">
  <!-- Side Panel for Listing Courses -->
  <div class="side-panel">
    <ul>
      {#each courseData as course}
        <li>
          <input
            type="checkbox"
            bind:checked={course.isSelected}
            on:change={() => handleCheckboxChange(course)}
          />
          <div
            class="color-square"
            style="background-color: {subjectColors[course.subject] ||
              '#607D8B'}"
          ></div>
          <span on:click={() => showCourseInfo(course)}>
            <strong>{course.subject} {course.course}</strong> - {course.location_name}
            - CAP: {course.capacity}
          </span>
        </li>
      {/each}
    </ul>
  </div>

  <!-- Map Controls -->
  <div class="map-container">
    <div class="container">
      <!-- Search Container -->
      <div class="search-container">
        <input
          type="text"
          placeholder="Search location..."
          bind:value={searchQuery}
        />
        <button class="button" on:click={handleUpdate}>Search</button>
      </div>

      <!-- Date Selector -->
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

      <!-- Time Slider -->
      <div class="time-slider">
        <input
          type="range"
          min="0"
          max="1440"
          step="5"
          bind:value={timeValue}
          on:change={updateTime}
        />
        <p class="time-slider-text">
          Selected Time: {formatTime(timeValue)}
        </p>
      </div>

      <!-- Update Button -->
      <button class="button" on:click={handleUpdate}>Refresh</button>
      <!-- Set Current Time Button -->
      <button class="button" on:click={setCurrentTime}>Set Current Time</button>
    </div>
    <!-- Map Display -->
    <div class="full-screen" bind:this={container}></div>
  </div>
</div>

<style>
  .color-square {
    width: 15px;
    height: 15px;
    display: inline-block;
    margin-right: 5px;
    border: 1px solid #ddd; /* Optional: for better visibility */
  }

  .container {
    display: flex;
    gap: 20px;
  }

  .side-panel {
    width: 400px; /* Adjust width as needed */
    overflow-y: auto; /* Scroll if content is too long */
    background-color: #f8f8f8; /* Background color for the side panel */
    padding: 10px;
    height: 90vh; /* Match the height of the map container */
    font-family: "Arial", sans-serif; /* Specify your preferred font family */
    font-size: 16px; /* Adjust the font size as needed */
  }

  .map-container {
    flex-grow: 1;
    position: relative; /* For absolute positioning of its children */
  }

  .search-container {
    /* position: absolute; */
    top: 10px;
    left: 10px; /* Position near the top-left corner of the map */
    z-index: 10;
  }

  .search-container input[type="text"],
  .button,
  .select {
    padding: 10px;
    margin-bottom: 5px; /* Spacing between elements */
    font-size: 1rem;
  }

  .button,
  .select {
    background-color: #4caf50; /* Green for button, can change for select */
    border: none;
    color: white;
    text-align: center;
    cursor: pointer;
    border-radius: 100px; /* Adjust as needed */
    margin-top: 5px;
    margin-bottom: 5px;
    font-size: 1rem;
    padding: 20px;
  }

  .time-slider {
    z-index: 10;
    /* position: absolute; */
    /* bottom: 20px; /* Position at the bottom of the map container */
    /* left: 10px; Align with the search container */
  }

  .full-screen {
    width: 100%; /* Fill the map container */
    height: 90vh; /* Adjust as needed */
  }

  .time-slider-text {
    font-family: Arial, Helvetica, sans-serif;
    color: blue;
  }
</style>
