import streamlit as st
import requests
import time
import os

# Get backend URL from Streamlit secrets or environment
BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))

def get_backend_status():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.warning(f"Backend connection failed: {e}")
        return False

def get_supported_languages():
    try:
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        if response.status_code == 200:
            return response.json().get('languages', ['en', 'hi'])
    except:
        pass
    return ['en', 'hi']

def get_supported_voices():
    try:
        response = requests.get(f"{BACKEND_URL}/v1/voices", timeout=5)
        if response.status_code == 200:
            data = response.json()
            voices = {}
            for voice in data.get('voices', []):
                lang = voice.get('language', 'en')
                voices.setdefault(lang, []).append(voice.get('id', 'alloy'))
            return voices
    except:
        pass
    return {
        'en': ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        'hi': ['hindi_voice', 'alloy']
    }

def synthesize_speech(text, language, voice):
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/audio/speech",
            json={
                "model": "tts-1",
                "input": text,
                "voice": voice,
                "response_format": "wav"
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Backend error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
    return None

def main():
    st.set_page_config(page_title="Text-to-Speech Application", page_icon="🎵", layout="wide")
    st.title("🎵 Text-to-Speech Application")

    backend_online = get_backend_status()

    if not backend_online:
        st.error("⚠️ Backend server is not available.")
        st.info(f"Expected backend URL: `{BACKEND_URL}`")
        st.stop()

    supported_languages = get_supported_languages()
    supported_voices = get_supported_voices()

    with st.sidebar:
        st.header("⚙️ Configuration")
        st.success("✅ Backend Connected")
        language = st.selectbox(
            "Select Language",
            supported_languages,
            format_func=lambda x: "English" if x == "en" else "Hindi" if x == "hi" else x.upper()
        )
        available_voices = supported_voices.get(language, ['alloy'])
        voice = st.selectbox("Select Voice", available_voices)
        st.subheader("🔗 Backend Info")
        st.code(BACKEND_URL, language="text")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📝 Text Input")
        text_input = st.text_area("Enter text to convert to speech", height=150)
        col_gen1, col_gen2, col_gen3 = st.columns(3)
        with col_gen1:
            generate_btn = st.button("🎵 Generate Speech", type="primary", disabled=not text_input.strip())
        with col_gen2:
            if text_input.strip():
                st.caption(f"Characters: {len(text_input)}")
        with col_gen3:
            if text_input.strip():
                st.caption(f"Est. time: {len(text_input)*0.05:.1f}s")

    with col2:
        st.subheader("🎧 Audio Output")
        if generate_btn and text_input.strip():
            with st.spinner("Generating speech..."):
                start_time = time.time()
                audio_data = synthesize_speech(text_input, language, voice)
                if audio_data:
                    st.audio(audio_data, format="audio/wav")
                    st.success(f"✅ Speech generated in {time.time() - start_time:.2f}s")
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_data,
                        file_name=f"speech_{language}_{voice}_{int(time.time())}.wav",
                        mime="audio/wav"
                    )

if __name__ == "__main__":
    main()
