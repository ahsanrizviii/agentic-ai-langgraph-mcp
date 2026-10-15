from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class BMIState(TypedDict):
    weight: float
    height: float
    bmi: float
    recommendation: str

def calculate_bmi(state: BMIState):
    bmi = state["weight"] / (state["height"] ** 2)

    return { "bmi": round(bmi, 2)}

def recommend_bmi(state: BMIState):
    bmi = state["bmi"]

    if bmi < 18.5:
        recommendation = "You have to gain weight"
    elif bmi <= 24.9:
        recommendation = "Maintain current healthy lifestyle"
    elif bmi <= 29.9:
        recommendation = "You should start focusing on your weight"
    else:
        recommendation = "You must lose weight"

    return {"recommendation": recommendation}

workflow = StateGraph(BMIState)

workflow.add_node("calculate_bmi", calculate_bmi)
workflow.add_node("recommend_bmi", recommend_bmi)

workflow.add_edge(START, "calculate_bmi")
workflow.add_edge("calculate_bmi", "recommend_bmi")
workflow.add_edge("recommend_bmi", END)

app = workflow.compile()

result = app.invoke({"weight":70,"height": 1.75})

print("BMI:", result["bmi"])
print("Recommendation:", result["recommendation"])
