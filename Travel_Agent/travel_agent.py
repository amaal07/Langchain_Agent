import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

api_key = os.getenv("AZUREOPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    api_key=api_key,    
    api_version="2024-12-01-preview",
    azure_endpoint=endpoint
)

# Added {summary} here so the AI actually sees the context
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a specialized Travel Agent. Only answer travel-related queries. "
               "Context from previous talk: {summary}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_input}"),
])

summary_prompt_template = ChatPromptTemplate.from_messages([
   MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Summarize the travel-related queries and responses from the above conversation in a concise manner.") 
])

history = []
summary = "No conversation yet."
count = 0

def chat_with_travel_agent(text_input):
    global history, summary, count

    if count > 5:
        summary_input = {"chat_history": history}
        # FIX: Added .content here so summary is a string, not an object
        summary_obj = llm.invoke(summary_prompt_template.invoke(summary_input))
        summary = summary_obj.content 
        
        history = []  
        count = 0  
        print(f"\n--- 🔄 New Summary Generated ---\n")
    
    chat_input = {
        "user_input": text_input,
        "chat_history": history,
        "summary": summary
    }
    
    full_prompt = prompt_template.invoke(chat_input)

    print("Agent: ", end="")
    full_response = ""

    for chunk in llm.stream(full_prompt):
        content = chunk.content
        print(content, end="", flush=True)
        full_response += content

    history.append(HumanMessage(content=text_input))
    history.append(AIMessage(content=full_response))
    print("Please find the Conversation History below:")
    for msg in history:
        if isinstance(msg, HumanMessage):
            print(f"System: {msg.content}") 
        elif isinstance(msg, AIMessage):
            print(f"You: {msg.content}")    
              
        print("----------------------------------------\n")
    count += 1


if __name__ == "__main__":
    print("\n" + "="*50)
    print("✈️  AZURE TRAVEL AGENT ACTIVE")
    print("Type 'exit' to quit or 'clear' to reset history.")
    print("="*50 + "\n")

    while True:
        try:
            user_input = input("\033[94mYou: \033[0m") 

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nAgent: Safe travels! Goodbye.")
                break

            if user_input.lower() == "clear":
                history = []
                count = 0
                summary = "No conversation yet."
                print("\n[System: Chat history cleared]\n")
                continue

            if not user_input.strip():
                continue

            chat_with_travel_agent(user_input)
            
        except KeyboardInterrupt:
            print("\nAgent: Session ended. Goodbye!")
            break
