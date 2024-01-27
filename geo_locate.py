# HELPERS FOR GEOLOCATION

import requests


def fetch_coordinates(address):
    """Fetch coordinates (latitude, longitude) for a given address, limited to Montreal Island."""
    # Format the address to include 'Montreal' for location biasing
    full_address = f"{address}, Montreal"

    # URL for Nominatim API with the formatted address
    api_url = f"https://nominatim.openstreetmap.org/search?format=json&q={full_address}"

    try:
        response = requests.get(api_url, headers={"User-Agent": "YourAppName"})
        response.raise_for_status()
        data = response.json()

        if not data:
            print(f"No results found for {address}")
            return None, None

        # Get the first result
        result = data[0]
        latitude = result["lat"]
        longitude = result["lon"]
        return latitude, longitude
    except requests.RequestException as e:
        print(f"Error fetching coordinates for address {address}: {e}")
        return None, None


def get_location_polygon(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "polygon_geojson": 1}
    # https://nominatim.openstreetmap.org/search?q=McGill+University&format=json&polygon_geojson=1
    response = requests.get(url, params=params)

    print(response.url)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Assuming the first result is the desired one
            return data[0].get("geojson")
    return None
