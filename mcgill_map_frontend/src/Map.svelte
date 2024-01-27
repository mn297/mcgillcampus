<script lang="ts">
	import { onMount } from "svelte";

	let container: HTMLElement | null;
	let map: google.maps.Map | undefined;
	let zoom = 16;
	let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
	let searchQuery = "";

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
			let initialPosition: google.maps.LatLngLiteral = {
				lat: 45.50741936700414,
				lng: -73.5791031897402,
			};
			const marker = new AdvancedMarkerElement({
				position: initialPosition,
				map: map,
			});
		}
	});
	function handleSearch() {
		console.log("Search query:", searchQuery);
		// Future implementation: Use searchQuery to perform a search
	}
</script>

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
		width: 100vw;
		height: 100vh;
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
