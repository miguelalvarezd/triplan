import json
from airportsdata import load
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Load airport data
airports = load("IATA")  # Data keyed by IATA code

# Function to find the nearest airports
def find_nearest_airports(city_name, num_results=3):
    geolocator = Nominatim(user_agent="airport_locator")
    
    # Get city coordinates
    location = geolocator.geocode(city_name)
    if not location:
        return None, f"City '{city_name}' not found."
    city_coords = (location.latitude, location.longitude)

    # Calculate distances
    airport_distances = []
    for code, details in airports.items():
        airport_coords = (details["lat"], details["lon"])
        distance = geodesic(city_coords, airport_coords).km
        airport_distances.append({"code": code, "name": details["name"], "distance_km": distance})

    # Sort and return nearest airports
    nearest = sorted(airport_distances, key=lambda x: x["distance_km"])[:num_results]
    return nearest, None

# Example usage
def report_airports(city_name):
    result, error = find_nearest_airports(city_name)

    if error:
        return (json.dumps({"error": error}, indent=4))
    else:
        output = {
            "city": city_name,
            "nearest_airports": result
        }
        return (json.dumps(output, indent=4))

if __name__ == '__main__':
    city_name = "dgsdag"
    print(report_airports(city_name))