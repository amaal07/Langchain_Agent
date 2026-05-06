import os
from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 1. Setup Models
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings()

# 2. Setup Vector Store (Knowledge Base) - using path relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
kb_path = os.path.join(script_dir, "knowledge_base.txt")

loader = TextLoader(kb_path)
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
vector_db = Chroma.from_documents(splitter.split_documents(docs), embeddings)
retriever = vector_db.as_retriever()

# 3. State & Schema
class EmailAnalysis(BaseModel):
    urgency: str = Field(description="Low, Medium, or High")
    topic: str = Field(description="Account, Billing, Bug, Feature Request, or Technical issue")
    decision: str = Field(description="Auto-reply or Escalation")
    follow_up: str = Field(description="Follow-up action required, e.g. 'Schedule follow-up in 3 days for fix confirmation' or 'None'")

class AgentState(TypedDict):
    email_content: str
    analysis: EmailAnalysis
    draft: str
    follow_up_scheduled: str

# 4. Nodes
def classify_node(state: AgentState):
    """Classifies the email by urgency, topic, decision, and follow-up action."""
    prompt = ChatPromptTemplate.from_template(
        "You are a customer support triage agent. Analyze this incoming support email and categorize it.\n\n"
        "Email: {content}\n\n"
        "Classify the following:\n"
        "- urgency: Low, Medium, or High\n"
        "- topic: One of Account, Billing, Bug, Feature Request, Technical issue\n"
        "- decision: 'Auto-reply' if the issue can be resolved with a knowledge base answer, "
        "'Escalation' if the issue is complex, urgent, or requires human intervention\n"
        "- follow_up: Describe any follow-up action needed (e.g., 'Schedule follow-up in 3 days to confirm fix', "
        "'Wait for customer confirmation', 'Monitor for recurrence') or 'None' if no follow-up is needed.\n\n"
        "Return structured data."
    )
    chain = prompt | llm.with_structured_output(EmailAnalysis)
    return {"analysis": chain.invoke({"content": state["email_content"]})}

def rag_node(state: AgentState):
    """Retrieves relevant knowledge base content and drafts a response."""
    query = state["email_content"]
    retrieved = retriever.invoke(query)
    context = "\n".join([d.page_content for d in retrieved])
    
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful customer support agent. Using the knowledge base context below, "
        "draft a polite, professional, and helpful response to the customer's email.\n\n"
        "Knowledge Base Context:\n{context}\n\n"
        "Customer Email:\n{query}\n\n"
        "Draft a response that addresses the customer's concern directly. "
        "If the knowledge base doesn't fully cover the issue, acknowledge that and provide what help you can."
    )
    chain = prompt | llm
    draft = chain.invoke({"context": context, "query": query}).content
    return {"draft": draft}

def escalation_node(state: AgentState):
    """Handles escalation for complex or urgent issues."""
    analysis = state["analysis"]
    return {
        "draft": (
            f"⚠️ ESCALATION REQUIRED ⚠️\n"
            f"This issue has been flagged for human agent review.\n"
            f"- Urgency: {analysis.urgency}\n"
            f"- Topic: {analysis.topic}\n"
            f"- Reason: Issue is complex or urgent and requires human intervention.\n\n"
            f"Original email:\n{state['email_content']}\n\n"
            f"A support specialist will review this case and respond shortly."
        )
    }

def follow_up_node(state: AgentState):
    """Schedules follow-up actions if required."""
    analysis = state["analysis"]
    follow_up = analysis.follow_up
    
    if follow_up and follow_up.lower() != "none":
        scheduled_msg = f"📅 Follow-up Scheduled: {follow_up}"
        # In a production system, this would create a calendar event, 
        # set a reminder, or create a ticket in a task management system.
        print(f"\n{scheduled_msg}")
        return {"follow_up_scheduled": scheduled_msg}
    else:
        return {"follow_up_scheduled": "No follow-up required."}

# 5. Graph Definition
def route_email(state: AgentState):
    """Routes email to either auto-reply (RAG) or escalation based on classification."""
    if state["analysis"].decision == "Escalation":
        return "escalate"
    return "generate_reply"

workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("classify", classify_node)
workflow.add_node("generate_reply", rag_node)
workflow.add_node("escalate", escalation_node)
workflow.add_node("follow_up", follow_up_node)

# Set entry point
workflow.set_entry_point("classify")

# Conditional routing after classification
workflow.add_conditional_edges(
    "classify", 
    route_email, 
    {"escalate": "escalate", "generate_reply": "generate_reply"}
)

# Both paths lead to follow-up check, then END
workflow.add_edge("generate_reply", "follow_up")
workflow.add_edge("escalate", "follow_up")
workflow.add_edge("follow_up", END)

app = workflow.compile()

# 6. Process a single email and display results
def process_email(email: str, label: str = ""):
    """Process a single customer email and print structured results."""
    if label:
        print(f"\n{'='*60}")
        print(f"📧 Scenario: {label}")
        print(f"{'='*60}")
    
    print(f"\n📩 Email: {email}\n")
    
    result = app.invoke({"email_content": email})
    
    analysis = result["analysis"]
    
    print(f"--- 📊 Analysis ---")
    print(f"  1. Urgency:    {analysis.urgency}")
    print(f"  2. Topic:      {analysis.topic}")
    print(f"  3. Decision:   {analysis.decision}")
    print(f"  4. Follow-up:  {analysis.follow_up}")
    
    print(f"\n--- 📝 Response Draft ---")
    print(result["draft"])
    
    print(f"\n--- 📅 Follow-up Action ---")
    print(f"  {result.get('follow_up_scheduled', 'N/A')}")
    
    print(f"\n{'-'*60}")
    return result

# 7. Execution with all 5 example scenarios
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖  AI CUSTOMER SUPPORT AGENT")
    print("Processing incoming customer emails...")
    print("="*60)

    # All 5 required example scenarios
    test_emails = [
        {
            "label": "Simple Product Question",
            "email": "Hi, how do I reset my password? I can't seem to find the option anywhere."
        },
        {
            "label": "Bug Report",
            "email": "The export feature crashes every time I select PDF format. I've tried multiple times with different reports and it keeps failing. I'm using Chrome on Windows 11."
        },
        {
            "label": "Urgent Billing Issue",
            "email": "I was charged twice for my subscription this month! I need this resolved immediately. My transaction IDs are TXN-8834 and TXN-8835. Please refund the duplicate charge ASAP."
        },
        {
            "label": "Feature Request",
            "email": "Can you add dark mode to the mobile app? It's available on the web version but I mostly use the app on my phone and the bright screen is hard on my eyes at night."
        },
        {
            "label": "Complex Technical Issue",
            "email": "Our API integration fails intermittently with 504 errors. It happens roughly 3-4 times per day, usually during peak hours (2-5 PM EST). We're sending POST requests to /api/v2/data/sync with payloads around 2MB. This is blocking our production pipeline."
        },
    ]

    for test in test_emails:
        process_email(test["email"], test["label"])
    
    print("\n" + "="*60)
    print("✅ All scenarios processed successfully!")
    print("="*60)
