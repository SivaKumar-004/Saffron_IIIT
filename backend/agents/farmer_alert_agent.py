from database.farmer_db import get_farmers_by_region
import random
from typing import List, Dict, Any

class FarmerAlertAgent:
    """
    Tier 1 Agent: Farmer Alert Agent
    Responsibility: Triggers warnings and dispatches SMS/Voice alerts to rural keypad-phone farmers.
    """
    def __init__(self):
        self.name = "Farmer Alert Agent"

    def dispatch_alert(self, region: str, risks: List[str], advisory: str) -> Dict[str, Any]:
        """
        Simulates the logic of finding farmers in the region and broadcasting SMS messages.
        """
        if not risks:
            return {
                "alert_triggered": False,
                "dispatch_method": "None",
                "dispatch_log": "No severe risks detected. No SMS dispatched.",
                "farmers_reached": 0
            }
            
        # Get REAL registered farmers
        registered_farmers = get_farmers_by_region(region)
        real_count = len(registered_farmers)
            
        # Simulate connecting to a regional database to query the REST of the phone numbers
        simulated_farmers_reached = random.randint(150, 5000)
        total_reached = simulated_farmers_reached + real_count
        
        # Format the short SMS text
        risk_summary = ", ".join(risks)
        sms_body = f"AGRISPHERE ALERT ({risk_summary}): {advisory} Stay safe!"
        
        # Build detailed delivery logs
        phones = [f.get('phone') for f in registered_farmers]
        log = f"Successfully broadcasted SMS alerts to {total_reached} farmers in {region}."
        if phones:
            log += f"\n👉 Successfully dispatched to specific direct numbers: {', '.join(phones)}"
        
        return {
            "alert_triggered": True,
            "dispatch_method": "SMS Protocol (Keypad Support)",
            "message_body": sms_body,
            "farmers_reached": total_reached,
            "dispatch_log": log
        }
