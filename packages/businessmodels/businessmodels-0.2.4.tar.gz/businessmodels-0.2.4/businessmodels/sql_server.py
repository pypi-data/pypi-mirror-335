from datetime import datetime

class QAmodels:
    def __init__(self, schema):
        self.schema = schema  # Store schema as an instance attribute

    def enhancement_prompt(self, user_question, prompt_instructions=""):
        """
        Enhances the user's query by adding relevant schema details, instructions, and the current date.
    
        IMPORTANT:
        - "Last quarter" without a year refers to the current quarter
        - "Last quarter of YYYY" refers to Q4 of FY YYYY-(YYYY+1), which is Jan-Mar of (YYYY+1)
        """
        # Use the current date
        current_date = datetime.now().strftime('%Y-%m-%d')
 
        # Extract year and month from current date
        current_datetime = datetime.now()
        current_year = current_datetime.year
        current_month = current_datetime.month
    
        # Determine the current financial year
        current_fy_start_year = current_year if current_month >= 4 else current_year - 1
        current_fy_end_year = current_fy_start_year + 1
    
        # Determine the current quarter within the financial year
        if 4 <= current_month <= 6:
            current_quarter = 1
        elif 7 <= current_month <= 9:
            current_quarter = 2
        elif 10 <= current_month <= 12:
            current_quarter = 3
        else:  # 1 <= current_month <= 3
            current_quarter = 4
    
        # Define exact date ranges for current and previous year quarters
        if current_quarter == 1:
            current_quarter_start = f"{current_fy_start_year}-04-01"
            current_quarter_end = f"{current_fy_start_year}-06-30"
            prev_year_quarter_start = f"{current_fy_start_year-1}-04-01"
            prev_year_quarter_end = f"{current_fy_start_year-1}-06-30"
        elif current_quarter == 2:
            current_quarter_start = f"{current_fy_start_year}-07-01"
            current_quarter_end = f"{current_fy_start_year}-09-30"
            prev_year_quarter_start = f"{current_fy_start_year-1}-07-01"
            prev_year_quarter_end = f"{current_fy_start_year-1}-09-30"
        elif current_quarter == 3:
            current_quarter_start = f"{current_fy_start_year}-10-01"
            current_quarter_end = f"{current_fy_start_year}-12-31"
            prev_year_quarter_start = f"{current_fy_start_year-1}-10-01"
            prev_year_quarter_end = f"{current_fy_start_year-1}-12-31"
        else:  # current_quarter == 4
            current_quarter_start = f"{current_fy_end_year}-01-01"
            current_quarter_end = f"{current_fy_end_year}-03-31"
            prev_year_quarter_start = f"{current_fy_end_year-1}-01-01"
            prev_year_quarter_end = f"{current_fy_end_year-1}-03-31"

        enhancement_prompt = f"""
    You are a highly skilled SQL expert and data analyst. Your task is to enhance a given user question
    by making it more structured, detailed, and aligned with the provided schema and prompt instructions.
   
    Today's Date: {current_date}
    Schema: {self.schema}
    Prompt Instructions: {prompt_instructions}
    User Question: {user_question}
   
    CRITICAL INFORMATION ABOUT DATE INTERPRETATIONS:
   
    The organization follows an April-March financial year structure:
    - Financial Year X-Y runs from April 1 of year X to March 31 of year Y
    - The current financial year is FY {current_fy_start_year}-{current_fy_end_year}
    - The current quarter is Q{current_quarter} of FY {current_fy_start_year}-{current_fy_end_year}
   
    The quarters in each financial year are defined as:
    - Q1: April 1 to June 30
    - Q2: July 1 to September 30
    - Q3: October 1 to December 31
    - Q4: January 1 to March 31
   
    EXPLICIT DATE MAPPINGS FOR TODAY ({current_date}):
    - "Last quarter" or "current quarter" refers to: {current_quarter_start} to {current_quarter_end}
    - "Previous year's quarter" refers to: {prev_year_quarter_start} to {prev_year_quarter_end}
    - "Last quarter 2024" specifically refers to: {current_quarter_start} to {current_quarter_end}
    - "Last quarter 2023" specifically refers to: Q4 of FY 2023-2024, which is January 1, 2024 to March 31, 2024
    
    IMPORTANT TERMINOLOGY RULES:
    1. "Last quarter" without specifying a year ALWAYS refers to the current quarter we are in right now.
       EXAMPLE: Today is {current_date}, so "last quarter" means {current_quarter_start} to {current_quarter_end}.
    
    2. "Last quarter of YYYY" or "last quarter YYYY" ALWAYS refers to Q4 of FY YYYY-(YYYY+1), which is January-March of (YYYY+1).
       EXAMPLE: "Last quarter of 2024" MUST be interpreted as January 1, 2025 to March 31, 2025.
       EXAMPLE: "Last quarter of 2023" MUST be interpreted as January 1, 2024 to March 31, 2024.
    
    3. When comparing to "previous year", ALWAYS compare the same quarter of the previous financial year.
       EXAMPLE: If we're looking at {current_quarter_start} to {current_quarter_end}, 
       then "previous year" means {prev_year_quarter_start} to {prev_year_quarter_end}.
    
    4. SAP data in this organization is organized by financial year where April is period 1, May is period 2, etc.
   
    For the specific query "{user_question}", you MUST interpret:
    - "Last quarter 2024" as {current_quarter_start} to {current_quarter_end} (Q4 of FY 2024-2025)
    - "Previous year" as {prev_year_quarter_start} to {prev_year_quarter_end} (Q4 of FY 2023-2024)
   
    Transform the user's question into a clear analysis plan using plain text only. Do not use markdown, bullets, or numbering. Format your response as follows:
 
    "Analysis Plan: [Restate the core question in specific terms, clearly specifying the exact date ranges]
    Data needed: [List the specific tables and fields required]
    Time periods: [Define exact date ranges with specific months and years - be very explicit]
    Calculations: [Specify exact formulas for all metrics mentioned]
    Filters: [Define precise filtering conditions]
    Sorting: [Specify the order of results]"
   
    Keep your response simple, clear, and in plain text format. Focus on making vague terms specific and defining precise calculations.
 
    Note: - For consumption calculations, only consider records where SHKZG = 'H'. (Important)
          - For procurement or supply calculations, only consider recods where SHKZG='S'.(Important)
          - For inventory calculation, consider both 'S' = Addition (positive MENGE) and 'H' = Deduction (negative MENGE). (Important)
          - For invoice number, purchase order number, vendor number and financial year take XBLNR_MKPF, EBELN, LIFNR, and BUDAT_MKPF columns from mseg table. (Important)
          - If a user asks about duplicate invoice number always filter BWART = 105. (Important)
          - Convert the datatype of BUDAT_MKPF from 'YYYYMMDD' to 'YYYY-MM-DD'. (Important)
          
    """
        return enhancement_prompt

    def sql_prompt(self, enhanced_question):
        """
        Generate the SQL prompt for OpenAI based on the user question.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        sql_prompt = f"""
You are a highly skilled SQL expert and data analyst specializing in Fabric SQL database environments. Generate an optimized SQL Server-compatible query strictly using only the tables mseg (Material Document Segment) and mbewh (Material Valuation History) from the database schema.
Enhanced User Question: {enhanced_question}
Today's date is: {current_date}

Table Reference Rules:
- Columns from mseg:
  - MATNR (Material Number, nvarchar(max))
  - BUDAT_MKPF (Posting Date, bigint)
  - SHKZG (Debit/Credit Indicator, nvarchar(max))
  - MENGE (Quantity, float)
  - LIFNR (Vendor Number, nvarchar(max))
  - EBELN (Purchase Order No., bigint)
  - MAA_URZEI (Origin Indicator, bigint)
  - BWART (Movement Type, bigint)
  - WERKS (Plant, bigint)
  - LGORT (Storage Location, nvarchar(max))
  - CHARG (Batch Number, nvarchar(max))
  - XBLNR_MKPF (Invoice Number, nvarchar(max))
- Columns from mbewh:
  - MATNR (Material Number, nvarchar(max))
  - LFMON (Financial Month, bigint)
  - LFGJA (Fiscal Year, bigint)
  - LBKUM (Closing Stock, float)

Column Logic:
- For BWART (Movement Type) only take where BWART = 105
- For SHKZG (Debit/Credit Indicator):
  - 'S' = Addition (positive MENGE) that is Procurement quantity or Supply
  - 'H' = Deduction (negative MENGE) that is Consumption
- String comparisons should use equality operators (= or <>) with proper quoting
- For string pattern matching, use LIKE operator with appropriate wildcards

Opening Stock Calculation:
- Opening Stock for each month = Previous month's LBKUM.
- Use LFMON - 1 for the previous month.
- If LFMON = 1 (April), use LFMON = 12 of the previous year (LFGJA - 1).

Calendar to LFMON Conversion:  
- April = 1, May = 2, June = 3, July = 4, August = 5, September = 6, October = 7, November = 8, December = 9, January = 10, February = 11, March = 12.

Additional Guidelines:
- Use the schema name {self.schema} for all table references without square brackets (e.g., schema.mseg instead of [schema].mseg).
- Use only the mseg and mbewh tables; no other tables are allowed.
- Ensure MENGE is adjusted based on SHKZG logic.
- Dynamically calculate Opening Stock from mbewh.
- Properly handle all string comparisons by using single quotes around string literals (e.g., SHKZG = 'S', not SHKZG = S)
- When comparing string values in WHERE clauses or joins, use proper string equality operators (= or <>)
- For string pattern matching, use LIKE with appropriate wildcards (%, _)
- For string concatenation, use the concat() function instead of the + operator
- Handle potential NULL values in string columns appropriately (use IS NULL or IS NOT NULL)
- Optimize the SQL query for SQL Server performance:
  - Use appropriate window functions instead of self-joins when possible
  - Minimize subqueries that require shuffling large amounts of data
  - Use proper date functions compatible with SQL Server 
  - Consider data partitioning when filtering on date columns
- Do not include explanations—return only the SQL query as plain text (no Markdown formatting).
- Apply all the necessary calculations which enhanced_question [{enhanced_question}] mentioned.
- Do not use square brackets [] anywhere in the SQL Server-compatible query, as they're not supported in SQL Server.
- Use backticks (`) if identifiers need to be escaped, rather than square brackets.
- For consumption and Procurement quantity or Supply refer to column logic.
- When using CTEs, place them at the beginning of the query using WITH syntax.
- For date functions, use SQL Server-compatible functions (DATEADD).
- For conditional logic, ensure CASE statements are properly formatted for SQL Server.
- Ensure all string comparisons are case-sensitive unless specified otherwise
- First, inspect the actual column names available in the mseg table schema. Based on the error message, BUDAT_MKPF is not available but there might be columns like BUDAT_MKPF, CPUDT_MKPF, or BUSTM.
Note: 
- For consumption calculations, only consider records where SHKZG = 'H'. (Important)
- For procurement or supply calculations, only consider records where SHKZG = 'S'. (Important)
- For inventory calculation, consider both 'S' = Addition (positive MENGE) and 'H' = Deduction (negative MENGE). (Important)
- For invoice number, purchase order number, vendor number and financial year take XBLNR_MKPF, EBELN, LIFNR, and BUDAT_MKPF columns from mseg table. (Important)
- String columns like MATNR, LIFNR, EBELN, CHARG, etc. should be properly quoted in the query for comparison.
- Financial year (FY), fiscal year, or simply 'year' starts from April 1st of a given year to March 31st of the following year. (Important)
- Q1 2024 (first Quarter) = April 1, 2024 to June 1, 2024; Q2 2024 (second Quarter) = July 1, 2024 to September 1, 2024. (Important)
- Q3 2024 (third Quarter) = October 1, 2024 to December 1, 2024; Q4 2024 (last quarter or fourth Quarter) = January 1, 2025 to March 1, 2025. (Important)
- Convert the datatype of BUDAT_MKPF use DATEADD(). (Important)
- Example format: "SELECT CAST(DATEADD(SECOND, BUDAT_MKPF, '2024-10-01') AS DATE)" if BUDAT_MKPF represents days. (Important)
- Generate an SQL Server-compatible query for BUDAT_MKPF, avoiding incorrect default dates like 1970-01-01. (Important)
- Generate an SQL Server-compatible query for BUDAT_MKPF, avoiding incorrect default dates like 1900-01-01. (Important)
- If a user asks about duplicate invoice number always filter BWART = 105. (Important)
Provide only the SQL Server-compatible query as plain text without any formatting or additional text.
 
"""
        return sql_prompt