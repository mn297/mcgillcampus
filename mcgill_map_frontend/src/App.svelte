<script lang="ts">
  import Map from "./Map.svelte";
  export let ready;

  import svelteLogo from "./assets/svelte.svg";
  import viteLogo from "/vite.svg";
  import Counter from "./lib/Counter.svelte";
</script>

<svelte:head>
	<script defer async
	src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
	</script>
</svelte:head>

<main>
  <head>
    <title>Simple Map</title>
    <script
      src="https://polyfill.io/v3/polyfill.min.js?features=default"
    ></script>

    <link rel="stylesheet" type="text/css" href="./style.css" />
  </head>
  <body>
    <div id="map"></div>

    <!-- prettier-ignore -->
    <!-- prettier-ignore -->
    <!-- prettier-ignore -->
    <!-- prettier-ignore -->
    <script>
(g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})
        ({key: "YOUR_API_KEY", v: "weekly"});
    </script>
  </body>
</main>

<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
</style>
