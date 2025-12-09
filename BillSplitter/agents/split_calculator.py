from typing import Dict, List, Any
from pydantic import BaseModel

class SplitResult(BaseModel):
    splits: Dict[str, float]
    total_bill: float
    details: Dict[str, Any]
    description: str

class SplitCalculatorAgent:
    def __init__(self):
        pass

    def calculate_split(self, bill_data: dict, user_map: Dict[str, str] = None) -> SplitResult:
        """
        Calculates the split based on bill data.
        
        Args:
            bill_data: The JSON output from BillParserAgent.
            user_map: Optional mapping of User Name -> Email. 
                      If None, uses names found in bill.
        """
        
        total_amount = bill_data.get("total_amount", 0.0)
        shared_costs = bill_data.get("shared_costs", [])
        user_charges = bill_data.get("user_charges", [])
        
        # Calculate total shared cost
        total_shared = sum(item.get("amount", 0.0) for item in shared_costs)
        
        active_users = [u.get("name") for u in user_charges]
        if not active_users:
             pass

        num_users = len(active_users)
        shared_per_user = total_shared / num_users if num_users > 0 else 0
        
        splits = {}
        details = {}
        
        for user in user_charges:
            name = user.get("name")
            user_total = user.get("total", 0.0)
            
            # Add shared portion
            final_amount = user_total + shared_per_user
            
            # Determine key (Email if map provided, else Name)
            key = name
            if user_map:
                phone = user.get("phone_number")
                if phone:
                    email = user_map.get(phone)
                    if email:
                        key = email
                else:
                    # Fallback or warning?
                    # User requested using email_id. If missing, we might want to keep name or skip?
                    # Keeping name is safer to avoid data loss.
                    pass

            splits[key] = round(final_amount, 2)
            details[key] = {
                "individual_charges": user_total,
                "shared_portion": round(shared_per_user, 2),
                "items": user.get("items", [])
            }
            
        return SplitResult(
            splits=splits,
            total_bill=total_amount,
            details=details,
            description=f"Bill for {bill_data.get('period_start', '')} to {bill_data.get('period_end', '')}"
        )

if __name__ == "__main__":
    # Test stub
    sample_data = {
        "total_amount": 100.0,
        "period_end": "2025-12-01",
        "period_start": "2025-11-01",
        "shared_costs": [{"description": "Base Plan", "amount": 20.0, "category": "Plan"}],
        "user_charges": [
            {"name": "Alice", "total": 30.0, "items": []},
            {"name": "Bob", "total": 50.0, "items": []}
        ]
    }
    sample_user_map = {
            "Alice": "alice@example.com",
            "Bob": "bob@example.com"
        }
    agent = SplitCalculatorAgent()
    print(agent.calculate_split(sample_data, sample_user_map))
