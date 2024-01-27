import './app.css'
import App from './App.svelte';

// const app = new App({
//   target: document.getElementById('app'),
// })


const app: App = new App({
  target: document.body,
  props: {
    ready: false,
  },
});

// Assuming `initMap` is part of the global window object
// Extend the Window interface to avoid TypeScript errors
declare global {
  interface Window {
    initMap: () => void;
  }
}

window.initMap = function ready() {
  app.$set({ ready: true });
}

export default app;
