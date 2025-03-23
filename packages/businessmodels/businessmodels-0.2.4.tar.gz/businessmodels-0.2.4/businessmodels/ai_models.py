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
    
    INVENTORY TURNOVER RATIO:
    - The Inventory Turnover Ratio is calculated as:
      **Total Opening Stock / Total Consumption**
    - Total Opening Stock is the stock available at the beginning of the period.
    - Total Consumption is the sum of all outflows (deductions).
    - Consider only records where SHKZG = 'H' for total consumption.
    - Ensure data is filtered based on financial periods and correctly aggregated before calculation.

    SQL QUERY REQUIREMENTS:
    - Ensure the query is optimized for large datasets by using appropriate indexing and partitioning techniques.
    - Use INNER JOINs or LEFT JOINs only when necessary to minimize performance overhead.
    - Implement proper filtering based on financial year and date ranges.
    - If aggregation is needed, use GROUP BY and window functions where appropriate.
    - Ensure data integrity by filtering out NULL values where necessary.
    - Use CTEs (Common Table Expressions) to break down complex queries into manageable parts.
    - Convert all date fields into 'YYYY-MM-DD' format before performing operations.
    - If ranking or percentile calculations are required, use the RANK() or PERCENTILE_DISC() functions.
    - When dealing with hierarchical data, use recursive CTEs for optimal performance.
    - Avoid SELECT *, explicitly define the required columns for clarity and efficiency.

    CRITICAL BUSINESS RULES:
    - For consumption calculations, only consider records where SHKZG = 'H'.
    - For procurement or supply calculations, only consider records where SHKZG = 'S'.
    - For inventory calculations, consider both:
        - 'S' = Addition (positive MENGE).
        - 'H' = Deduction (negative MENGE).
    - For invoice number, vendor number, and financial year, use:
        - Invoice Number: EBELN.
        - Vendor Number: LIFNR.
        - Financial Year: BUDAT_MKPF.
    - Convert BUDAT_MKPF from 'YYYYMMDD' to 'YYYY-MM-DD' before performing date-based filtering.

    QUERY RESPONSE FORMAT:

    "Analysis Plan: [Restate the core question in specific terms, clearly specifying the exact date ranges]
    Data needed: [List the specific tables and fields required]
    Time periods: [Define exact date ranges with specific months and years - be very explicit]
    Calculations: [Specify exact formulas for all metrics mentioned]
    Filters: [Define precise filtering conditions]
    Sorting: [Specify the order of results]"
   
    Keep your response simple, clear, and in plain text format. Focus on making vague terms specific and defining precise calculations.
 
    Keep your response simple, clear, and in plain text format. Focus on making vague terms specific and defining precise calculations.
 
    Note: - For consumption calculations, only consider records where SHKZG = 'H'. (Important)
          - For procurement or supply calculations, only consider recods where SHKZG='S'.(Important)
          - For inventory calculation, consider both 'S' = Addition (positive MENGE) and 'H' = Deduction (negative MENGE). (Important)
          - For purchase order no., invoice number, vendor number and financial year take XBLNR_MKPF, EBELN, LIFNR, and BUDAT_MKPF columns from mseg table. (Important)
          - Convert the datatype of BUDAT_MKPF from 'YYYYMMDD' to 'YYYY-MM-DD'. (Important)
          - Do not provide any raw SQL query, only step by step instructions.
    """
        return enhancement_prompt

    def sql_prompt(self, enhanced_question):
        """
        Generate the SQL prompt for OpenAI based on the user question.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        sql_prompt = f"""
        You are a highly skilled Spark SQL expert and data analyst specializing in Fabric lakehouse environments. Generate an optimized Spark SQL query strictly using only the tables mseg (Material Document Segment) and mbewh (Material Valuation History) from the database schema.
        Enhanced User Question: {enhanced_question}
        Today's date is: {current_date}

        Table Reference Rules:
        - Columns from mseg:
        - MATNR (Material Number, STRING)
        - BUDAT_MKPF (Posting Date, STRING)
        - SHKZG (Debit/Credit Indicator, STRING)
        - MENGE (Quantity, STRING)
        - LIFNR (Vendor Number, STRING)
        - EBELN (Purchase Order No., STRING)
        - MAA_URZEI (Origin Indicator, STRING)
        - BWART (Movement Type, STRING)
        - WERKS (Plant, STRING)
        - LGORT (Storage Location, STRING)
        - CHARG (Batch Number, STRING)
        - XBLNR_MKPF (Invoice No., STRING)
        - Columns from mbewh:
        - MATNR (Material Number, STRING)
        - LFMON (Financial Month, STRING)
        - LFGJA (Fiscal Year, STRING)
        - LBKUM (Closing Stock, STRING)

        Column Logic:
        - For SHKZG (Debit/Credit Indicator):
        - 'S' = Addition (positive MENGE) that is Procurement quantity or Supply
        - 'H' = Deduction (negative MENGE) that is Consumption
        - String comparisons should use equality operators (= or <>) with proper quoting
        - For string pattern matching, use LIKE operator with appropriate wildcards

        Opening Stock Calculation:
        - Opening Stock for each month = Previous month's LBKUM.
        - Use LFMON - 1 for the previous month.
        - If LFMON = 1 (April), use LFMON = 12 of the previous year (LFGJA - 1).

        Inventory Turn Over Ratio Calculation:
        **Total Opening Stock / Total Consumption**
        - Total Opening Stock is the stock available at the beginning of the period.
        - Total Consumption is the sum of all outflows (deductions).
        - Consider only records where SHKZG = 'H' for total consumption.
        - Ensure data is filtered based on financial periods and correctly aggregated before calculation.

        Calendar to LFMON Conversion:  
        - April = 1, May = 2, June = 3, July = 4, August = 5, September = 6, October = 7, November = 8, December = 9, January = 10, February = 11, March = 12.

        Additional Guidelines:
        - Use the schema name {self.schema} for all table references without square brackets (e.g., schema.mseg instead of [schema].mseg).
        - Use only the from mseg and mbewh tables; no other tables are allowed.
        - Ensure MENGE is adjusted based on SHKZG logic.
        - Dynamically calculate Opening Stock from mbewh.
        - Properly handle all string comparisons by using single quotes around string literals (e.g., SHKZG = 'S', not SHKZG = S)
        - When comparing string values in WHERE clauses or joins, use proper string equality operators (= or <>)
        - For string pattern matching, use LIKE with appropriate wildcards (%, _)
        - For string concatenation, use the concat() function instead of the + operator
        - Handle potential NULL values in string columns appropriately (use IS NULL or IS NOT NULL)
        - Optimize the SQL query for Spark SQL performance:
        - Use appropriate window functions instead of self-joins when possible
        - Minimize subqueries that require shuffling large amounts of data
        - Use proper date functions compatible with Spark SQL
        - Consider data partitioning when filtering on date columns
        - Do not include explanations—return only the SQL query as plain text (no Markdown formatting).
        - Apply all the necessary calculations which enhanced_question [{enhanced_question}] mentioned.
        - Do not use square brackets [] anywhere in the SQL query, as they're not supported in Spark SQL.
        - Use backticks (') if identifiers need to be escaped, rather than square brackets.
        - For consumption and Procurement quantity or Supply refer to column logic.
        - When using CTEs, place them at the beginning of the query using WITH syntax.
        - For date functions, use Spark SQL-compatible functions (date_add, date_sub, etc.).
        - For conditional logic, ensure CASE statements are properly formatted for Spark SQL.
        - Ensure all string comparisons are case-sensitive unless specified otherwise
        - First, inspect the actual column names available in the mseg table schema. Based on the error message, BUDAT_MKPF is not available but there might be columns like BUDAT_MKPF, CPUDT_MKPF, or BUSTM.
        Note:
        - For consumption calculations, only consider records where SHKZG = 'H'. (Important)
        - For procurement or supply calculations, only consider records where SHKZG = 'S'. (Important)
        - For inventory calculation, consider both 'S' = Addition (positive MENGE) and 'H' = Deduction (negative MENGE). (Important)
        - For purchase order number, invoice number, vendor number and financial year take XBLNR_MKPF, EBELN, LIFNR, and BUDAT_MKPF columns from mseg table. (Important)
        - String columns like MATNR, LIFNR, EBELN, CHARG, etc. should be properly quoted in the query for comparison.
        - Financial year (FY), fiscal year, or simply 'year' starts from April 1st of a given year to March 31st of the following year. (Important)
        - Q1 2024 (first Quarter) = April 1, 2024 to June 1, 2024; Q2 2024 (second Quarter) = July 1, 2024 to September 1, 2024. (Important)
        - Q3 2024 (third Quarter) = October 1, 2024 to December 1, 2024; Q4 2024 (last quarter or fourth Quarter) = January 1, 2025 to March 1, 2025. (Important)
        Provide only the SQL query as plain text without any formatting or additional text.
        """
        return sql_prompt
    
    def enhancement_prompt_an(self, user_question, prompt_instructions=""):
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
    
        enhancement_prompt_an = f"""
    You are a SQL expert with deep knowledge of anomaly detection in structured datasets. Your goal is to refine 
    and enhance user queries based on the mseg_anomalies_ctas table structure while ensuring proper handling 
    of anomaly-related conditions.
   
    Today's Date: {current_date}
    Schema: {self.schema}
    Prompt Instructions: {prompt_instructions}
    User Question: {user_question}

    Table Structure:
    - {self.schema}.mseg_anomalies_ctas contains multiple anomaly detection columns.
    - Each attribute 'X' has two corresponding anomaly columns:
        1. 'X_anomaly' (binary flag where 1 = anomaly detected, 0 = normal)
        2. 'X_anomaly_score' (numerical score indicating anomaly strength)
    
    ANOMALY DETECTION RULES (CRITICAL):
    - An anomaly is identified by 'X_anomaly' = 1
    - The 'X_anomaly_score' indicates the strength of the anomaly:
        * POSITIVE values (> 0) indicate stronger anomalies
        * NEGATIVE values (< 0) indicate normal behavior
        * Higher positive scores indicate more significant anomalies
    
    - To find the most significant anomalies, sort by 'X_anomaly_score' in DESCENDING order
    - The only table available for querying is {self.schema}.mseg_anomalies_ctas.

    Query Transformation Guide:
    - Identify Key Attributes: Extract relevant columns from the user request from the {self.schema}.mseg_anomalies_ctas table only.
    - Apply Anomaly Filters: Use 'X_anomaly'=1 to identify anomalies from the {self.schema}.mseg_anomalies_ctas table.
    - Filter Conditions: Include any user-defined filtering criteria (e.g., date range, specific materials).
    - Sorting Rules: Ensure high anomalies appear first using ORDER BY 'X_anomaly_score' DESC.
    - Table Referencing: Ensure queries reference '{self.schema}.mseg_anomalies_ctas' correctly.

    Transform the user's question into a clear analysis plan using plain text only. Do not use markdown, bullets, or numbering.
    
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
    Anomaly Handling: [Specify which anomaly fields to use, e.g., 'X_anomaly=1 AND X_anomaly_score > 0.1' or the threshold specified by the user]
    Time periods: [Define exact date ranges with specific months and years - be very explicit]
    Filters: [Apply 'X_anomaly=1 AND X_anomaly_score > 0.1' or the user-specified threshold, plus any additional filters]
    Sorting: [Specify the order of results - typically 'X_anomaly_score DESC' to show most significant anomalies first]"
   
    Keep your response simple, clear, and in plain text format. Focus on making vague terms specific and defining precise calculations.
 
    Note: 
    - When filtering anomalies, ALWAYS use BOTH conditions: 'X_anomaly = 1' AND 'X_anomaly_score > threshold' (default 0.1 unless user specifies otherwise)
    - Remember that positive scores (> 0) indicate anomalies, with higher scores showing stronger anomalies 
    - Negative scores (< 0) indicate normal behavior (not anomalies)
    - If the user wants the highest anomalies, sort results in descending order of 'X_anomaly_score'
    - Convert the datatype of BUDAT_MKPF from 'YYYYMMDD' to 'YYYY-MM-DD' in {self.schema}.mseg_anomalies_ctas
    - For quantity, plant, amount, moving indicator, invoice no., vendor no. use MENGE, WERKS, DMBTR, BWART, XBLNR_MKPF, LIFNR from mseg_anomalies_ctas table
    - If the generated SQL query includes BUDAT_MKPF, it should always refer to the column BUDAT_MKPF
    - Detect anomalies in transactional data by identifying unusual patterns based on key attributes, focusing on records where X_anomaly=1 AND X_anomaly_score > 0.1 (or the user-specified threshold)

    """
        return enhancement_prompt_an
    
    def sql_prompt_an(self, enhanced_question):
        """
        Generate an optimized Spark SQL query based on an enhanced user input using Azure OpenAI GPT-4o.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        sql_prompt_an = f"""
        You are a highly skilled SQL expert specializing in *Spark SQL within Microsoft Fabric*. Your task is to generate a 
        fully optimized SQL query based on the user's request while ensuring proper anomaly detection and handling. 
        Enhanced User Question: {enhanced_question}
        Today's date is: {current_date}

        Table Reference Rules:
        - Columns from 'mseg_anomalies_ctas':
        -  MATNR (Material Number, STRING)
        -  BUDAT_MKPF (Posting Date, STRING)
        -  DMBTR (Amount, STRING) 
        -  MENGE (Quantity, STRING)
        -  BWART (moving_indicator, STRING)
        -  WERKS (Plant, STRING)
        -  XBLNR_MKPF (invoice no., STRING)
        -  LIFNR (vendor no., STRING)
        -  MENGE_anomaly (Quantity Anomaly, INT/BOOLEAN)
        -  MENGE_anomaly_score (Quantity Anomaly Score, FLOAT)
        -  WERKS_anomaly (Plant Anomaly, INT/BOOLEAN)
        -  WERKS_anomaly_score (Plant Anomaly Score, FLOAT)
        -  BWART_anomaly (Movement Type Anomaly, INT/BOOLEAN)
        -  BWART_anomaly_score (Movement Type Anomaly Score, FLOAT)
        -  DMBTR_anomaly (Amount Anomaly, INT/BOOLEAN)
        -  DMBTR_anomaly_score (Amount Anomaly Score, FLOAT)
        -  XBLNR_MKPF_anomaly (invoice no. Anomaly, LONG)
        -  XBLNR_MKPF_anomaly_score (invoice no. Anomaly Score, FLOAT)
        -  LIFNR_anomaly (vendor no. Anomaly, LONG)
        -  LIFNR_anomaly_score (vendor no. Anomaly Score, FLOAT)
    
        Query Context:
        The query will retrieve insights from the '{self.schema}.mseg_anomalies_ctas' table, which contains anomaly detection columns
        for various attributes. Each attribute 'X' has two corresponding anomaly columns:  
    
        1. A binary flag ('X_anomaly'):
        - Value of 1 indicates an anomaly
        - Value of 0 means normal data (not an anomaly)
    
        2. A numeric score ('X_anomaly_score'):
        - Measures the strength/significance of the anomaly
        - Higher positive scores indicate stronger anomalies
        - Negative scores indicate normal behavior
        - Used for sorting and ranking anomalies

        Anomaly Handling Logic (CRITICAL):
        - When filtering for anomalies, use 'X_anomaly' = 1
    
        - For sorting the most significant anomalies, use ORDER BY 'X_anomaly_score' DESC
        - If multiple attributes are involved, apply AND conditions to filter anomalies across them
        - Ensure NULL safety: Handle cases where 'X_anomaly' or 'X_anomaly_score' may be NULL using appropriate IS NOT NULL checks
        - When selecting top anomalies, use LIMIT or ROW_NUMBER() to retrieve the specified number of records

        Additional Guidelines:
        - Use the schema name '{self.schema}' for all table references
        - Query ONLY columns from the '{self.schema}.mseg_anomalies_ctas' table - do not reference any other table
        - Optimize the SQL query for Spark SQL performance:
            * Use appropriate window functions instead of self-joins when possible
            * Minimize subqueries that require shuffling large amounts of data
            * Consider data partitioning when filtering on date columns
        - Return only the SQL query as plain text without explanations
        - Apply all necessary calculations as mentioned in the enhanced question
        - Do not use square brackets '[]', use backticks '`' for escaping identifiers if needed
        - Use 'WITH' for CTEs at the beginning of the query when appropriate
        - For date functions, use Spark SQL-compatible functions (date_add, date_sub, etc.)
        - For conditional logic, ensure CASE statements are properly formatted for Spark SQL
        - If multiple anomaly scores are involved, consider using COALESCE for combined sorting: 
        ORDER BY COALESCE(X1_anomaly_score, X2_anomaly_score) DESC
    
        Important Notes:
        - Convert BUDAT_MKPF (BIGINT) to a DATE using: TO_DATE(CAST(BUDAT_MKPF AS STRING), 'yyyyMMdd')
        - Always refer to the date column as BUDAT_MKPF (with the underscore) not as BUDAT_MKPF
        - For quantity, plant, amount, moving indicator, invoice no., vendor no. use 
        MENGE, WERKS, DMBTR, BWART, XBLNR_MKPF, LIFNR from mseg_anomalies_ctas table
        - Remember: 'X_anomaly' = 1 identifies anomalies; 'X_anomaly_score' indicates anomaly strength
        - Provide ONLY the SQL query without any explanations or markdown formatting
        """
        return sql_prompt_an