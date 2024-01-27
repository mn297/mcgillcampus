<script lang="ts">
	import { onMount } from "svelte";

	let container: HTMLElement | null;
	let map: google.maps.Map | undefined;
	let zoom = 16;
	let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
	let markerPosition: google.maps.LatLngLiteral | undefined;
	let searchQuery = "";
	let timeValue = 0; // Slider value
	let selectedDay = "Monday"; // Default value

	// Function to convert slider value to time string
	function formatTime(hour) {
		return hour + ":00 " + (hour < 12 ? "AM" : "PM");
	}

	// Hardcoded values for day and time
	const day = "Monday";
	const time = "10:30 AM";
	onMount(async () => {
		if (container) {
			map = new google.maps.Map(container, {
				zoom,
				center,
				mapId: "McGillMap",
			});
			const { AdvancedMarkerElement } = (await google.maps.importLibrary(
				"marker",
			)) as google.maps.MarkerLibrary;

			// test marker position
			try {
				const response = await fetch(
					"http://127.0.0.1:8000/get_lat_long",
				);
				if (response.ok) {
					markerPosition = await response.json();
					console.log("Marker Position:", markerPosition);
				} else {
					console.error(
						"Failed to get marker position:",
						response.statusText,
					);
				}
			} catch (error) {
				console.error("Error:", error);
			}

			// Fetch course data
			try {
				const response = await fetch(
					`http://127.0.0.1:8000/get_data?day=${encodeURIComponent(
						day,
					)}&time=${encodeURIComponent(time)}`,
				);
				if (response.ok) {
					const courseData = await response.json();
					console.log("courseData:", courseData);
					// Process courseData to display on the map
				} else {
					console.error(
						"Failed to get courseData:",
						response.statusText,
					);
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
	// Function to call the API when the slider value changes
	function updateTime() {
		const formattedTime = formatTime(timeValue);
		console.log("Selected Time:", formattedTime);
		// Call the API with the selected time
		// Replace this with your API call
	}

	// Button event handler
	async function handleUpdate() {
		const formattedTime = formatTime(timeValue);
		console.log(
			"Selected Day:",
			selectedDay,
			"Selected Time:",
			formattedTime,
		);

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/get_data?day=${encodeURIComponent(
					selectedDay,
				)}&time=${encodeURIComponent(formattedTime)}`,
			);
			if (response.ok) {
				const courseData = await response.json();
				console.log("Updated courseData:", courseData);
				// Process courseData to display on the map
			} else {
				console.error("Failed to get courseData:", response.statusText);
			}
		} catch (error) {
			console.error("Error:", error);
		}
	}
</script>

<button on:click={handleUpdate}>Update</button>

<div class="time-slider">
	<input
		type="range"
		min="0"
		max="23"
		bind:value={timeValue}
		on:change={updateTime}
	/>
	<p>Selected Time: {formatTime(timeValue)}</p>
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
	.full-screen {
		width: 50vw;
		height: 50vh;
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

	.time-slider {
		position: absolute;
		bottom: 10px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 10;
	}
</style>
