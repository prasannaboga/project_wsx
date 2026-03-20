# Project WSX

### Terminal Commands

activate shell
```shell
eval $(poetry env activate)
```

running fastapi server
```
fastapi dev -e src.project_wsx.main:app --port 8101
```

production
```
PYTHONPATH=src gunicorn project_wsx.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8101 --workers 4 --log-level debug --timeout 120
```

run sample mcp server

```shell
poetry run t11_sample_mcp_server --transport streamable-http
poetry run t12_task_mcp_server --transport streamable-http
```

install sample mcp server

```shell
mcp install --with /Users/prasannaboga/Projects/project_wsx --with "mcp[cli]" src/project_wsx/scripts/t11_sample_mcp_server.py
mcp install --with /Users/prasannaboga/Projects/project_wsx --with "mcp[cli]" src/project_wsx/scripts/t12_task_mcp_server.py
```

run sample streamlit

```shell
poetry run streamlit run src/project_wsx/scripts/t11_streamlit_mcp_client.py
poetry run streamlit run src/project_wsx/scripts/t12_task_mcp_client.py
```


RAG Example 
```
poetry run t09_bootstrap_ingest
```
