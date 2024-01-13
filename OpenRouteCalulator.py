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

    def get_route(self, start_coordinates, end_coordinates):
        params = {
            "coordinates": [start_coordinates, end_coordinates],
            "format": "geojson",
            "profile": "driving-car"
        }

        response = requests.post(self.base_url, json=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Errore nella richiesta: {response.status_code}, {response.text}")
            return None
