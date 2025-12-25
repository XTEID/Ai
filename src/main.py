import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS
import os
import time

# Page config
st.set_page_config(page_title="AI Internet Explorer", page_icon="🌐", layout="wide")

st.title("🌐 AI Internet Explorer")
st.markdown("Saya adalah AI yang dapat membantu Anda mempelajari informasi dari seluruh internet tanpa kendala.")

# Initialize OpenAI client using Replit AI Integration
# Using environment variables provided by the integration
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY", "dummy")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

def search_internet(query):
    """Search internet with error handling and retries."""
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
                if results:
                    return results
        except Exception as e:
            if attempt == 2:
                st.error(f"Gagal mencari di internet: {str(e)}")
                return []
            time.sleep(1)
    return []

def get_ai_response(prompt, search_context):
    """Get AI response with error handling."""
    try:
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # However, gpt-4o is currently very stable for this integration.
        full_prompt = f"""
        Anda adalah AI yang berpengetahuan luas. Gunakan informasi pencarian berikut untuk menjawab pertanyaan pengguna secara akurat.
        
        Konteks Pencarian:
        {search_context}
        
        Pertanyaan: {prompt}
        
        Jawaban (dalam Bahasa Indonesia):
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Anda adalah asisten AI yang membantu, cerdas, dan teliti."},
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
