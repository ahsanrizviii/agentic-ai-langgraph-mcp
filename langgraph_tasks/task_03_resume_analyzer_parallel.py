from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class ResumeState(TypedDict):
    resume: str
    skills: str
    experience: str
    education: str

resume = """Ahsan Rizvi. BSc in Computer Science. 6 months of experience as a Python developer as well as SQL.
            Worked on Django, Data scrapping and ML projects."""

def analyze_skills(state: ResumeState):
    resume = state["resume"].lower()

    if "python" in resume:
        skills = "Python found"
    else:
        skills = "Python not found"

    return {"skills": skills}


def analyze_experience(state: ResumeState):
    resume = state["resume"].lower()

    if "developer" in resume or "engineer" in resume:
        experience = "Technical experience found"
    else:
        experience = "Technical experience not found"

    return {"experience": experience}


def analyze_education(state: ResumeState):
    resume = state["resume"].lower()

    if "bsc" in resume or "bachelor" in resume:
        education = "Bachelor's degree found"
    else:
        education = "Bachelor's degree not found"

    return {"education": education}


workflow = StateGraph(ResumeState)

workflow.add_node("skills", analyze_skills)
workflow.add_node("experience", analyze_experience)
workflow.add_node("education", analyze_education)

workflow.add_edge(START, "skills")
workflow.add_edge(START, "experience")
workflow.add_edge(START, "education")

workflow.add_edge("skills", END)
workflow.add_edge("experience", END)
workflow.add_edge("education", END)

app = workflow.compile()



result = app.invoke({"resume": resume})

print("Skills:", result["skills"])
print("Experience:", result["experience"])
print("Education:", result["education"])