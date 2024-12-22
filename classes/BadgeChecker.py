import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import requests

from datetime import datetime


class BadgeChecker:
    def __init__(self) -> None:
        """Initialize BadgeChecker object. Includes initializing Firestore database client and app.
        """
        # Grabs the credentials from the keys folder and puts them in a special Firebase object.
        cred = credentials.Certificate("keys/weatherboy-firestore.json")
        # Initializes the app with the credentials. This app initialization is required for all Firebase services and gets reused throughout the program.
        self.app = firebase_admin.initialize_app(cred)
        # Initializes the database client.
        self.db = firestore.client()
        
        self.wunderground_url_prefix = "https://www.wunderground.com/dashboard/pws/"

    def get_stations(self) -> list:
        """Get the station IDs, their corresponding owner names, and document ID from the Firestore database.

        Returns:
            list: List of dicts containing stations and their info.
        """
        # Reference to the Stations collection.
        stations_ref = self.db.collection("Stations")
        # Grabs all the documents from the collection.
        docs = stations_ref.stream()

        # Dictionary to store the station IDs and their corresponding owner names.
        station_ids = []

        # Iterates through the documents and grabs the station ID from each one.
        for doc in docs:
            # Converts the document to a dictionary.
            dict = doc.to_dict()
            # Adds the document ID to the dictionary.
            dict["DocumentID"] = doc.id
            station_ids.append(dict)

        return station_ids

    def add_station(
        self, station_id: str, owner_first_name: str, owner_last_name: str
    ) -> None:
        """Add a station to the Firestore database.

        Args:
            station_id (str): The station ID.
            owner_first_name (str): The owner's first name.
            owner_last_name (str): The owner's last name.
        """
        new_station = {
            "StationID": station_id,
            "OwnerFirstName": owner_first_name,
            "OwnerLastName": owner_last_name,
        }

        # Adds the new station to the Stations collection.
        self.db.collection("Stations").add(new_station)

    def remove_station(self, station_id: str) -> None:
        """Remove a station from the Firestore database.

        Args:
            station_id (str): The station ID.
        """
        # Grabs the document from the Stations collection that matches the station ID. Uses .get() 
        # instead of .stream() because there should be very few documents.
        # I have to use .get() and retrieve the whole document instead of just the reference. This is
        # a limitation of the SDK.
        docs = self.db.collection("Stations").where("StationID", "==", station_id).get()
        
        for doc in docs:
            # I guess that with a document, you can call .reference to get the reference to the document 
            # which is then used for deletion.
            doc.reference.delete()

    def update_badge_status(self) -> None:
        """Check the badge status of all stations, and update the database with results."""
        # Get the stations from the Firestore database.
        stations = self.get_stations()
        
        # Iterate through the stations and check their badge status.
        for station in stations:
            station_id = station["StationID"]
            station_wunderground_url = self.wunderground_url_prefix + station_id
            response = requests.get(station_wunderground_url).text
            
            if "goldstar" in response:
                has_badge = True
            else:
                has_badge = False
            
            # Create a dictionary with the badge status and the timestamp.
            data = {"HasBadge": has_badge, "TimeStamp": firestore.SERVER_TIMESTAMP}
            # Get a reference to the Checks collection of the station.
            doc_ref = self.db.collection("Stations").document(station["DocumentID"]).collection("Checks")
            # Add the badge status dict as a document to the Checks collection.
            doc_ref.add(data)
            
    def get_badge_status(self) -> dict:
        """Get the badge status of all stations from the Firestore database.

        Returns:
            dict: A dict with all stations, which are each sub dicts with the station's badge status and time with badge.
        """
        pass
        
if __name__ == "__main__":
    checker = BadgeChecker()
    # checker.add_station("123", "John", "Doe")
    # print(checker.get_stations())
    # checker.remove_station("123")
    checker.update_badge_status()
