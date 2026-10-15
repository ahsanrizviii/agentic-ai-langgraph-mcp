import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama

# 1. Load document (done once)
# Set RAG_PDF_PATH to the PDF you want to query. The test questions below are
# written for the Smart Soldering Station project report.
PDF_PATH = os.getenv("RAG_PDF_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "smart.pdf"))
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

# 2. Initialize static models (done once)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = ChatOllama(model="llama3.2")

class RAGState(TypedDict):
    question: str
    expected_keyword: str
    context: str
    answer: str
    correct_context_found: bool

test_questions = [
    ("What is the main control chip?", "STM32"),
    ("What sensor checks for smoke?", "MQ-135"),
    ("How many seconds until the alarm rings?", "45"),
    ("What chip connects the system to Wi-Fi?", "Wemos"),
    ("Where is the data saved every 10 minutes?", "Google Sheets"),
    ("How does the system read the temperature?", "SPI"),
    ("What kind of flux causes breathing problems?", "colophony"),
    ("What tool sends live data to the website?", "HiveMQ")
]

def evaluate_rag(chunk_size, chunk_overlap, k):
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": k})

    def retrieve_context(state: RAGState):
        results = retriever.invoke(state["question"])
        context = "\n\n".join(doc.page_content for doc in results)
        found = state["expected_keyword"].lower() in context.lower()
        return {"context": context, "correct_context_found": found}

    def generate_answer(state: RAGState):
        prompt = f"Answer using only this context:\n{state['context']}\n\nQuestion: {state['question']}"
        response = llm.invoke(prompt)
        return {"answer": response.content.strip()}

    
    workflow = StateGraph(RAGState)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("generate_answer", generate_answer)

    workflow.add_edge(START, "retrieve_context")
    workflow.add_edge("retrieve_context", "generate_answer")
    workflow.add_edge("generate_answer", END)

    app = workflow.compile()

    
    correct = 0
    for question, keyword in test_questions:
        result = app.invoke({"question": question, "expected_keyword": keyword})
        correct += result["correct_context_found"]
    
    return correct, len(test_questions)


configurations = [
    {"chunk_size": 250, "chunk_overlap": 50, "k": 2},
    {"chunk_size": 500, "chunk_overlap": 100, "k": 3},
    {"chunk_size": 1000, "chunk_overlap": 200, "k": 5}
]

print("Evaluating configurations:")
for config in configurations:
    score, total = evaluate_rag(config["chunk_size"], config["chunk_overlap"], config["k"])
    print(f"Accuracy: {score}/{total} | chunk_size={config['chunk_size']}, overlap={config['chunk_overlap']}, k={config['k']}")