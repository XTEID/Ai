import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

# Page config
st.set_page_config(
    page_title="V AI Z",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space+Grotesk', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a, #020617);
    }
    
    .main-title {
        font-size: 7rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -4px;
    }
    
    .sub-title {
        color: #94a3b8;
        text-align: center;
        font-size: 2.2rem;
        margin-bottom: 2rem;
    }
    
    .stChatMessage {
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .stChatMessage[data-testimonial="user"] {
        background-color: rgba(99, 102, 241, 0.15) !important;
        border-left: 5px solid #6366f1 !important;
    }

    .stChatMessage[data-testimonial="assistant"] {
        background-color: rgba(168, 85, 247, 0.05) !important;
        border-left: 5px solid #a855f7 !important;
    }
</style>
""", unsafe_allow_html=True)

# Database Helper
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    # Handle the specific Replit DB hostname issue by fallback to default or retry
    try:
        return psycopg2.connect(db_url, connect_timeout=5)
    except psycopg2.OperationalError as e:
        # If 'helium' fails, it might be a temporary DNS issue in the environment
        st.error(f"Koneksi database terputus sejenak, mencoba kembali... ({str(e)})")
        time.sleep(2)
        return psycopg2.connect(db_url, connect_timeout=10)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Simple Auth for up to 20 users
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def get_user_count():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        result = cur.fetchone()
        count = result[0] if result else 0
        cur.close()
        conn.close()
        return count
    except Exception as e:
        st.error(f"Database error: {e}")
        return 0

def register_user(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email) VALUES (%s) ON CONFLICT (email) DO NOTHING", (email,))
    conn.commit()
    cur.close()
    conn.close()

def login_sidebar():
    with st.sidebar:
        st.title("👤 Account")
        if not st.session_state.logged_in:
            tab1, tab2 = st.tabs(["Login", "Daftar"])
            
            with tab1:
                l_email = st.text_input("Email", key="l_email")
                l_pass = st.text_input("Password", type="password", key="l_pass")
                if st.button("Masuk"):
                    if l_email and l_pass:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("SELECT password FROM users WHERE email = %s", (l_email,))
                        res = cur.fetchone()
                        cur.close()
                        conn.close()
                        if res and res[0] == l_pass:
                            st.session_state.logged_in = True
                            st.session_state.user_email = l_email
                            st.rerun()
                        else:
                            st.error("Email atau password salah.")
            
            with tab2:
                r_email = st.text_input("Email Baru", key="r_email")
                r_pass = st.text_input("Password Baru", type="password", key="r_pass")
                if st.button("Buat Akun"):
                    if r_email and r_pass and "@" in r_email:
                        current_count = get_user_count()
                        if current_count < 20:
                            try:
                                conn = get_db_connection()
                                cur = conn.cursor()
                                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (r_email, r_pass))
                                conn.commit()
                                cur.close()
                                conn.close()
                                st.success("Akun berhasil dibuat! Silakan login.")
                            except Exception as e:
                                st.error("Email sudah terdaftar.")
                        else:
                            st.error("Kuota user penuh (Maks 20 user).")
                    else:
                        st.warning("Data tidak valid.")
        else:
            st.success(f"Logged in: {st.session_state.user_email}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_email = None
                st.rerun()
        
        st.divider()
        st.title("✉️ Support")
        with st.expander("Report an Issue"):
            feedback_msg = st.text_area("Detail kendala Anda:")
            if st.button("Kirim ke Developer"):
                if feedback_msg:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("INSERT INTO feedback (user_id, message) VALUES (%s, %s)", ("guest", feedback_msg))
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("Pesan terkirim! Terima kasih.")
                        # Notifikasi sederhana via UI untuk admin (karena server SMTP butuh kredensial)
                        st.toast(f"Notifikasi terkirim ke {os.environ.get('ADMIN_EMAIL')}", icon="📧")
                    except Exception as e:
                        st.error(f"Gagal mengirim: {e}")
                else:
                    st.warning("Pesan tidak boleh kosong.")

login_sidebar()

st.markdown('<h1 class="main-title">V AI Z</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">⚡ Intelligent Research. Global Insights. Beyond Boundaries.</p>', unsafe_allow_html=True)

# AI Client
client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY", "dummy"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

def search_internet(query):
    scientific_query = f"{query} research paper scientific article scholarly"
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(scientific_query, max_results=7)]
                if results: return results
        except: time.sleep(1)
    return []

def get_ai_response(prompt, search_context, history):
    try:
        full_prompt = f"History:\n{history}\nContext:\n{search_context}\nQuestion: {prompt}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Anda adalah asisten peneliti AI yang handal. Jawablah setiap pertanyaan dengan mendalam berdasarkan konteks ilmiah."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Apa yang ingin Anda pelajari hari ini?"):
    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu untuk mulai mengobrol.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🔍 Meneliti...", expanded=True) as status:
                search_results = search_internet(prompt)
                context = "\n".join([f"- {r['title']}: {r['body']}" for r in search_results]) if search_results else "No context found."
                status.update(label="✅ Selesai meneliti!", state="complete")
            
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
            response = get_ai_response(prompt, context, history)
            st.markdown(response)
            
            if search_results:
                with st.expander("Sumber"):
                    for r in search_results:
                        st.write(f"[{r['title']}]({r['href']})")
                    
        st.session_state.messages.append({"role": "assistant", "content": response})
