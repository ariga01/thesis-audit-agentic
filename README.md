# Agentic Framework for Auditing Data with CrewAI

**Description:** This project utilizes the CrewAI framework to automate audit procedures on datasets, specifically focusing on revenue and expenditure cycles. It employs a multi-agent system to interpret audit requirements, analyze data through SQL queries, and generate comprehensive audit reports.

## Files

### `agentic.py`

**Description:** Main script that orchestrates the audit process using CrewAI agents. It sets up the agents, tasks, and crew, connects to an SQLite database, performs the audit, and saves the results.

**Details:**

-   Defines agents with specific roles: Senior Auditor, Senior IT Auditor, and Audit Report Manager.
-   Creates tasks for each agent: interpreting audit requirements, analyzing data with SQL, and generating reports.
-   Uses tools for database interaction: listing tables, fetching schema, and executing SQL queries.
-   Handles data loading from CSV files into an SQLite database.
-   Executes the audit process using a CrewAI crew.
-   Saves the audit report and usage metadata to specified output directories.

**Dependencies:**

-   `crewai`
-   `langchain_community`
-   `python-dotenv`
-   `sqlite3`
-   `pandas`
-   `glob`
-   `langchain_google_genai`
-   `langchain_anthropic`

**Environment Variables:**

-   `GOOGLE_API_KEY`

### `eval.py`

**Description:** Evaluation script that assesses the generated audit reports based on predefined criteria. It uses a language model (Claude-3-5-sonnet) to grade the reports.

**Details:**

-   Loads environment variables and sets up language models (Claude and Gemini).
-   Locates the output directory and reads the generated audit report.
-   Defines grading criteria based on the audit cycle (revenue or expenditure).
-   Invokes the language model to assess the report against the criteria.
-   Uses a compiler LLM (gemini) to extract only grade numbers from grader LLM (claude).
-   Saves the grading results and debug information to files.

**Dependencies:**

-   `python-dotenv`
-   `langchain_core`
-   `langchain_google_genai`
-   `langchain_anthropic`

**Environment Variables:**

-   `ANTHROPIC_API_KEY`
-   `GOOGLE_API_KEY`

## Setup

1.  **Install required packages:**

    ```bash
    pip install crewai langchain_community python-dotenv pandas sqlite3 glob langchain_google_genai langchain_anthropic
    ```

2.  **Set up environment variables:** Create a `.env` file and add your `GOOGLE_API_KEY` and `ANTHROPIC_API_KEY`.

3.  **Place input CSV files:** Place input CSV files in the appropriate directory (`input/revenue_cycle_audit` for revenue, `input/expenditure_cycle_audit` for expenditure).

4.  **Run the main script:**

    ```bash
    python agentic.py
    ```

5.  The script will create a `database.db`, load CSV files, and generate audit reports and usage information in the output directory.

6.  **Evaluate the report:** Run `python eval.py` (after setting appropriate variables in the file).

7.  The result of evaluation will be located on current working directory, as `{target_folder_name}_Debug_{version}.txt` and `{target_folder_name}_Grade_{version}.txt`

## Usage

-   **Revenue Cycle Audit:** To audit the revenue cycle, ensure CSV files related to customers, cash receipts, shipping logs, and sales invoices are placed in the `input/revenue_cycle_audit` directory.
-   **Expenditure Cycle Audit:** To audit the expenditure cycle, place CSV files related to check registers, voucher payments, vendor databases, inventory, purchase orders, and receiving reports in the `input/expenditure_cycle_audit` directory.
-   **Model Compiler Used:** `gemini-2.0-flash-exp`. To change the model used by compiler LLM, you may edit the variable `model_compiler` on `eval.py`
-   **Target Folder Name:** `output/llama-3.3-70b`. To change the target folder used by the eval, you may edit the variable `target_folder_name`, and make sure to put the folder in the correct location.

## Notes

-   The code is set up to use Gemini models for the main audit process and Claude for evaluation.  You can customize the models by modifying the `model` variable in each script.
-   Rate limiting is implemented using `InMemoryRateLimiter`. Adjust the `requests_per_second` parameter as needed based on your API usage limits.
-   The output directory can be changed using the `output_dir` variable.
-   Human input is enabled for all agents and can be set to `False` to disable it.
