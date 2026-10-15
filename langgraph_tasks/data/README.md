# RAG source document

`task_08_rag_local_llm.py` loads `langgraph_tasks/data/smart.pdf` by default.

The script's eight test questions are written for the **Smart Soldering Workbench & Safety Guardian** project report (STM32, MQ-135, HiveMQ, Google Sheets…). Download that report from the [smart-soldering-station-iot](https://github.com/rysahona12/smart-soldering-station-iot) repository, save it here as `smart.pdf`, and run the script.

To query a different PDF, set `RAG_PDF_PATH` and replace `test_questions` with question/keyword pairs that match it:

```bash
export RAG_PDF_PATH=/path/to/your.pdf     # Windows PowerShell: $env:RAG_PDF_PATH="D:\your.pdf"
python langgraph_tasks/task_08_rag_local_llm.py
```
