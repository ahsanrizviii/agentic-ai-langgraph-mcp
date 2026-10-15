from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

class AnswerState(TypedDict):
    question: str
    answer: str
    score: int
    feedback: str
    iteration: int

llm = ChatOllama(model="llama3.2",temperature=0)

question = "State one advantage of drinking diet coke"

def generate_answer(state: AnswerState):

    response = llm.invoke(f"""Answer the following question properly:{state["question"]}. 
    Give a short and clear answer.""")

    print(f"Iteration: {state['iteration']}")
    print(".....")
    print("Answer generated")
    print(response.content.strip())

    return {"answer": response.content.strip()}

def evaluate_answer(state: AnswerState):

    response = llm.invoke(f"""Rate the following answer between 1 and 10 and give short feedback.

    This is the question: {state["question"]}
    This is the answer: {state["answer"]}

    Use the following format below:

    Score: [your score]
    Feedback: [your feedback]

    Keep things concise and don't write anything else""")

    text = response.content.strip()

    score = 1
    feedback = ""

    lines = response.content.strip().splitlines()

    score = int(lines[0].split(":")[1].strip())
    feedback = lines[1].split(":", 1)[1].strip()

    print(f"Score: {score}")
    print(f"Feedback: {feedback}")

    return {
        "score": score,
        "feedback": feedback
    }

def improve_answer(state: AnswerState):

    response = llm.invoke(f"""Improve this answer based on the feedback. Write only the improved answer.

                                Question: {state["question"]}
                                Answer: {state["answer"]}
                                Score: {state["score"]}
                                Feedback: {state["feedback"]}""")

    print(f"\nIteration: {state['iteration'] + 1}")
    print(".....")
    print("Answer improved")
    print(response.content.strip())

    return {
        "answer": response.content.strip(),
        "iteration": state["iteration"] + 1
    }


def router(state: AnswerState):

    if state["score"] >= 9:
        return "finish"

    if state["iteration"] >= 5:
        return "finish"

    return "improve"


workflow = StateGraph(AnswerState)

workflow.add_node("generate", generate_answer)
workflow.add_node("evaluate", evaluate_answer)
workflow.add_node("improve", improve_answer)

workflow.add_edge(START, "generate")
workflow.add_edge("generate", "evaluate")

workflow.add_conditional_edges(
    "evaluate",
    router,
    {
        "finish": END,
        "improve": "improve"
    }
)

workflow.add_edge("improve", "evaluate")

app = workflow.compile()


result = app.invoke({
    "question": question,
    "answer": "",
    "score": 0,
    "feedback": "",
    "iteration": 1
})


print("\nFinal Answer:")
print("--------------")
print(result["answer"])