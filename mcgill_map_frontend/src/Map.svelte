<script lang="ts">
  let container: HTMLElement | null;
  let map: google.maps.Map | undefined;
  let zoom = 16;
  let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
  let markerPosition: google.maps.LatLngLiteral | undefined;
  import { onMount } from "svelte";

  onMount(async () => {
    if (container) {
      map = new google.maps.Map(container, {
        zoom,
        center,
        mapId: "McGillMap",
      });
      const { AdvancedMarkerElement } = (await google.maps.importLibrary(
        "marker"
      )) as google.maps.MarkerLibrary;
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
      const marker = new AdvancedMarkerElement({
        position: markerPosition,
        map: map,
      });
    }
  });
</script>

<div class="full-screen" bind:this={container}></div>

<style>
  .full-screen {
    width: 50vw;
    height: 50vh;
  }
</style>
