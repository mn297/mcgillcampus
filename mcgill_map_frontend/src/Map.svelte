<script lang="ts">
  let container: HTMLElement | null;
  let map: google.maps.Map | undefined;
  let zoom = 16;
  let center: google.maps.LatLngLiteral = { lat: 45.5053, lng: -73.5775 };
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
</script>

<div class="full-screen" bind:this={container}></div>

<style>
  .full-screen {
    width: 100vw;
    height: 100vh;
  }
</style>
