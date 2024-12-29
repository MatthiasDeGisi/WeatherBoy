import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import requests


class BadgeChecker:
    def __init__(self, db: firestore.Client) -> None:
        """Initialize the BadgeChecker object.

        Args:
            db (firestore.Client): A Firestore database client. Passed in so that there aren't multiple clients.
        """
        # Sets the firestore database client, which is passed in when the object is created.
        self.db = db

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

    def add_station( #TODO: Add a check to see if the station already exists. Raise an exception to be caught by command
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
        doc_ref = self.db.collection("Stations").add(new_station)
        # This has to be a list because thats what the write_badge_status method expects.
        badge_status = [
            {
                "DocumentID": doc_ref[
                    1
                ].id,  # Need to use [1] because doc_ref is a tuple with the document reference and the ID.
                "CurrentStatus": {
                    "HasBadge": False,
                    "TimeStamp": firestore.SERVER_TIMESTAMP,
                },
            }
        ]
        self.write_badge_status(badge_status)

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

    def scrape_badge_status(self) -> list:
        """Scrape the badge status of all stations from the Wunderground website.

        Returns:
            list: A list of dicts with document IDs, each with sub dicts with
            the station's badge status and timestamp of the check.
        """
        # Get the stations from the Firestore database.
        stations = self.get_stations()  # TODO pass this in instead

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

    def write_badge_status(self, badge_statuses: list) -> None:
        """Write the badge status of all stations passed in to the method to the Firestore database.

        Args:
            badge_statuses (list): A list of dicts with document IDs, each with sub dicts with
            the station's badge status and timestamp of the check.
        """
        # Iterate through the badge statuses in the passed in list
        for station in badge_statuses:
            # Reference to the Checks collection for the given station, using the
            # ID contained in the badge status item.
            doc_ref = (
                self.db.collection("Stations")
                .document(station["DocumentID"])
                .collection("Checks")
            )

            # Add the badge status to the Checks collection.
            doc_ref.add(station["CurrentStatus"])

    def get_badge_status(self) -> dict:
        """Get the badge info of all stations from the Firestore database.

        Returns:
            list: A list with all stations, which are each sub dicts with the
            station's badge info and optionally time with badge.
        """
        stations = self.get_stations()  # TODO pass this in instead (???)
        badge_info = []

        for station in stations:

            # True check may not be there, so it is reset every iteration.
            true_check = None

            # Dictionary to store the station's badge info.
            station_badge_info = {}
            station_badge_info["StationID"] = station["StationID"]
            station_badge_info["OwnerFirstName"] = station["OwnerFirstName"]

            # Reference to the Checks collection for the given station.
            collection_ref = (
                self.db.collection("Stations")
                .document(station["DocumentID"])
                .collection("Checks")
            )

            # Query to get the most recent false check.
            query = (
                collection_ref.where("HasBadge", "==", False)
                .order_by("TimeStamp", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            false_check_docs = query.get()

            # Query to get the most recent true check.
            query = (
                collection_ref.where("HasBadge", "==", True)
                .order_by("TimeStamp", direction=firestore.Query.DESCENDING)
                .limit(1)
            )
            true_check_docs = query.get()

            # There will always be a false check, but there may not be a true check.
            # Have to use [0] because the query returns a list of documents, and
            # I only expect one doc to be returned.
            false_check = false_check_docs[0].to_dict()
            if true_check_docs:
                true_check = true_check_docs[0].to_dict()

                # If the true check exists and is more recent than the false check (therefore
                # they currently have the badge), calculate the time between the two.
                if true_check["TimeStamp"] > false_check["TimeStamp"]:
                    time_with_badge = true_check["TimeStamp"] - false_check["TimeStamp"]
                    has_badge = True
                    # Add the time with badge to the station's badge info.
                    station_badge_info["TimeWithBadge"] = time_with_badge

                # If the false check is more recent than the true check, they do not have the badge.
                elif false_check["TimeStamp"] > true_check["TimeStamp"]:
                    has_badge = False

            # If there is no true check, they do not have the badge.
            elif (not true_check) and (false_check):
                has_badge = False

            # Add the station's badge info to the station's dict.
            station_badge_info["HasBadge"] = has_badge
            badge_info.append(station_badge_info)

        return badge_info

if __name__ == "__main__":
    checker = BadgeChecker()
    # checker.add_station("123", "John", "Doe")
    # print(checker.get_stations())
    # checker.update_badge_status()
    # checker.remove_station("123")
    # badge_status = checker.get_badge_status()
    # checker.write_badge_status(badge_status)
    # print(checker.query_person_badge_status())
