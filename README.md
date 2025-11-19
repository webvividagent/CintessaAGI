# CintessaAGI  
> A personal AI companion that builds a **neural map of you** using Ollama + pg-vector + Streamlit.

## What it does
- Chat via **Ollama** (any GGUF model)
- **Persistent memory**: every message is embedded (`nomic-embed-text`) and stored in **Postgres + pgvector** for semantic recall
- **Replika-style questions**: bot asks deepening questions after each reply → bigger conversation tensor
- **Multi-user**: sign-up / log-in, vector search sidebar ("What did I say about dogs?")
- **GPU ready**: single-command NVIDIA stack

## Quick start (GPU)
```bash
git clone https://github.com/yourname/CintessaAGI.git && cd CintessaAGI
docker exec -it cintessaagi-ollama-1 ollama pull goekdenizguelmez/JOSIEFIED-Qwen3:8b
docker exec -it cintessaagi-ollama-1 ollama pull nomic-embed-text
docker compose -f docker-compose.gpu.yaml up -d
open http://localhost:8501          # Streamlit UI
