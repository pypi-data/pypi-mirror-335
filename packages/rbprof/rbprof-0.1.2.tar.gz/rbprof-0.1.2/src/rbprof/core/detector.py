from typing import List, Dict

class Detector:
    def __init__(self):
        self.threshold = 1  # Minimum number of anomalies to trigger detection

    def detect_ransomware(self, anomalies: List[Dict]) -> bool:
        """
        Detects ransomware based on the number of anomalies.
        """
        if len(anomalies) >= self.threshold:
            return True
        return False