import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import requests


class BadgeChecker:
    def __init__(self) -> None:
        """Initialize BadgeChecker object. Includes initializing Firestore database client and app."""
        # Grabs the credentials from the keys folder and puts them in a special Firebase object.
        cred = credentials.Certificate("keys/weatherboy-firestore.json")
        # Initializes the app with the credentials. This app initialization is required for all 
        # Firebase services and gets reused throughout the program.
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
        doc_ref = self.db.collection("Stations").add(new_station) # can I get the ID from this? prolly not

        # TODO add code to write an initial false check to the Checks collection

        # collection_ref = (
        #         self.db.collection("Stations")
        #         .document(doc_ref.id)
        #         .collection("Checks")
        #     )



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

    def get_badge_status(self) -> list:
        """Get the badge status of all stations from the Wunderground website.

        Returns:
            list: A list of dicts with document IDs, each with sub dicts with 
            the station's badge status and timestamp of the check.
        """
        # Get the stations from the Firestore database.
        stations = self.get_stations() # TODO pass this in instead

        badge_statuses = []

        # Iterate through the stations and check their badge status.
        for station in stations:
            station_id = station["StationID"]
            station_wunderground_url = self.wunderground_url_prefix + station_id
            response = requests.get(station_wunderground_url).text

            if "goldstar" in response:
                has_badge = True
            else:
                has_badge = False

            # Create a dictionary with the document ID for the given station and the
            # badge status (bool and timestamp in a sub dict).
            data = {
                "DocumentID": station["DocumentID"],
                "CurrentStatus": {
                    "HasBadge": has_badge,
                    "TimeStamp": firestore.SERVER_TIMESTAMP,
                },
            }

            # Append this instance of the dictionary to the list.
            badge_statuses.append(data)

        return badge_statuses

    def write_badge_status(self, badge_statuses: list) -> None: #FIXME should be just params not this stupid dict shit
        """Write the badge status of all stations passed in to the method to the Firestore database.

        Args:
            badge_statuses (list): A list of dicts with document IDs, each with sub dicts with 
            the station's badge status and timestamp of the check.
        """
        # Iterate through the badge statuses in the passed in list
        for station in badge_statuses:
            # Reference to the Checks collection for the given station, using the ID contained in the badge status item.
            doc_ref = (
                self.db.collection("Stations")
                .document(station["DocumentID"])
                .collection("Checks")
            )

            # Add the badge status to the Checks collection.
            doc_ref.add(station["CurrentStatus"])

    def query_badge_status(self) -> dict: # FIXME WIP
        """Get the badge status of all stations from the Firestore database.

        Returns:
            list: A list with all stations, which are each sub dicts with the 
            station's badge status and time with badge.
        """
        stations = self.get_stations() # TODO pass this in instead
        for station in stations:
            false_check = None
            true_check = None
            
            collection_ref = (
                self.db.collection("Stations")
                .document(station["DocumentID"])
                .collection("Checks")
            )

            query = (
                collection_ref.where("HasBadge", "==", False)
                .order_by("TimeStamp", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            false_check_docs = query.get()
            
            query = (
                collection_ref.where("HasBadge", "==", True)
                .order_by("TimeStamp", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            true_check_docs = query.get()
            
            if false_check_docs:
                false_check = false_check_docs[0].to_dict()
            
            if true_check_docs:
                true_check = true_check_docs[0].to_dict()

            if (true_check and false_check):
                if true_check["TimeStamp"] > false_check["TimeStamp"]:
                    time = true_check["TimeStamp"] - false_check["TimeStamp"]
                    badge = True
                    print(time, badge)
                elif false_check["TimeStamp"] > true_check["TimeStamp"]:
                    badge = False
                    print(badge)
            elif (not true_check) and (false_check):
                badge = False
                print(badge)
        # get false order by desc time limit 1
        # get true order by desc time limit 1
        # if true > false, then time == time between false and true and badge == true
        # elif false > true, then badge == false
        pass


if __name__ == "__main__":
    checker = BadgeChecker()
    # checker.add_station("123", "John", "Doe")
    # print(checker.get_stations())
    # checker.update_badge_status()
    # checker.remove_station("123")
    # badge_status = checker.get_badge_status()
    # checker.write_badge_status(badge_status)
    checker.query_badge_status()
