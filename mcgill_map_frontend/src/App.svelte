<script>
  import Map from "./Map.svelte";
  export let ready;

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
</script>

<svelte:head>
  <script
    defer
    async
    src={`https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`}
  >
  </script>
</svelte:head>

{#if ready}
  <Map></Map>
{/if}
<style>
  :global(body) {
    padding: 0;
  }
</style>
