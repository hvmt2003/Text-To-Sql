import os
import requests
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load env variables (DB_URI assumed to be present)
load_dotenv()

# Configuration
DB_URI = os.getenv("DB_URI", "mysql+pymysql://root:password@localhost:3306/text_to_sql")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# Global Engine
engine = create_engine(DB_URI)

import time

# Global Schema Cache
_CACHED_SCHEMA = None

def get_schema():
    """Extracts schema from the MySQL database using SQLAlchemy Inspector."""
    global _CACHED_SCHEMA
    if _CACHED_SCHEMA:
        return _CACHED_SCHEMA
        
    print("... Fetching Schema from DB ...")
    start_time = time.time()
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_str = ""
        for table in tables:
            columns = inspector.get_columns(table)
            col_desc = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            schema_str += f"Table {table}: {col_desc}\n"
        
        _CACHED_SCHEMA = schema_str
        print(f"... Schema fetched in {time.time() - start_time:.2f}s ...")
        return schema_str
    except Exception as e:
        return f"Error fetching schema: {e}"

def generate_sql_ollama(question, schema):
    """Sends prompt to Ollama to get SQL Query."""
    prompt = f"""You are an expert SQL Assistant. Given the database schema and a user question, generate a valid MySQL SELECT query.

SCHEMA:
{schema}

QUESTION: {question}

RULES:
- Return ONLY the SQL query.
- Do NOT return markdown (no ```sql ... ```).
- Do NOT return explanations.
- Only SELECT statements are allowed.
- Start the SQL with SELECT.
- Use MySQL syntax.

SQL:
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def validate_sql(sql):
    """Ensures SQL is safe and read-only."""
    if not sql:
        return False, "Empty SQL generated."
    
    # Remove markdown code blocks
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)
    sql = sql.strip()

    # Must start with SELECT
    if not sql.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."
    
    # Forbidden keywords
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "EXEC", "--", ";"]
    upper_sql = sql.upper()
    for word in forbidden:
        if re.search(r'\b' + re.escape(word) + r'\b', upper_sql):
            return False, f"Forbidden keyword detected: {word}"
            
    return True, sql

def execute_query(sql):
    """Executes SQL on MySQL DB and returns list of dicts."""
    try:
        # Using Pandas to read SQL is easiest
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
            # Convert Timestamps to string to ensure JSON serializability
            for col in df.select_dtypes(include=['datetime', 'datetimetz']).columns:
                df[col] = df[col].astype(str)
            return df.to_dict(orient="records"), None
    except Exception as e:
        return None, str(e)

def ask_database(question):
    """Main Orchestrator."""
    print(f"\n--- Processing Question: {question} ---")
    
    # 1. Get Schema
    schema = get_schema()
    if "Error" in schema:
        return f"Schema Error: {schema}", []

    # 2. LLM Generate
    print("... Sending to Ollama ...")
    start_llm = time.time()
    raw_sql = generate_sql_ollama(question, schema)
    print(f"... Ollama responded in {time.time() - start_llm:.2f}s ...")
    
    if not raw_sql:
        return "Error generating SQL", []
    
    # 3. Validate
    is_valid, clean_sql = validate_sql(raw_sql)
    if not is_valid:
        return f"Invalid SQL: {clean_sql}", []
    
    # 4. Execute
    print(f"... Executing SQL: {clean_sql} ...")
    results, error = execute_query(clean_sql)
    if error:
        return f"SQL Execution Error: {error}", []
        
    return clean_sql, results
