<script lang="ts">
	let container: HTMLElement | null;
	let map: google.maps.Map | undefined;
	let zoom = 16;
	let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
	let markerPosition: google.maps.LatLngLiteral | undefined;
	let searchQuery = "";
	import { onMount } from "svelte";

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
</script>
<div class="date-selector">
    <select>
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
</style>
