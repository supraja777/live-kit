import os
import re
import json
import asyncio
import aiohttp
from typing import Annotated
from groq import Groq
from duckduckgo_search import DDGS
from livekit.agents.llm import function_tool

from dotenv import load_dotenv
load_dotenv()

# Initialize the Groq Client
# Ensure GROQ_API_KEY is in your environment variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class LeetCodeSolutionTool:
    @function_tool
    async def generate_problem_approaches(
        self,
        url: Annotated[str, "The full LeetCode problem URL"],
        language: Annotated[str, "The programming language for the code solution"]
    ) -> str:
        """
        Fetches a LeetCode problem's content and asks Groq to generate all 
        possible algorithmic approaches in a structured JSON format.
        """
        # 1. Extract the title slug from the URL
        match = re.search(r"problems/([\w-]+)", url)
        if not match:
            return json.dumps({"error": "Invalid LeetCode URL format."})
        
        slug = match.group(1)

        # 2. Fetch the actual problem description from LeetCode GraphQL
        # This provides the AI with the exact constraints and requirements
        gql_url = "https://leetcode.com/graphql"
        query = """
        query getQuestionDetail($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            title
            content
          }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(gql_url, json={'query': query, 'variables': {'titleSlug': slug}}) as resp:
                    data = await resp.json()
                    q_data = data.get('data', {}).get('question')
                    if not q_data:
                        return json.dumps({"error": f"Problem '{slug}' not found on LeetCode."})
                    
                    # Strip HTML tags so the LLM gets clean text
                    description = re.sub('<[^<]+?>', '', q_data['content'])
        except Exception as e:
            return json.dumps({"error": f"Failed to fetch problem data: {str(e)}"})

        # 3. Ask Groq to generate the solutions
        # We don't manually parse snippets; we give the AI the whole description 
        # and let it "reason" out the best approaches.
        prompt = f"""
        Problem Title: {q_data['title']}
        Problem Description: {description}
        Target Programming Language: {language}

        TASK:
        Analyze the problem and generate a comprehensive list of ALL valid algorithmic approaches 
        (e.g., Brute Force, Optimized, Space-Efficient, etc.).

        For each approach, provide:
        1. A list of patterns/algorithms used.
        2. A clear explanation of the approach.
        3. Time Complexity (TC).
        4. Space Complexity (SC).
        5. The complete implementation code in {language}.

        OUTPUT FORMAT:
        Return ONLY a JSON object with the following structure:
        {{
          "approaches": [
            {{
              "list of patterns": ["Pattern 1", "Pattern 2"],
              "Approach": "Detailed explanation here",
              "TC": "O(...)",
              "SC": "O(...)",
              "Code": "..."
            }}
          ]
        }}
        """

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Senior Technical Interviewer. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return json.dumps({"error": f"Groq Generation Error: {str(e)}"})

# --- MAIN EXECUTION BLOCK ---
async def main():
    # Instantiate the tool
    tool = LeetCodeSolutionTool()

    # Configuration for the test
    target_url = "https://leetcode.com/problems/minimum-removals-to-achieve-target-xor/description/"
    target_lang = "C++"

    print(f"--- Requesting all solutions for: {target_url} ---")
    
    # Call the tool
    json_response = await tool.generate_problem_approaches(
        url=target_url, 
        language=target_lang
    )

    # Display the structured result
    try:
        final_data = json.loads(json_response)
        print(json.dumps(final_data, indent=2))
    except Exception as e:
        print("Raw Response from Agent:")
        print(json_response)

if __name__ == "__main__":
    asyncio.run(main())