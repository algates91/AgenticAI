from typing import Dict, List, Any
from pydantic import BaseModel

class SplitResult(BaseModel):
    user_splits: Dict[str, float]
    total_bill: float
    details: Dict[str, Any]

class SplitCalculatorAgent:
    def __init__(self):
        pass

    def calculate_split(self, bill_data: dict, user_config: Dict[str, List[str]] = None) -> SplitResult:
        """
        Calculates the split based on bill data.
        
        Args:
            bill_data: The JSON output from BillParserAgent.
            user_config: Optional mapping of User Name -> [Phone Numbers]. 
                         If None, uses names found in bill.
        """
        
        total_amount = bill_data.get("total_amount", 0.0)
        shared_costs = bill_data.get("shared_costs", [])
        user_charges = bill_data.get("user_charges", [])
        
        # Calculate total shared cost
        total_shared = sum(item.get("amount", 0.0) for item in shared_costs)
        
        # Identify all users
        # If user_config is provided, we map bill users to config users
        # For simplicity, we'll assume bill_data names match or we just use them.
        
        active_users = [u.get("name") for u in user_charges]
        if not active_users:
             # Fallback if no user charges found, split everything equally?
             # For now, let's assume there are user charges.
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
            
            splits[name] = round(final_amount, 2)
            details[name] = {
                "individual_charges": user_total,
                "shared_portion": round(shared_per_user, 2),
                "items": user.get("items", [])
            }
            
        return SplitResult(
            user_splits=splits,
            total_bill=total_amount,
            details=details
        )

if __name__ == "__main__":
    # Test stub
    sample_data = {
        "total_amount": 100.0,
        "shared_costs": [{"description": "Base Plan", "amount": 20.0, "category": "Plan"}],
        "user_charges": [
            {"name": "Alice", "total": 30.0, "items": []},
            {"name": "Bob", "total": 50.0, "items": []}
        ]
    }
    agent = SplitCalculatorAgent()
    print(agent.calculate_split(sample_data))
