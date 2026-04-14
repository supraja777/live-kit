import os
import json
from ddgs import DDGS
from groq import Groq

from dotenv import load_dotenv

load_dotenv()

# Initialize the Groq Client globally
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_leetcode_questions(topic=None, level=None, company=None):
    """
    Combines search and LLM extraction to return a structured list of LeetCode problems.
    """
    
    # 1. Targeted Search Query Construction
    query_parts = ["site:leetcode.com/problems/"]
    if topic: query_parts.append(topic)
    if level: query_parts.append(level)
    if company: query_parts.append(f"asked at {company}")
    
    search_query = " ".join(query_parts)
    print(f"--- Initiating Deep Search: {search_query} ---")

    # 2. Gather snippets using DuckDuckGo
    results_text = ""
    try:
        with DDGS() as ddgs:
            # max_results=20 ensures we provide enough raw data for the agent to find 5+ valid problems
            results = ddgs.text(search_query, max_results=20)
            for i, r in enumerate(results):
                results_text += f"RESULT_{i}:\nTitle: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n\n"
    except Exception as e:
        print(f"Search Error: {e}")
        return None

    # 3. Construct the Rich Prompt
    rich_prompt = f"""
    You are a Technical Sourcing Agent. I have provided raw search data from LeetCode.

    CONTEXT:
    Topic: {topic if topic else 'General'}
    Level: {level if level else 'Any'}
    Target Company: {company if company else 'N/A'}

    DATA:
    {results_text}

    TASK:
    1. Identify at least 5 distinct LeetCode problems from the data.
    2. Extract the exact 'question name', the primary 'Topic', and the direct 'url'.
    3. Ensure the URL is a direct link (leetcode.com/problems/...).

    OUTPUT FORMAT (STRICT JSON ONLY):
    {{
      "questions": [
        {{
          "question name": "String",
          "Topic": "String",
          "url": "String"
        }}
      ]
    }}
    """

    # 4. Call Groq Agent for JSON Extraction
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs ONLY valid JSON."},
                {"role": "user", "content": rich_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )

        # Parse and return the JSON data
        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"Groq API Error: {e}")
        return None

# --- TESTING THE FLOW ---
if __name__ == "__main__":
    # Example: Fetching medium array questions for Amazon
    data = get_leetcode_questions(topic="Array", level="Medium", company="Amazon")
    
    if data and "questions" in data:
        print("\n--- Found Questions ---")
        print(json.dumps(data, indent=2))
    else:
        print("Failed to retrieve or parse questions.")