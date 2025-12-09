import sys
from graph import load_config, parse_bill, calculate_splits

def test_flow(bill_path):
    print(f"Testing flow with bill: {bill_path}")
    
    # 1. Initialize State
    state = {
        "bill_file_path": bill_path,
        "errors": []
    }
    
    # 2. Run Nodes Sequentially
    state.update(load_config(state))
    if state["errors"]:
        print("Errors after load_config:", state["errors"])
        return

    state.update(parse_bill(state))
    if state["errors"]:
        print("Errors after parse_bill:", state["errors"])
        print("Falling back to MOCK bill data for verification...")
        state["errors"] = [] # Clear errors
        state["bill_data"] = {
            "total_amount": 100.0,
            "period_start": "2025-11-01",
            "period_end": "2025-12-01",
            "shared_costs": [{"description": "Base Plan", "amount": 20.0, "category": "Plan"}],
            "user_charges": [
                {"name": "ANANDRAJ RAVI", "total": 30.0, "items": []}, # Should map to 91anandraj@gmail.com
                {"name": "SRAVYA REKAPALLI", "total": 50.0, "items": []} # Should map to sravyarekapalli1996@gmail.com
            ]
        }

    state.update(calculate_splits(state))
    if state["errors"]:
        print("Errors after calculate_splits:", state["errors"])
        return

    # 3. Print Results
    print("\n--- Split Results ---")
    splits = state.get("splits", {})
    for user, amount in splits.items():
        print(f"{user}: ${amount}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_splits.py <bill_path>")
        sys.exit(1)
    
    test_flow(sys.argv[1])
