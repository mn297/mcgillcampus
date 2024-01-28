<script>
  import Map from "./Map.svelte";
  export let ready;

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
</script>

<svelte:head>
  <script
    defer
    async
    src={`https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&libraries=visualization`}
  >
  </script>
</svelte:head>
<body>
  <h1 class="text">The McGill Map</h1>
  {#if ready}
    <Map></Map>
  {/if}
</body>

<style>
  :global(body) {
    padding: 0;
  }
  .text {
    font-family: "Bookman", serif;
    font-size: 2rem;
    margin: 0;
    padding: 1rem;
    background-color: red;
    color: white;
  }
</style>
