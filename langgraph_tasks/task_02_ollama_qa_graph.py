from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

class QAState(TypedDict):
    question: str
    answer: str

llm = ChatOllama(

    model="llama3.2"
)

def answer_question(state: QAState):
    response = llm.invoke(state["question"])

    return {"answer": response.content.strip()}

workflow = StateGraph(QAState)

workflow.add_node("answer_question", answer_question)

workflow.add_edge(START, "answer_question")
workflow.add_edge("answer_question", END)

app = workflow.compile()

result = app.invoke({"question": "What is the capital of Bangladesh?"})

print("Question:", result["question"])
print("Answer:", result["answer"])