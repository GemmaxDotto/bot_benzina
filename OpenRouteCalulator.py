import requests

class OpenRouteService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
            "Authorization": f"Bearer {api_key}"
        }

    def get_route_length(self, start_coordinates, end_coordinates):
        params = {
            "start": f"{start_coordinates[0]},{start_coordinates[1]}",
            "end": f"{end_coordinates[0]},{end_coordinates[1]}",
            "api_key": self.api_key
        }

        response = requests.get(self.base_url, params=params, headers=self.headers)
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            route_length = data['features'][0]['properties']['segments'][0]['distance']
            return route_length
        else:
            print(f"Errore nella richiesta: {response.status_code}, {response.text}")
            return None