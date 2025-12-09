from fastmcp import FastMCP
from dotenv import load_dotenv
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
import os
from .model import (
    GetGroupInformationRequest, 
    GroupInfo, 
    GroupMember, 
    Balance,
    AddExpenseRequest, 
    AddExpenseResponse
)

mcp = FastMCP("Bill Splitter 🚀")

def get_splitwise_client():
    return Splitwise(
        os.environ.get("SPLITWISE_CONSUMER_KEY"),
        os.environ.get("SPLITWISE_CONSUMER_SECRET"),
        api_key=os.environ.get("SPLITWISE_API_KEY")
    )

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
def get_group_information(request: GetGroupInformationRequest) -> GroupInfo:
    """
    Gets information about a Splitwise group.
    """
    sObj = get_splitwise_client()
    
    # 1. Find Group
    target_group = None
    for group in sObj.getGroups():
        if request.group_name_filter.lower() in group.getName().lower():
            target_group = group
            break
            
    if not target_group:
        raise ValueError(f"Group matching '{request.group_name_filter}' not found.")
    
    # Map to Pydantic Model
    members = []
    for m in target_group.getMembers():
        members.append(GroupMember(
            id=m.getId(),
            first_name=m.getFirstName(),
            last_name=m.getLastName(),
            email=m.getEmail() or "",
            registration_status=m.getRegistrationStatus(),
            balance=[
                Balance(amount=float(b.getAmount()), currency_code=b.getCurrencyCode()) 
                for b in m.getBalances()
            ]
        ))
        
    return GroupInfo(
        id=target_group.getId(),
        name=target_group.getName(),
        members=members
    )

def _add_expense_to_splitwise_logic(request: AddExpenseRequest) -> AddExpenseResponse:
    """
    Internal logic for adding an expense.
    """
    sObj = get_splitwise_client()
    
    # 1. Find Group
    target_group = None
    for group in sObj.getGroups():
        if request.group_name_filter.lower() in group.getName().lower():
            target_group = group
            break
            
    if not target_group:
        return AddExpenseResponse(success=False, message=f"Group matching '{request.group_name_filter}' not found.")

    # 2. Prepare Expense
    expense = Expense()
    expense.setCost(str(request.total_amount))
    expense.setDescription(request.description)
    expense.setGroupId(target_group.getId())
    expense.setCurrencyCode("USD")
    
    # 3. Handle Splits
    users = []
    current_user = sObj.getCurrentUser()
    group_members = target_group.getMembers()

    if request.splits:
        # Map emails to Member IDs
        member_map = {m.getEmail(): m.getId() for m in group_members if m.getEmail()}
        
        total_owed_check = 0.0
        
        for email, amount in request.splits.items():
            member_id = member_map.get(email)
            if not member_id:
                 # Check if it's the current user?
                 if email == current_user.getEmail():
                     member_id = current_user.getId()
                 else:
                     return AddExpenseResponse(success=False, message=f"Member {email} not found.")
            
            u = ExpenseUser()
            u.setId(member_id)
            u.setOwedShare(str(amount))
            
            # Who paid?
            # For simplicity, assume Current User paid EVERYTHING.
            if member_id == current_user.getId():
                u.setPaidShare(str(request.total_amount))
            else:
                u.setPaidShare("0.00")
                
            users.append(u)
            total_owed_check += float(amount)
            
        # Validation
        if abs(total_owed_check - request.total_amount) > 0.05:
            return AddExpenseResponse(success=False, message=f"Splits total ({total_owed_check}) does not match expense total ({request.total_amount}).")
            
    else:
        # Equal Split Logic
        num_members = len(group_members)
        if num_members == 0:
             return AddExpenseResponse(success=False, message="Group has no members.")
             
        split_amount = round(request.total_amount / num_members, 2)
        
        # Adjust for rounding errors on the last person
        total_allocated = split_amount * num_members
        remainder = round(request.total_amount - total_allocated, 2)
        
        for i, member in enumerate(group_members):
            u = ExpenseUser()
            u.setId(member.getId())
            
            amount = split_amount
            if i == num_members - 1:
                amount += remainder
                
            u.setOwedShare(str(amount))
            
            # Who paid? Assume Current User paid EVERYTHING.
            if member.getId() == current_user.getId():
                u.setPaidShare(str(request.total_amount))
            else:
                u.setPaidShare("0.00")
            
            users.append(u)

    expense.setUsers(users)

    # 4. Create Expense
    expense, errors = sObj.createExpense(expense)
    
    if errors:
        error_msg = str(errors.getErrors()) if hasattr(errors, 'getErrors') else str(errors)
        return AddExpenseResponse(success=False, message=f"Error creating expense: {error_msg}")
        
    return AddExpenseResponse(success=True, expense_id=expense.getId(), message="Expense created successfully!")

@mcp.tool
def add_expense_to_splitwise(request: AddExpenseRequest) -> AddExpenseResponse:
    """
    Adds an expense to a Splitwise group.
    """
    return _add_expense_to_splitwise_logic(request)
    """
    Adds an expense to a Splitwise group.
    """


if __name__ == "__main__":
    load_dotenv()
    port = int(os.environ.get("MCP_PORT", 8000))
    mcp.run(transport="http", port=port)