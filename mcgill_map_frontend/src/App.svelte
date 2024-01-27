<script>
  import Map from "./Map.svelte";
  export let ready;
</script>

<svelte:head>
  <script
    defer
    async
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCALH7OHHPmgyR8m4dW3j7mJf8PZTfJZD4&callback=initMap"
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
