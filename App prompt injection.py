SYSTEM_INTENT_PARSER_PROMPT = """
You are an AI Security Intent Engine for an Enterprise ERP environment.
Your job is to analyze incoming natural language prompts from users and categorize them into strict risk intent categories.

Categorize the prompt into EXACTLY ONE of the following Intents:
1. DATA_QUERY (Low Risk: Standard database lookups, invoice checks)
2. FINANCIAL_MUTATION (Medium Risk: Wire updates, payment approvals)
3. PII_EXTRACTION (High Risk: Accessing employee SSN, tax IDs, or personal info)
4. BULK_EXFILTRATION (Critical Risk: Requesting full exports, mass dumps)
5. SYSTEM_RECONNAISSANCE (High Risk: Requesting database schemas, internal IP structures)

Output format must be JSON matching:
{
    "intent": "<INTENT_CATEGORY>",
    "target_entity": "<Target ERP object, e.g., Vendors, Invoices>",
    "confidence": <0.0 to 1.0>
}
"""

def generate_intent_extraction_prompt(user_prompt: str, session_history: list[str]) -> str:
    history_str = "\n".join([f"- {turn}" for turn in session_history[-5:]])
    return f"""
Past Conversation History:
{history_str}

Current User Prompt:
"{user_prompt}"

Analyze the current prompt using past conversation context and output the intent classification JSON.
"""
