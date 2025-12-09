import os
import json
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Import our existing agents
from agents.bill_parser import BillParserAgent, BillData
from agents.split_calculator import SplitCalculatorAgent
from agents.whatsapp_notifier import WhatsAppNotifierAgent
from agents.splitwise_agent import SplitwiseAgent

load_dotenv()

# 1. Define State
class AgentState(TypedDict):
    bill_file_path: str
    bill_data: Dict[str, Any] # Serialized BillData
    contacts: Dict[str, str] # Email -> Phone (for Notifier)
    phone_map: Dict[str, str] # Phone -> Email (for Calculator)
    splits: Dict[str, float]
    splitwise_expense_id: str
    notification_status: Dict[str, str]
    errors: List[str]

# 2. Define Nodes

def load_config(state: AgentState) -> AgentState:
    print("--- Node: Load Config ---")
    contacts_file = "contacts.json"
    phone_map = {} # Phone -> Email
    email_to_phone = {} # Email -> Phone
    
    if os.path.exists(contacts_file):
        with open(contacts_file, "r") as f:
            raw_contacts = json.load(f)
            # Handle list of dicts
            if isinstance(raw_contacts, list):
                for c in raw_contacts:
                    phone = c.get("phone")
                    email = c.get("email_id")
                    if phone and email:
                        phone_map[phone] = email
                        email_to_phone[email] = phone
            elif isinstance(raw_contacts, dict):
                # Legacy support - assume Name -> Phone, no email?
                # Or maybe Phone -> Email?
                # User said "created from contacts.json" which is list of dicts now.
                pass
    else:
        print(f"Warning: {contacts_file} not found.")
    
    print(f"Loaded {len(phone_map)} contacts.")
    return {"contacts": email_to_phone, "phone_map": phone_map, "errors": []}

def parse_bill(state: AgentState) -> AgentState:
    print("--- Node: Parse Bill ---")
    file_path = state["bill_file_path"]
    agent = BillParserAgent()
    try:
        bill_data_obj = agent.parse_bill(file_path)
        # Convert Pydantic to dict for state serialization
        return {"bill_data": bill_data_obj.dict()}
    except Exception as e:
        return {"errors": state["errors"] + [f"Bill Parser Error: {str(e)}"]}

def calculate_splits(state: AgentState) -> AgentState:
    print("--- Node: Calculate Splits ---")
    if not state.get("bill_data"):
        return {"errors": state["errors"] + ["No bill data found."]}
        
    agent = SplitCalculatorAgent()
    try:
        # Pass phone map to agent
        result = agent.calculate_split(state["bill_data"], state.get("phone_map"))
        return {"splits": result.splits}
    except Exception as e:
        return {"errors": state["errors"] + [f"Split Calculator Error: {str(e)}"]}

def add_to_splitwise(state: AgentState) -> AgentState:
    print("--- Node: Add to Splitwise ---")
    splits = state.get("splits")
    bill_data = state.get("bill_data")
    
    if not splits or not bill_data:
        return {"errors": state["errors"] + ["Missing splits or bill data for Splitwise."]}

    total_amount = bill_data.get("total_amount", 0.0)
    description = f"Wireless Bill for {bill_data.get('usage_period', '')}"
    
    agent = SplitwiseAgent()
    result = agent.add_expense(
        total_amount=total_amount,
        description=description,
        splits=splits
    )
    
    if "expense_id" in result:
        return {"splitwise_expense_id": str(result["expense_id"])}
    else:
        return {"errors": state["errors"] + [f"Splitwise Error: {result.get('error')}"]}

# def send_notifications(state: AgentState) -> AgentState:
#     print("--- Node: Send Notifications ---")
#     splits = state.get("splits")
#     contacts = state.get("contacts") # Now Email -> Phone
    
#     if not splits:
#         return {"errors": state["errors"] + ["No splits to notify."]}
        
#     agent = WhatsAppNotifierAgent()
#     # Agent expects splits keys to match contacts keys.
#     # Since splits are now Emails, and contacts is Email->Phone, this should match perfectly!
#     results = agent.send_notifications(splits, contacts)
#     return {"notification_status": results}

# 3. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("load_config", load_config)
workflow.add_node("parse_bill", parse_bill)
workflow.add_node("calculate_splits", calculate_splits)
workflow.add_node("add_to_splitwise", add_to_splitwise)
# workflow.add_node("send_notifications", send_notifications)

workflow.set_entry_point("load_config")

workflow.add_edge("load_config", "parse_bill")
workflow.add_edge("parse_bill", "calculate_splits")
workflow.add_edge("calculate_splits", "add_to_splitwise")
workflow.add_edge("add_to_splitwise", END)

app = workflow.compile()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python graph.py <bill_path>")
        sys.exit(1)
        
    bill_path = sys.argv[1]
    
    initial_state = {
        "bill_file_path": bill_path,
        "errors": []
    }
    
    print("Starting Graph...")
    for output in app.stream(initial_state):
        for key, value in output.items():
            print(f"Finished Node: {key}")
            # print(f"State Update: {value}")
            
    print("Graph Finished.")
