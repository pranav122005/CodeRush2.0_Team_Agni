from groq import Groq
from config import settings

client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

def check_duplicate_transaction(payment_id: str, tx_id: str) -> bool:
    """
    Queries Groq LLM to check if this transaction should be processed.
    Returns True if it's safe to process (no duplicate found), False otherwise.
    In a real system, the LLM would have RAG access to a database of transactions.
    Here we simulate the LLM analyzing the structure and making a policy decision.
    """
    if not client:
        # For testing without an API key, we simulate an APPROVE
        return True
        
    prompt = f"""
    You are a strict financial registry compliance bot.
    A new settlement request came in.
    Payment ID: {payment_id}
    Transaction ID: {tx_id}
    
    If this transaction looks malformed or if you suspect it's a replay attack, output REJECT.
    Otherwise, output APPROVE.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.0
        )
        answer = response.choices[0].message.content.strip().upper()
        return "APPROVE" in answer
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fail closed on ambiguity or error
        return False
