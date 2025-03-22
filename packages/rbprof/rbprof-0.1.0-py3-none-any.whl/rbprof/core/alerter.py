import logging

class Alerter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_alert(self, message: str):
        """
        Sends an alert when ransomware is detected.
        """
        self.logger.warning(f"RANSOMWARE ALERT: {message}")