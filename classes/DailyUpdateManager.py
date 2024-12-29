from classes import BadgeChecker

import datetime

class DailyUpdateManager(BadgeChecker):
    def __init__(self):
        """Initializes the DailyUpdateManager class."""
        super().__init__()
        self.daily_update_time = datetime.time(9, 0)
    
    def add_daily_update_channel(self, channel_id: int):
        """Add a channel to the daily update list.

        Args:
            channel_id (int): The ID of the channel to add.
        """
        pass
    
    def remove_daily_update_channel(self, channel_id: int):
        """Removes a channel from the daily update list.

        Args:
            channel_id (int): The ID of the channel to remove.
        """
        pass
    
    def set_daily_update_time(self, time: datetime.time):
        """Set the time for the daily update.

        Args:
            time (datetime.time): The time to set.
        """
        self.daily_update_time = time
    
    def get_daily_update_time(self) -> datetime.time:
        """Get the time for the daily update.

        Returns:
            datetime.time: The time for the daily update.
        """
        return self.daily_update_time