from typing import List, Dict

class BehavioralEngine:
    def __init__(self):
        self.ransomware_patterns = {
            "encrypt": "Ransomware typically encrypts files.",
            "delete_backup": "Ransomware often deletes backups.",
            "modify_master_boot_record": "Ransomware may modify the MBR.",
        }

    def analyze_behavior(self, data: List[Dict]) -> List[Dict]:
        """
        Analyzes behavior for ransomware-like patterns.
        """
        anomalies = []
        for entry in data:
            action = entry.get("action")
            if action in self.ransomware_patterns:
                entry["description"] = self.ransomware_patterns[action]
                anomalies.append(entry)
        return anomalies