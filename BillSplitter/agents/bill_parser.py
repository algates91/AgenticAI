import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

class LineItem(BaseModel):
    description: str = Field(description="Description of the charge")
    amount: float = Field(description="Amount of the charge")
    category: str = Field(description="Category of the charge (e.g., Plan, Device, Usage, Tax)")

class UserCharge(BaseModel):
    name: str = Field(description="Name of the user or line owner")
    phone_number: Optional[str] = Field(description="Phone number associated with the line")
    items: List[LineItem] = Field(description="List of charges for this user")
    total: float = Field(description="Total charges for this user")

class BillData(BaseModel):
    total_amount: float = Field(description="Total amount of the bill")
    period_start: str = Field(description="Billing period start date")
    period_end: str = Field(description="Billing period end date")
    usage_period: str = Field(description="Usage period")
    shared_costs: List[LineItem] = Field(description="Shared costs not specific to a user (e.g., account level taxes, base plan)")
    user_charges: List[UserCharge] = Field(description="Charges broken down by user/line")

class BillParserAgent:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=BillData)

    def parse_bill(self, file_path: str) -> dict:
        """Parses a bill file (image or PDF) and returns structured data."""
        
        # TODO: Handle PDF to image conversion if needed, or pass PDF directly if supported
        # For now assuming image path or text content if we extract it first.
        # Gemini 1.5 Pro can handle PDF directly via API but LangChain integration might need specific handling.
        # Let's assume we pass the file as a media block.
        
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if not mime_type:
            raise ValueError("Could not determine mime type of the file")

        with open(file_path, "rb") as f:
            image_data = f.read()

        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract the following information from this bill. Return JSON matching the specified format. Make sure to extract only information associated with phone number & name and total amount should be the total of all charges."},
                {"type": "text", "text": self.parser.get_format_instructions()},
                {"type": "media", "mime_type": mime_type, "data": image_data},
            ]
        )

        response = self.llm.invoke([message])
        json_result = self.parser.parse(response.content)
        return BillData(**json_result)

if __name__ == "__main__":
    # Test code
    import sys
    if len(sys.argv) > 1:
        agent = BillParserAgent()
        try:
            result = agent.parse_bill(sys.argv[1])
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python bill_parser.py <path_to_bill>")
