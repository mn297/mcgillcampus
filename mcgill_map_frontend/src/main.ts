import App from './App.svelte';
// import { MarkerClusterer } from "@googlemaps/markerclusterer";

interface AppProps {
  ready: boolean;
}

const app = new App({
  target: document.body,
  props: {
    ready: false,
  } as AppProps,
});

declare global {
  interface Window {
    initMap: () => void;
  }
}

window.initMap = function ready() {
  app.$set({ ready: true });
};
export default app;
