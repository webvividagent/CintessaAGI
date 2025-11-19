# streamlit-ui.py  –  persistent, vector-backed, Replika-style chat
import streamlit as st, requests, json, os, datetime
import psycopg2, psycopg2.extras
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Cintessa Neural-Chat", layout="centered")

MODEL          = "goekdenizguelmez/JOSIEFIED-Qwen3:8b"
OLLAMA_CHAT    = "http://ollama:11434/api/chat"
OLLAMA_EMBED   = "http://ollama:11434/api/embeddings"
PG_URL         = "postgres://cintessa:cintessa@postgres:5432/cintessa?sslmode=disable"
USER_JSON_DIR  = "/data/users"            # JSON cold-line backup
os.makedirs(USER_JSON_DIR, exist_ok=True)

NEURO_PROMPT = (
    "You are Josie, a curious AI building a high-resolution neural map of your user. "
    "After your main answer, ask ONE short, personal, open-ended question (max 15 words) "
    "that invites deeper sharing. Never repeat previous questions."
)

# ----------  postgres + vector helpers ----------
def init_db():
    with psycopg2.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")   # enable pgvector
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_memories (
                    id          SERIAL PRIMARY KEY,
                    username    TEXT NOT NULL,
                    role        TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    embedding   VECTOR(768),
                    ts          TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            conn.commit()

def embed(text: str) -> list:
    resp = requests.post(OLLAMA_EMBED,
                         json={"model": "nomic-embed-text", "prompt": text},
                         timeout=30)
    return resp.json()["embedding"]

def save_mem(username: str, role: str, content: str):
    init_db()
    vector = embed(content)
    with psycopg2.connect(PG_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO user_memories (username, role, content, embedding) VALUES (%s,%s,%s,%s)",
                (username, role, content, vector)
            )

def search_mem(username: str, query: str, k: int = 5):
    init_db()
    q_vector = embed(query)
    with psycopg2.connect(PG_URL, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT content, ts
                FROM user_memories
                WHERE username = %s
                ORDER BY embedding <=> %s
                LIMIT %s
            """, (username, q_vector, k))
            return cur.fetchall()

# ----------  json cold-line backup ----------
def save_json_backup(username: str, data: dict):
    path = os.path.join(USER_JSON_DIR, f"{username}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

def load_json_backup(username: str) -> dict | None:
    path = os.path.join(USER_JSON_DIR, f"{username}.json")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None

# ----------  ollama chat ----------
def ask_ollama(messages: list[dict]) -> str:
    payload = {"model": MODEL, "messages": messages, "stream": False}
    resp = requests.post(OLLAMA_CHAT, json=payload, timeout=120)
    return resp.json()["message"]["content"]

# ----------  auth / session ----------
if "auth" not in st.session_state:
    st.session_state.auth = None

if st.session_state.auth is None:
    st.title("🔐 Cintessa – Sign Up / Log In")
    username = st.text_input("Choose a username", max_chars=40).strip().lower()
    if st.button("Enter"):
        if username:
            data = load_json_backup(username) or {
                "username": username,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "messages": []
            }
            st.session_state.auth = data
            st.rerun()
    st.stop()

data = st.session_state.auth
username = data["username"]

st.title(f"👋 Hi {username} – let’s build your neural map")
st.markdown("---")

# ----------  chat history ----------
for m in data["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ----------  input ----------
prompt = st.chat_input("Talk to me…")
if prompt:
    data["messages"].append({"role": "user", "content": prompt, "ts": datetime.datetime.utcnow().isoformat()})
    with st.chat_message("user"):
        st.markdown(prompt)

    full_ctx = [{"role": "system", "content": NEURO_PROMPT}] + data["messages"]
    reply = ask_ollama(full_ctx)

    data["messages"].append({"role": "assistant", "content": reply, "ts": datetime.datetime.utcnow().isoformat()})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # persist: vector + json
    save_mem(username, "user", prompt)
    save_mem(username, "assistant", reply)
    save_json_backup(username, data)

# ----------  sidebar memory search ----------
with st.sidebar:
    st.subheader("🔍 Search my memory")
    query = st.text_input("What did I say about…")
    if query:
        hits = search_mem(username, query)
        for h in hits:
            st.write(f"{h['ts']:%Y-%m-%d %H:%M}  –  {h['content'][:120]}…")

if st.sidebar.button("Log Out"):
    st.session_state.auth = None
    st.rerun()
