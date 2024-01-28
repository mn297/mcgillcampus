<script context="module" lang="ts">
    export function gaussianRandom() {
        let u = 0,
            v = 0;
        while (u === 0) u = Math.random();
        while (v === 0) v = Math.random();
        return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    export function createHeatmapPoints(courseData) {
        let heatmapData = [];

        courseData.forEach((data) => {
            // Explicitly convert to numbers
            const capacity = parseInt(data.capacity) || 1;
            const lat = Number.parseFloat(data.latitude);
            const lng = Number.parseFloat(data.longitude);

            // Check if the values are indeed numbers
            if (!Number.isNaN(lat) && !Number.isNaN(lng)) {
                // Create the LatLng object
                // const point = new google.maps.LatLng({ lat, lng });

                // If the point is valid, push it to the heatmapData array
                // heatmapData.push(point);
                for (let i = 0; i < capacity; i++) {
                    const offsetLat = lat + gaussianRandom() * 0.0001; // Apply Gaussian dispersion
                    const offsetLng = lng + gaussianRandom() * 0.0001;
                    const point = new google.maps.LatLng(offsetLat, offsetLng);
                    // console.log("point_offset:", point.lat(), point.lng());

                    heatmapData.push(point);
                }
            } else {
                console.error(
                    "Invalid lat/lng values:",
                    data.latitude,
                    data.longitude,
                );
            }
        });

        return heatmapData;
    }
</script>
