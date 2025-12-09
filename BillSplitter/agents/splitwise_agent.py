from typing import Dict, Any, Optional
from splitwise_mcp.model import AddExpenseRequest, AddExpenseResponse
from dotenv import load_dotenv
# We import the function directly for now as per plan, 
# but in a real MCP setup this might be an RPC call.
from splitwise_mcp.mcpServer import _add_expense_to_splitwise_logic as add_expense_to_splitwise

class SplitwiseAgent:
    def __init__(self):
        pass

    def add_expense(self, 
                    total_amount: float, 
                    description: str, 
                    splits: Dict[str, float], 
                    group_name_filter: str = "at&t") -> Dict[str, Any]:
        """
        Adds an expense to Splitwise using the MCP tool.

        Args:
            total_amount: Total cost of the bill.
            description: Description for the expense.
            splits: Dictionary of Email -> Amount.
            group_name_filter: Group name to search for (default: "at&t").

        Returns:
            Dict containing 'expense_id' on success, or 'error' on failure.
        """
        
        # Validate inputs
        if not splits:
            return {"error": "No splits provided."}
            
        req = AddExpenseRequest(
            total_amount=total_amount,
            description=description,
            group_name_filter=group_name_filter,
            splits=splits
        )

        try:
            response: AddExpenseResponse = add_expense_to_splitwise(req)
            if response.success:
                return {"expense_id": response.expense_id}
            else:
                return {"error": response.message}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

if __name__ == "__main__":
    # Test stub
    load_dotenv()
    agent = SplitwiseAgent()
    # Mock data - this will likely fail without real credentials/group, 
    # but verifies import and structure.
    print(agent.add_expense(100.0, "Test Bill", {"91anandraj@gmail.com": 100.0}))
