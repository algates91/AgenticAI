# Agentic AI Bill Splitter

A robust, multi-agent system designed to automate the tedious process of splitting monthly wireless bills. It leverages **LangGraph** for orchestration, **Google Gemini 2.0 Flash** for intelligent document parsing, and **Model Context Protocol (MCP)** for seamless integration with Splitwise.

## 🚀 Features

*   **📄 Intelligent Parsing**: Extracts detailed usage and charges from PDF bills using Gemini 2.0 Flash.
*   **➗ Smart Splitting**: Automatically calculates individual shares, distributing shared costs (like base plans and taxes) equally while assigning specific usage charges to the correct user.
*   **💸 Splitwise Integration**: Adds expenses directly to a Splitwise group using a custom MCP server.
*   **📱 WhatsApp Notifications**: Sends personalized breakdown notifications to each user via Twilio.
*   **📞 Phone-based Lookup**: Maps users from the bill to their contact details using phone numbers.
*   **🧠 Agentic Workflow**: Orchestrated by LangGraph for reliable state management and error handling.

## 🛠️ Architecture

The system is composed of several specialized agents coordinated by a central graph:

1.  **BillParserAgent**: Reads the PDF and extracts structured data (Pydantic models).
2.  **SplitCalculatorAgent**: Applies logic to split the bill, handling shared vs. individual costs.
3.  **SplitwiseAgent**: Interfaces with the Splitwise MCP server to record the expense.
4.  **WhatsAppNotifierAgent**: Formats and sends messages to users.

## 📋 Prerequisites

*   Python 3.10+
*   **Google Gemini API Key** (for parsing)
*   **Splitwise API Credentials** (Consumer Key, Secret, API Key)
*   **Twilio Account** (SID, Auth Token, WhatsApp Number)

## ⚙️ Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure `fastmcp` is installed for the Splitwise integration.*

3.  **Configure Environment Variables**:
    Create a `.env` file in the `BillSplitter` directory with the following:
    ```env
    GOOGLE_API_KEY=your_gemini_key
    
    SPLITWISE_CONSUMER_KEY=your_key
    SPLITWISE_CONSUMER_SECRET=your_secret
    SPLITWISE_API_KEY=your_api_key
    
    TWILIO_ACCOUNT_SID=your_sid
    TWILIO_AUTH_TOKEN=your_token
    TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
    
    MCP_PORT=8000
    ```

4.  **Set up Contacts**:
    Create a `contacts.json` file. This maps phone numbers found on the bill to Splitwise emails and notification numbers.
    ```json
    [
        {
            "name": "User Name",
            "phone": "123.456.7890", 
            "email_id": "user@example.com"
        },
        ...
    ]
    ```
    *   `phone`: The format must match how it appears on the bill (e.g., dots or dashes).
    *   `email_id`: Used to identify the user in Splitwise.

## 🏃 Usage

### 1. Start the Splitwise MCP Server
The MCP server handles the connection to Splitwise. Run this in a separate terminal:

```bash
python -m splitwise_mcp.mcpServer
```

### 2. Run the Bill Splitter Workflow
Execute the main graph script, providing the path to your PDF bill:

```bash
python graph.py /path/to/your/bill.pdf
```

## 🧪 Testing

You can verify the split logic without sending data to APIs using the verification script:

```bash
python verify_splits.py /path/to/your/bill.pdf
```
