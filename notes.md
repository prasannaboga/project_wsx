                  RAG - Pdf Example

                  ┌─────────────┐
                  │  config.yaml│
                  └──────┬──────┘
                        │
                  ┌──────▼────────┐
                  │ ExtractSvc    │  → PDF → text chunks
                  │ (PDF parsing) │
                  └──────┬────────┘
                        │
                  ┌──────▼────────┐
                  │ EmbedSvc      │  → text → embeddings
                  │ (local model) │
                  └──────┬────────┘
                        │
                  ┌──────▼────────┐
                  │ Vector Store  │  → FAISS / Chroma
                  │ (storage)     │
                  └──────┬────────┘
                        │
                  ┌──────▼────────┐
                  │ RAG API       │  → query → context → LLM
                  │ (FastAPI)     │
                  └───────────────┘


                 +-------------------+
                 | Auth0 OAuth       |
                 |-------------------|
                 | /authorize        |
                 | /oauth/token      |
                 | /jwks.json        |
                 +---------+---------+
                           │
                           │ JWT
                           ▼
                  +----------------+
                  | Python MCP     |
                  |----------------|
                  | verify JWT     |
                  | expose tools   |
                  +--------+-------+
                           │
                           ▼
                       AI Clients
               (Postman / Cursor / Claude)


                  Postman / Cursor
                        │
                        │ 1. Call MCP
                        ▼
                  POST /mcp
                        │
                        │ 401 + WWW-Authenticate
                        ▼
                  Client shows "Authorize" button
                        │
                        ▼
                  GET /authorize (browser login)
                        │
                        ▼
                  Auth0 login
                        │
                        ▼
                  Redirect to client
                        │
                        ▼
                  POST /oauth/token
                        │
                        ▼
                  Access Token
                        │
                        ▼
                  Call MCP with Bearer token
