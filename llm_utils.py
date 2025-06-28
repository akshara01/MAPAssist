from transformers import pipeline

llm = pipeline("text2text-generation", model="google/flan-t5-base", max_new_tokens=50)

def classify_severity(user_message):
    prompt = f"""
Classify the distress level of the following message into one of these buckets: CRITICAL, MEDIUM, LOW.

- CRITICAL: Life-threatening emergencies (injuries, flooding inside home, etc.)
- MEDIUM: Needs help but not life-threatening (lost power, needs food)
- LOW: Awareness or general info request (shelter location, storm updates)

Message: "{user_message}"
Answer:"""

    result = llm(prompt)[0]['generated_text']
    print("🧠 Raw LLM output:", result)
    
    # Extract the answer cleanly
    for level in ["CRITICAL", "MEDIUM", "LOW"]:
        if level in result.upper():
            return level
    return "LOW"  # default fallback
