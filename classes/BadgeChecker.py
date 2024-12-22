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
            dict = doc.to_dict()
            owner_first_name = dict["OwnerFirstName"]
            station_id = dict["StationID"]

            station_ids[station_id] = owner_first_name

        return station_ids

    def add_station(
        self, station_id: str, owner_first_name: str, owner_last_name: str
    ) -> None:
        """Add a station to the Firestore database.

        Args:
            station_id (str): The station ID.
            owner_first_name (str): The owner's first name.
            owner_last_name (str): The owner's last name.
        """ ""
        pass
        new_station = {
            "StationID": station_id,
            "OwnerFirstName": owner_first_name,
            "OwnerLastName": owner_last_name,
        }

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
            # I guess that with a document, you can call .reference to get the reference to the document which is then used for deletion.
            doc.reference.delete()


if __name__ == "__main__":
    checker = BadgeChecker()
    checker.add_station("123", "John", "Doe")
    print(checker.get_stations())
    checker.remove_station("123")
