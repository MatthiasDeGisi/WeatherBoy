import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class BadgeChecker():
    def __init__(self):
        
        # Grabs the credentials from the keys folder and puts them in a special Firebase object.
        cred = credentials.Certificate("keys/weatherboy-firestore.json")
        # Initializes the app with the credentials. This app initialization is required for all Firebase services and gets reused throughout the program.
        self.app = firebase_admin.initialize_app(cred)
        # Initializes the database client.
        self.db = firestore.client()
    
    def get_stations(self):
        stations_ref = self.db.collection("Stations")
        docs = stations_ref.stream() # All the documents in the collection are streamed in.
        
        station_ids = []
        
        # Iterates through the documents and grabs the station ID from each one.
        for doc in docs:
            # Converts the document to a dictionary.
            dict = doc.to_dict() # This could be all one line, but it's split up for readability.
            station_id = dict["StationID"]
            
            station_ids.append(station_id)
        
        return station_ids

if __name__ == "__main__":
    checker = BadgeChecker()
    checker.get_stations()