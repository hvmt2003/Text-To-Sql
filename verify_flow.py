from chatbot_engine import ask_database
import sys

def test_query():
    question = "Show me the top 3 most expensive products."
    print(f"Testing Question: {question}")
    
    try:
        sql, result = ask_database(question)
        print(f"Generated SQL: {sql}")
        print(f"Result: {result}")
        
        if "Error" in sql:
            print("FAILED: Error returned.")
            sys.exit(1)
            
        if not result or len(result) == 0:
            print("WARNING: No results returned (might be valid if DB is empty).")
        
        print("SUCCESS: Flow executed correctly.")
        
    except Exception as e:
        print(f"EXCEPTION: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_query()
