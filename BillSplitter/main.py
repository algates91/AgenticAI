import os
import sys
import json
from dotenv import load_dotenv
from agents.bill_parser import BillParserAgent
from agents.split_calculator import SplitCalculatorAgent
from agents.whatsapp_notifier import WhatsAppNotifierAgent

# Load environment variables
load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_bill_file>")
        sys.exit(1)

    bill_path = sys.argv[1]
    
    if not os.path.exists(bill_path):
        print(f"Error: File not found at {bill_path}")
        sys.exit(1)

    print(f"--- Starting Bill Splitter Agentic System ---")
    print(f"Processing file: {bill_path}")

    # 1. Initialize Agents
    parser_agent = BillParserAgent()
    calculator_agent = SplitCalculatorAgent()
    notifier_agent = WhatsAppNotifierAgent()

    # 2. Parse Bill
    print("\n[1/3] Parsing Bill...")
    try:
        bill_data = parser_agent.parse_bill(bill_path)
        print("Bill parsed successfully.")
        # print(json.dumps(bill_data, indent=2)) # Debug
    except Exception as e:
        print(f"Error parsing bill: {e}")
        sys.exit(1)

    # 3. Calculate Splits
    print("\n[2/3] Calculating Splits...")
    # TODO: Load user config from a file or env. For now, we'll infer from bill or use a dummy map.
    # In a real app, we'd have a mapping of Name -> Phone.
    # Let's try to load a 'contacts.json' if it exists, otherwise prompt or warn.
    
    contacts = {}
    contacts_file = "contacts.json"
    if os.path.exists(contacts_file):
        with open(contacts_file, "r") as f:
            contacts = json.load(f)
    else:
        print(f"Warning: {contacts_file} not found. Notifications might fail if phone numbers are missing.")
        # Create a dummy contacts file for the user to fill
        with open(contacts_file, "w") as f:
            json.dump({"Alice": "+1234567890", "Bob": "+0987654321"}, f, indent=2)
        print(f"Created template {contacts_file}. Please update it with real numbers.")

    split_result = calculator_agent.calculate_split(bill_data, contacts)
    print("Splits calculated:")
    print(json.dumps(split_result.user_splits, indent=2))

    # 4. Notify Users
    print("\n[3/3] Sending Notifications...")
    # Ask for confirmation before sending?
    confirm = input("Send WhatsApp notifications? (y/n): ")
    if confirm.lower() == 'y':
        results = notifier_agent.send_notifications(split_result.user_splits, contacts)
        print("Notification Results:")
        print(json.dumps(results, indent=2))
    else:
        print("Skipping notifications.")

    print("\n--- Process Complete ---")

if __name__ == "__main__":
    main()
