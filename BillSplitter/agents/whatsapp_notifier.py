import os
from dotenv import load_dotenv

load_dotenv()

from twilio.rest import Client
from typing import Dict, List

class WhatsAppNotifierAgent:
    def __init__(self):
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Warning: Twilio credentials not found. Messages will not be sent.")

    def send_notifications(self, splits: dict, user_contacts: Dict[str, str]) -> Dict[str, str]:
        """
        Sends WhatsApp notifications to users.
        
        Args:
            splits: Dictionary of User -> Amount (from SplitResult.user_splits)
            user_contacts: Dictionary of User -> Phone Number (e.g., "+1234567890")
            
        Returns:
            Dictionary of User -> Status ("sent", "failed", "skipped")
        """
        results = {}
        
        for user, amount in splits.items():
            phone = user_contacts.get(user)
            
            if not phone:
                results[user] = "skipped (no phone number)"
                continue
                
            message_body = (
                f"Hello {user}, your share of the wireless bill this month is ${amount:.2f}. "
                "Please pay at your earliest convenience."
            )
            
            try:
                if self.client:
                    message = self.client.messages.create(
                        from_=f"whatsapp:{self.from_number}",
                        body=message_body,
                        to=f"whatsapp:{phone}"
                    )
                    results[user] = f"sent (sid: {message.sid})"
                else:
                    print(f"[Mock Send] To: {phone}, Body: {message_body}")
                    results[user] = "mock_sent"
            except Exception as e:
                results[user] = f"failed ({str(e)})"
                
        return results

if __name__ == "__main__":
    # Test stub
    agent = WhatsAppNotifierAgent()
    splits = {"Alice": 45.50}
    contacts = {"Alice": "+15551234567"} # Replace with real number to test if creds are set
    print(agent.send_notifications(splits, contacts))
