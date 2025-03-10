from crewai import LLM, Agent, Task, Crew
from crewai.tools import tool
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDatabaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from dotenv import load_dotenv
import os
import json
import sqlite3
import pandas as pd
import glob

output_dir = "output"
version = "Revenue"
# version = "Expenditure"

model = "gemini-2.0-flash"

if version == "Revenue":
    location = "input\revenue_cycle_audit"
if version == "Expenditure":
    location = "input\expenditure_cycle_audit"

load_dotenv()

llm = LLM(
    model=f"gemini/{model}",
    api_key = os.environ['GOOGLE_API_KEY'],
    temperature=0.4,
    max_tokens=8192
)

if version == "Revenue":
        question = """        
                Below is the information about the cycle and assertion
                Audit Information :
                Audit Cycle: Revenue cycle
                Audit Assertion: Occurance
                
                Metadata :
                Customer_DB.csv
                Columns:
                Customer_Num: A unique number identifying each customer.
                Name: The name of the customer or business.
                Street: The street address of the customer.
                City: The city where the customer is located.
                State: The state where the customer resides.
                Zip: The ZIP/postal code for the customer's address.
                Credit_Limit: The maximum amount of credit extended to the customer.
                Sales_Rep: The ID of the salesperson assigned to this customer.
                Row Count: 64

                Cash_Receipt.csv
                Columns:
                Amount: The amount received as payment.
                Check_Number: The identification number of the check used for payment.
                Customer_Num: A unique number identifying the customer making the payment.
                Invoice_Number: The number of the invoice being paid.
                Payment_Date: The date the payment was received.
                Remit_Num: A unique remittance number associated with the payment.
                Row Count: 165
                Sample Rows:
                {Amount: 95.2, Check_Number: 14834.98043, Customer_Num: 65003, Invoice_Number: 200000, Payment_Date: '1/10/2004', Remit_Num: 12654}
                {Amount: 1229.1, Check_Number: 6493.156342, Customer_Num: 516372, Invoice_Number: 202284, Payment_Date: '1/11/2004', Remit_Num: 12655}
                {Amount: 3038.1, Check_Number: 16728.81604, Customer_Num: 516372, Invoice_Number: 203065, Payment_Date: '2/1/2004', Remit_Num: 12656}

                Shipping Log (Shipping_Log.csv)
                This dataset records details about shipping activities. Key columns include:
                BOL_Num: Bill of Lading Number, a unique identifier for each shipment.
                Carrier: Name of the shipping carrier (e.g., UPS, FedEx).
                Invoice_Number: The invoice number associated with the shipment.
                Customer_Num: Identifier for the customer receiving the shipment.
                Ship_Date: The date the shipment was sent.

                Sales_Invoice.csv
                File Details:
                Number of rows: 700
                Number of columns: 6
                Columns:
                Invoice_Number: Unique identifier for the sales invoice.
                Customer_Num: Customer number associated with the invoice.
                Amount_Due: Total amount due for the invoice.
                Sales_Date: Date the sale was made.
                Due_Date: Deadline for the payment.
                Remit_Num: Remittance number for payment tracking.
        """
if version == "Expenditure":
        question = """        
                Below is the information about the cycle and assertion
                Audit Information :
                Audit Cycle: Expenditure cycle
                Audit Assertion: Completeness
                
                Metadata :
                Check_Register.csv  
                Columns:  
                Chk_Amnt: The amount of the check issued.  
                Chk_Num: The unique identification number assigned to each check.  
                Pay_Date: The date when the payment was made.  
                Ven_Num: Vendor number, a unique identifier for the vendor receiving the payment.  
                Voucher_Num: Voucher number, a unique identifier associated with the transaction.  
                Row Count: 312  

                Voucher_Pay.csv  
                Columns:  
                Voucher_Num: A unique number identifying the voucher.  
                PO_Num: The purchase order number associated with the voucher.  
                Ven_Num: Vendor number indicating the supplier.  
                Sup_Invce: Supplier invoice number tied to the payment.  
                Full_Amount: Total amount of the payment.  
                Disc_Amnt: Discount amount applied to the payment.  
                Due_Date: The date by which the payment is due.  
                Chk_Num: Check number used for the payment.  

                Vendor_DB.csv  
                Columns:  
                City: City where the vendor is located.  
                Last_Active: Last date the vendor was active.  
                Name: Name of the vendor.  
                Ven_Number: Unique identifier for the vendor.  
                Review_Date: Last review date for the vendor's performance or status.  
                State, Street, Zip: Address information for the vendor.  

                Inventory.csv  
                Columns:  
                Product_Num: Unique number identifying each product.  
                Description: Description of the product (e.g., type, color, or specifications).  
                Unit_Cost: Cost per unit of the product.  
                Sale_Price: Sale price per unit of the product.  
                Quan_On_Hand: Quantity of the product currently available in inventory.  
                Reorder_Point: Minimum stock level at which the product should be reordered.  
                Value_at_Cost: Total value of inventory at unit cost.  
                Market_Value: Total market value of the inventory.  

                Purchase_Order.csv  
                Columns:  
                PO_Num: Purchase order number.  
                Date: Date the purchase order was created.  
                Product: The product being ordered.  
                Quantity: Number of units ordered.  
                Cost: Unit cost of the product.  
                Ext_Cost: Extended cost (quantity multiplied by unit cost).  
                Ven_Num: Vendor number for the supplier.  
                RR_Num: Receiving report number associated with the order.  
                Row Count: 331  

                Receiving_Report.csv  
                Columns:  
                RR_Num: Receiving report number.  
                PO_Num: Purchase order number linked to the received items.  
                Product: The product received.  
                Quantity: Quantity of the product received.  
                Ven_Num: Vendor number associated with the shipment.  
                Rec_Date: Date the items were received.  
                Row Count: 307  
        """

@tool("list_tables")
def list_tables() -> str:
    """List the available tables in the database"""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema(tables: str) -> str:
    """
    Input is a comma-separated list of tables, output is the schema and sample rows
    for those tables. Be sure that the tables actually exist by calling `list_tables` first!
    Example Input: table1, table2, table3
    """
    tool = InfoSQLDatabaseTool(db=db)
    return tool.invoke(tables)

@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute a SQL query against the database. Returns the result"""
    return QuerySQLDatabaseTool(db=db).invoke(sql_query)

interpreter_agent = Agent(
        role="Senior Auditor",
        goal="Given the input from user, make comprehensive and actionable audit plan for IT auditor",
        backstory="""You are a skilled Senior Auditor, 
                celebrated for your ability to make comprehensive and actionable audit plan for the other members given the provided information""",
        human_input=True,
        max_iter=5,
        max_rpm=20,
	max_tokens=4000,
        cache=True,
        llm=llm
)
interpret_task = Task(
        description="""
        You need to do the following action in one step, and should not request additional information

        You need to make actionabe plan for the IT Auditor, in the following guidelines:
        1. Understand the specific audit cycle and assertion that are being asked
        2. Read the metadata and understand how each file and column can relate to each other in planning the audit plan
        3. Make specific and concise audit plan to be carried out by Senior IT Auditor, including the SQL statement,so it can effectively use SQL query to analyze the dataset
        4. Set specific rule and criteria, given the audit cycle and assertion
        5. Show the output in 'result' variable

        Below is the information about the cycle, assertion, and metadata:
        {problem}
        """,
        expected_output="Provide a concise and clear actionable and SQL statement for an IT auditor. Ensure it includes explicit criteria for audit goal.",
        agent=interpreter_agent
)

analyzer_agent = Agent(
    role="Senior IT Auditor",
	goal="""Given the information provided by Senior Auditor, analyze the targeted dataset to achieve the audit goal.""",
	backstory="""You are a senior Senior IT Auditor with extensive experience in software and its best practices.
            	You have expertise in analyzing dataset given the criteria and goals using SQL Query""",
	human_input=True,
    max_iter=8,
    max_rpm=20,
	max_tokens=4000,
    cache=True,
    llm=llm,
    tools=[list_tables, tables_schema, execute_sql]
)
analyzer_task = Task(
	description="""
                    You need to do this in sequence:
                    1. Read and understand the specific audit plan by Senior Auditor
                    2. Read the SQL Query based on the provided information and audit plan
                    3. Execute the SQL Query one by one
                    4. Make sure to limit the output first before implementing no limit condition, to reduce token for the context window
                    5. List the findings and write it for the next agent to be for the audit report
                    """,
	expected_output="Analysis of the dataset to achieve the audit goal. output of the analysis should be assigned to the 'result' variable",
	agent=analyzer_agent
)

report_agent = Agent(
    role="Audit Report Manager",
	goal="Create comprehensive and compelling audit reports that provide clear insights and actionable recommendations.",
	backstory="""You are a renowned Manager Auditor, celebrated for your ability to produce insightful and impactful audit reports. 
    Your reports distill complex audit findings into clear, accessible, and actionable insights, making them highly valuable to stakeholders.""",
	human_input=True,
    max_iter=1,
    max_rpm=10,
	max_tokens=4000,
    cache=True,
    llm=llm
)
report_task = Task(
    description="""Using the python dataset analysis results provided by the IT Auditor Team, write an engaging and comprehensive audit report.
        Your report should be:
        - Informative and accessible to a non-technical audience.
        - Clear and concise, avoiding complex jargon to ensure readability.
        - Comprehensive, covering the audit procedures and associated audit findings.
        
        Your report should include:
        - A brief introduction that provides context for the audit.
        - A detailed description of the performed audit procedures.
        - A thorough presentation of the obtained audit findings, including payment details.
        - Actionable recommendations based on the findings.
        - A final conclusion that summarizes the key points and implications.
        
        The goal is to create a report that effectively communicates the audit findings and provides valuable insights to stakeholders. 
        As the report-writing expert, you are responsible for producing this report without requesting additional information. Utilize the provided data and insights to complete your task effectively.""",
	expected_output='A full audit report presented in a clear and accessible manner.',
	agent=report_agent
)

answers = []
usage_metadata = []

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect("database.db")

# List all CSV files in the directory
csv_files = glob.glob(f"{location}/*.csv")  # Replace with your CSV folder path

for file in csv_files:
    # Create a unique table name based on the file name (without the extension)
    table_name = os.path.splitext(os.path.basename(file))[0]
    
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file)
    
    # Write the DataFrame to the database
    df.to_sql(name=table_name, con=connection, if_exists="replace", index=False)
    print(f"Table '{table_name}' created from '{file}'.")

db = SQLDatabase.from_uri("sqlite:///database.db")

analysis_crew = Crew(
	agents=[interpreter_agent, analyzer_agent, report_agent],
	tasks=[interpret_task, analyzer_task, report_task],
    max_rpm=20,
	max_tokens=4000,
    cache=True,
	verbose=True
)

inputs = {'problem': f""" {question}"""}
result = analysis_crew.kickoff(inputs=inputs)
connection.close()

usage_planner = result.token_usage
usage_metadata.append(str(usage_planner))
answers.append(str(result.raw))

os.makedirs(output_dir, exist_ok=True)

# Save answers
answers_file_path = os.path.join(output_dir, f"{model}_Report_{version}.txt")
with open(answers_file_path, "w") as answer_file:
    answer_file.write("\n".join(answers))

# Save usage metadata
usage_file_path = os.path.join(output_dir, f"{model}_Usage_{version}.txt")
with open(usage_file_path, "w") as usage_file:
    for metadata in usage_metadata:
        usage_file.write(json.dumps(metadata) + "\n")

print(f"Answers saved to: {answers_file_path}")
print(f"Usage metadata saved to: {usage_file_path}")