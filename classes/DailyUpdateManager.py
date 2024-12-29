import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class DailyUpdateManager():
    def __init__(self, db: firestore.Client) -> None:
        """_summary_

        Args:
            db (firestore.Client): A firestore database client. Passed in so that there aren't multiple clients.
        """
        pass
    def add_daily_update_channel(self, channel_id: int) -> None: #TODO: Add a check to see if the channel already exists. Raise an exception to be caught by command
        """Add a daily update channel to the Firestore database.

        Args:
            channel_id (str): The channel ID.
        """
        pass

    def remove_daily_update_channel(self, channel_id: int) -> None:
        """Remove a daily update channel from the Firestore database.

        Args:
            channel_id (str): The channel ID.
        """
        pass

    def get_daily_update_channels(self) -> list:
        """Get the daily update channels from the Firestore database.

        Returns:
            list: A list of dicts with the channel IDs and the document IDs.
        """
        pass
