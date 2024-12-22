import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class BadgeChecker:
    def __init__(self):

        # Grabs the credentials from the keys folder and puts them in a special Firebase object.
        cred = credentials.Certificate("keys/weatherboy-firestore.json")
        # Initializes the app with the credentials. This app initialization is required for all Firebase services and gets reused throughout the program.
        self.app = firebase_admin.initialize_app(cred)
        # Initializes the database client.
        self.db = firestore.client()

    def get_stations(self) -> dict:
        """Get the station IDs and their corresponding owner names from the Firestore database.

        Returns:
            dict: Dictionary with the station IDs as keys and the owner names as values.
        """
        # Reference to the Stations collection.
        stations_ref = self.db.collection("Stations")
        # Grabs all the documents from the collection.
        docs = stations_ref.stream()

        # Dictionary to store the station IDs and their corresponding owner names.
        station_ids = {}

        # Iterates through the documents and grabs the station ID from each one.
        for doc in docs:
            # Converts the document to a dictionary.
            dict = (
                doc.to_dict()
            ) 
            owner_first_name = dict["OwnerFirstName"]
            station_id = dict["StationID"]

            station_ids[station_id] = owner_first_name

        return station_ids

    def add_station(self, station_id: str, owner_name: str) -> None:
        """Add a station to the Firestore database.

        Args:
            station_id (str): The station ID.
            owner_name (str): The owner's name.
        """
        pass
    
    def remove_station(self, station_id: str) -> None:
        """Remove a station from the Firestore database.

        Args:
            station_id (str): The station ID.
        """
        pass
    
    
if __name__ == "__main__":
    checker = BadgeChecker()
    print(checker.get_stations())
