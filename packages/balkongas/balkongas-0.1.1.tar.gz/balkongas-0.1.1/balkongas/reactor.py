import requests


class Reactor:
    def __init__(self, uuid):
        self.uuid = uuid
        self.data = {}

    def refresh(self):
        response = requests.get(
            f"https://api.balkongas.de/v1/metrics/{self.uuid}/json/latest/"
        )
        response.raise_for_status()
        self.data = response.json()
