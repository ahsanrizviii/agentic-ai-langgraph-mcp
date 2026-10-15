# LangGraph Tasks

Eight self-contained scripts, each demonstrating one LangGraph pattern. Run any of them from the repository root after `pip install -r requirements.txt`.

| # | Script | Pattern | Needs |
|---|---|---|---|
| 01 | `task_01_bmi_calculator_langgraph.py` | Sequential two-node graph with typed state | — |
| 02 | `task_02_ollama_qa_graph.py` | Single LLM node | Ollama |
| 03 | `task_03_resume_analyzer_parallel.py` | Parallel fan-out / fan-in | — |
| 04 | `task_04_student_score_router.py` | Conditional routing | — |
| 05 | `task_05_iterative_answer_improvement.py` | Generate → evaluate → improve loop (LLM-as-judge) | Ollama |
| 06 | `task_06_tool_agent_chatbot.py` | ReAct-style tool agent (`ToolNode` + `tools_condition`) | Ollama, internet |
| 07 | `task_07_ltm_postgres_memory.py` | Short-term + long-term memory (`InMemorySaver` + `PostgresStore`) | Ollama, PostgreSQL |
| 08 | `task_08_rag_local_llm.py` | RAG with FAISS + retrieval-configuration benchmark | Ollama, a PDF |

```bash
python langgraph_tasks/task_01_bmi_calculator_langgraph.py
```

## Prerequisites

- **Ollama** with the models used here:
  ```bash
  ollama pull llama3.2
  ollama pull nomic-embed-text   # embeddings for task 08
  ```
- **PostgreSQL** for task 07. Create a database called `chatmemory`, or point `DB_URI` somewhere else:
  ```bash
  export DB_URI="postgresql://postgres:postgres@localhost:5432/chatmemory"
  ```
  Tables are created automatically on first run. Type `quit` or `exit` to leave the chat.
- **A PDF** for task 08 — see [`data/README.md`](data/README.md).

Expected output from the offline tasks:

```text
task_01  →  BMI: 22.86 | Recommendation: Maintain current healthy lifestyle
task_03  →  Skills: Python found | Experience: Technical experience found | Education: Bachelor's degree found
task_04  →  Score: 12 | Level: low | Advice: Study more and practice the weak topics.
```
