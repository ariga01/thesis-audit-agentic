from dotenv import load_dotenv
import os
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

load_dotenv()

model = "claude-3-5-sonnet-20241022"
model_compiler = 'gemini-2.0-flash-exp'

version = "revenue"
# version = "expenditure"

# target_folder_name = "output\gemini-1.5-flash"
# target_folder_name = "output\gemini-1.5-flash-8b"
# target_folder_name = "output\gemini-1.5-pro"
# target_folder_name = "output\gpt-4o"
# target_folder_name = "output\gpt-4o-mini"
# target_folder_name = "output\llama-3.1-8b"
target_folder_name = "output\llama-3.3-70b"

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.3
)

llm = ChatAnthropic(
    api_key = os.environ['ANTHROPIC_API_KEY'],
    model=model, 
    max_tokens = 4096,
    temperature = 0.3,
    rate_limiter = rate_limiter,
    verbose = True
    )

llm_compiler = ChatGoogleGenerativeAI(
    api_key = os.environ['GOOGLE_API_KEY'],
    model=model_compiler, 
    max_tokens = 8192,
    temperature = 0.3,
    rate_limiter = rate_limiter,
    verbose = True
    )

# Get the current working directory
cwd = os.getcwd()

# Locate the target folder
target_folder = None
for folder in os.scandir(cwd):
    if folder.is_dir() and folder.name == target_folder_name:
        target_folder = folder.path
        break

# Raise an error if the folder is not found
if not target_folder:
    raise FileNotFoundError(f"Folder '{target_folder_name}' not found in the current working directory.")

# Find the single .txt file
txt_files = [f for f in os.listdir(target_folder) if f.endswith('.txt')]

# Ensure there is exactly one .txt file
if len(txt_files) != 1:
    raise ValueError(f"Expected exactly one .txt file in '{target_folder}', found {len(txt_files)}.")

# Get the file path
txt_file_path = os.path.join(target_folder, txt_files[0])

# Read the content of the file
with open(txt_file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if version == "revenue":
    criteria = """
        You are an expert auditor tasked to grade the Audit report given the criteria below.
        1. Each criteria, has one point, which you need to check whether it's TRUE/ FALSE, hence the allowable value is 0/ 1. EXCEPT in defined criteria where 0.5 points is allowed
        2. In total, there are 3 section, with 10 criteria, which results in maximum point of 10
        3. For each criteria, explain your reasoning on why assign such number for the output, whether the output is actually fulfill/ did not fulfill the criteria given.

        Grading Criteria and Setion:
        1. Audit Procedures
        1.1 Check whether the plan try to join the Sales Invoice and Customer tables to identify any sales invoices issued to customers that do not exist in the Customer table, or at least any resemblance on trying to match these
        1.2 Check whether the plan try to join the Sales Invoice and Shipping Log tables to check for any missing records in either table, or at least any resemblance on trying to match these
        1.3 Check whether the plan try to join the Cash Receipt and Sales Invoice tables to identify any cash receipts that are not associated with a corresponding sales invoice, or at least any resemblance on trying to match these
        1.4 Check whether the SQL statement does exist and make sense
        2. Audit Findings
        2.1 Check whether they find Sales Invoice (Left Join) with non existent customer in Customer table, the sales invoice number is 213943 and 214119. IF FOUND ONLY PARTIAL OR MORE THAN ASKED, ASSIGN 0.5 POINTS
        2.2 Check whether they find Sales Invoice (Full Join) without corresponding Shipping Log, the sales invoice is 214022. IF FOUND MORE THAN ASKED, ASSIGN 0.5 POINTS
        2.3 Check whether they find Cash Receipt (Left Join) without corresponding record in the Sales Invoice Table. The Memo Notes number : 12684, 12687, 12814, with Invoice number in the Cash Receipt table : 213418, 213423, 203452, respectively, which they should mention that these invoice number do not exist in the Sales Invoice table. IF FOUND ONLY PARTIAL OR MORE THAN ASKED, ASSIGN 0.5 POINTS
        3. Audit Recommendation
        3.1 They should recommend that the final user should check further the Cash Receipt with nonexistent Sales Invoice number in the Sales Invoice table, of what would be the cause of it
        3.2 They should try to recommend better input control for the case
        3.3 They should assess that the overall existence/ occurance assertions may be in good shape

        Example Output:
        1.1. Points : [0/1] : ; Reasoning : [Reasoning]
        1.2. Points : [0/1] : ; Reasoning : [Reasoning]
        1.3. Points : [0/1] : ; Reasoning : [Reasoning]

        Now assess the human input given
        """
if version == "expenditure":
    criteria = """
        You are an expert auditor tasked to grade the Audit report given the criteria below.
        1. Each criteria, has one point, which you need to check whether it's TRUE/ FALSE, hence the allowable value is 0/ 1. EXCEPT in defined criteria where 0.5 points is allowed
        2. In total, there are 3 section, with 10 criteria, which results in maximum point of 10
        3. For each criteria, explain your reasoning on why assign such number for the output, whether the output is actually fulfill/ did not fulfill the criteria given.

        Grading Criteria and Setion:
        1. Audit Procedures
        1.1 Check whether the plan try to check for gaps, sequence and duplicates in Purchase Order and Receiving Report, or at least any resemblance on trying to match these. If partially true, assign 0.5 point
        1.2 Check whether the plan try to check for duplicates in check number and voucher number in Check Register, or at least any resemblance on trying to match these. If partially true, assign 0.5 point
        1.3 Check whether the plan try to join the Receiving Report with the Purchase Order, to check the completeness assertions, or at least check whether there are any Receiving Report without corresponding Purchase Order, or at least any resemblance on trying to match these. If partially true, assign 0.5 point
        1.4 Check whether the SQL statement does exist and make sense
        2. Audit Findings
        2.1 Check whether they find duplicates, gaps, and sequence problem in Purchase Order and Receiving Report. Which in all case mentioned, do exist. IF FOUND ONLY PARTIAL, ASSIGN 0.5 POINTS
        2.2 Check whether they find duplicate check number and voucher number in Check Register. The check number should not contain duplicates, while the voucher number contain 2 records with one matching voucher number. IF FOUND MORE THAN ASKED, ASSIGN 0.5 POINTS
        2.3 Check whether they find Receiving Report (Left Join) without corresponding Receiving Report Number in the Purchase Order Table. Although the case is that they do have matching PO Number, just that in the Purchase Order table, the Receiving Report number is blank or may be not updated. IF FOUND ONLY PARTIAL  ASSIGN 0.5 POINTS
        3. Audit Recommendation
        3.1 They should recommend that the final user should implement better entry control, as the amount of gaps, sequence problem, and duplicates in the record increase the probability of omitted transactions
        3.2 They should try to check further on records with those aforementioned problem to check the possibility of omission
        3.3 They should assess that the overall completeness assertions may be not ideal

        Example Output:
        1.1. Points : [0/1] : ; Reasoning : [Reasoning]
        1.2. Points : [0/1] : ; Reasoning : [Reasoning]
        1.3. Points : [0/1] : ; Reasoning : [Reasoning]

        Now assess the human input given
        """
    
answers = []
debug = []

messages = [
    (
        "system", criteria,
    ),
    ("human", content),
]

ai_msg = llm.invoke(messages)
print(ai_msg.content)

debug.append(ai_msg.content.strip())

compiler = [
    (
        "system",
        """You are an expert assintant that can do anything.
        1. Given the input from user, return only the number and point being given
        2. You MUST ONLY RETURN NUMBER AND POINTS
        3. The reasoning should be excluded

        Example Output:
        [NUMBER]. [POINTS]
        [NUMBER]. [POINTS]
        [NUMBER]. [POINTS]
        """,
    ),
    ("human", ai_msg.content),
]
ai_msg = llm_compiler.invoke(compiler)
print(ai_msg.content.strip())
answers.append(ai_msg.content.strip())

# Save the answers to {model}Answer.txt
with open(f"{target_folder_name}_Debug_{version}.txt", "w") as debug_file:
        debug_file.write("".join(debug))

# Save the answers to {model}Answer.txt
with open(f"{target_folder_name}_Grade_{version}.txt", "w") as answer_file:
        answer_file.write("".join(answers))