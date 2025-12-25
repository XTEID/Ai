import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import os
import time

# Page config
st.set_page_config(
    page_title="V AI Z",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space+Grotesk', sans-serif;
    }
    
    .main {
        background-color: #0e1117;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a, #020617);
    }
    
    /* Header styling */
    .main-title {
        font-size: 4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .sub-title {
        color: #94a3b8;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Chat message styling */
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
    
    /* Status box styling */
    .stStatusWidget {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* References styling */
    .stExpander {
        border: none !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
    }
    
    /* Input area styling */
    .stChatInputContainer {
        padding-bottom: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">V AI Z</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">⚡ Intelligent Research. Global Insights. Beyond Boundaries.</p>', unsafe_allow_html=True)

# Initialize OpenAI client using Replit AI Integration
# Using environment variables provided by the integration
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY", "dummy")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

def search_internet(query):
    """Search internet with scientific focus and error handling."""
    # Menambahkan keyword penelitian untuk hasil yang lebih akademis
    scientific_query = f"{query} research paper scientific article scholarly"
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(scientific_query, max_results=7)]
                if results:
                    return results
        except Exception as e:
            if attempt == 2:
                st.error(f"Gagal mencari di internet: {str(e)}")
                return []
            time.sleep(1)
    return []

def get_ai_response(prompt, search_context):
    """Get AI response with research focus and ethical compliance."""
    try:
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        full_prompt = f"""
        Anda adalah AI Peneliti Senior yang ahli dalam menganalisis karya ilmiah global.
        
        Tugas Anda:
        1. Jawablah SETIAP pertanyaan pengguna dengan informasi yang relevan dan mendalam. Jika konteks pencarian tidak mencukupi, gunakan pengetahuan internal Anda untuk memberikan jawaban yang paling membantu.
        2. Berikan kesimpulan yang akurat, objektif, dan mendalam berdasarkan konteks pencarian.
        3. Pastikan seluruh jawaban mematuhi koridor hukum dan etika penelitian internasional.
        4. Hindari segala bentuk saran atau konten yang melanggar hukum (bebas dari tindak pidana).
        5. Gunakan bahasa ilmiah yang mudah dipahami namun tetap formal.
        
        Konteks Pencarian Ilmiah:
        {search_context}
        
        Pertanyaan Peneliti: {prompt}
        
        Kesimpulan Ilmiah (Bahasa Indonesia):
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Anda adalah asisten peneliti AI yang selalu memberikan jawaban atas setiap input pengguna dengan integritas ilmiah dan kepatuhan hukum."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "FREE_CLOUD_BUDGET_EXCEEDED" in error_msg:
            st.error("Budget cloud gratis telah terlampaui. Mohon tunggu beberapa saat.")
        else:
            st.error(f"Terjadi kesalahan pada AI: {error_msg}")
        return "Maaf, saya mengalami kendala teknis saat memproses jawaban."

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Apa yang ingin Anda pelajari hari ini?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 Mencari informasi terbaru...", expanded=True) as status:
            search_results = search_internet(prompt)
            if search_results:
                context = "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in search_results])
                status.update(label="✅ Informasi ditemukan! Menganalisis...", state="complete")
            else:
                context = "Tidak ada hasil pencarian yang ditemukan."
                status.update(label="⚠️ Tidak menemukan informasi spesifik, mencoba menjawab dengan pengetahuan internal...", state="complete")
        
        response = get_ai_response(prompt, context)
        st.markdown(response)
        
        # Add references if available
        if search_results:
            with st.expander("Sumber Informasi"):
                for r in search_results:
                    st.write(f"[{r['title']}]({r['href']})")
                
    st.session_state.messages.append({"role": "assistant", "content": response})
