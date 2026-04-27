import os
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AZUREOPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

filepath = os.path.join(os.path.dirname(__file__), "prompt_criteria.md")


def load_criteria(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        criteria = file.read()
    return criteria


criteria_text = load_criteria(filepath)

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_key=api_key,    
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert prompt engineer and evaluator.

Your task is to evaluate the user's prompt against the following scoring criteria:

---
{criteria}
---

For EACH of the 5 criteria (Clarity, Specificity / Details, Context, Output Format & Constraints, Persona Defined), you MUST:
1. State the criterion name
2. Give a score from 0 to 10
3. Provide a brief justification (1-2 sentences explaining why you gave that score)

Then:
- Present all scores in a markdown table with columns: Criteria | Score (0-10) | Justification
- Calculate the **Final Score** as the average of all 5 criteria scores (rounded to 1 decimal)
- Provide a short overall explanation of the prompt's strengths and weaknesses
- Suggest specific, actionable improvements to make the prompt better

Output everything in well-formatted markdown.""",
        ),
        ("human", "Please evaluate this prompt:\n\n{user_prompt}"),
    ]
)

# Accept prompt from command line argument or use a default
DEFAULT_PROMPT = """Write a Blog on AI."""

# Take user input interactively
print("Enter the prompt you want to evaluate (press Enter to use default):")
user_input = input("> ").strip()
user_prompt = user_input if user_input else DEFAULT_PROMPT

print(f"📝 Evaluating prompt: \"{user_prompt}\"\n")
print("=" * 60)

chain = prompt_template | llm

response = chain.invoke({"criteria": criteria_text, "user_prompt": user_prompt})

print(response.content)
