from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class StudentState(TypedDict):
    score: int
    level: str
    advice: str

def check_score(state: StudentState):
    score = state["score"]

    if score < 50:
        level = "low"
    elif score < 80:
        level = "medium"
    else:
        level = "high"

    return {"level": level}


def route_score(state: StudentState):
    return state["level"]

def low_score(state: StudentState):
    return {"advice": "Study more and practice the weak topics."}

def medium_score(state: StudentState):
    return {"advice": "Keep practicing and review your mistakes."}

def high_score(state: StudentState):
    return {"advice": "Great job! Keep up the good work."}

workflow = StateGraph(StudentState)

workflow.add_node("check_score", check_score)
workflow.add_node("low", low_score)
workflow.add_node("medium", medium_score)
workflow.add_node("high", high_score)

workflow.add_edge(START, "check_score")

workflow.add_conditional_edges(
    "check_score",
    route_score,
    {
        "low": "low",
        "medium": "medium",
        "high": "high",
    },
)

workflow.add_edge("low", END)
workflow.add_edge("medium", END)
workflow.add_edge("high", END)

app = workflow.compile()

result = app.invoke({"score": 12})

print("Score:", result["score"])
print("Level:", result["level"])
print("Advice:", result["advice"])