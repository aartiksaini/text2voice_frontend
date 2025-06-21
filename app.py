"""
Independent Frontend for TTS Application
Streamlit-based web interface that connects to backend API
"""

import streamlit as st
import requests
import time

# ✅ Use Streamlit secrets instead of os.environ for deployment
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

def get_backend_status():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_supported_languages():
    try:
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('languages', ['en', 'hi'])
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
                if lang not in voices:
                    voices[lang] = []
                voices[lang].append(voice.get('id', 'alloy'))
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
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server. Please ensure the backend is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try with shorter text.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Text-to-Speech Application",
        page_icon="🎵",
        layout="wide"
    )

    st.title("🎵 Text-to-Speech Application")
    st.markdown("*Independent Frontend with Backend API*")

    backend_online = get_backend_status()

    if not backend_online:
        st.error("⚠️ Backend server is not available. Please start the backend service.")
        st.info(f"Expected backend URL: {BACKEND_URL}")
        st.stop()

    supported_languages = get_supported_languages()
    supported_voices = get_supported_voices()

    with st.sidebar:
        st.header("⚙️ Configuration")
        st.success("✅ Backend Connected")

        language = st.selectbox(
            "Select Language",
            options=supported_languages,
            format_func=lambda x: "English" if x == "en" else "Hindi" if x == "hi" else x.upper(),
            help="Choose the language for text-to-speech synthesis"
        )

        available_voices = supported_voices.get(language, ['alloy'])
        voice = st.selectbox(
            "Select Voice",
            options=available_voices,
            help=f"Choose voice for {language.upper()} language"
        )

        st.subheader("🔗 Backend Info")
        st.code(f"{BACKEND_URL}", language="text")

        st.subheader("📡 API Endpoints")
        st.caption("OpenAI-compatible:")
        st.code(f"{BACKEND_URL}/v1/audio/speech", language="text")
        st.caption("Health check:")
        st.code(f"{BACKEND_URL}/health", language="text")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Text Input")
        text_input = st.text_area(
            "Enter text to convert to speech",
            height=150,
            placeholder="Type your text here... (English or Hindi)",
            help="Enter the text you want to convert to speech"
        )

        col_gen1, col_gen2, col_gen3 = st.columns(3)
        with col_gen1:
            generate_btn = st.button("🎵 Generate Speech", type="primary", disabled=not text_input.strip())
        with col_gen2:
            if text_input.strip():
                st.caption(f"Characters: {len(text_input)}")
        with col_gen3:
            if text_input.strip():
                estimated_time = len(text_input) * 0.05
                st.caption(f"Est. time: {estimated_time:.1f}s")

    with col2:
        st.subheader("🎧 Audio Output")
        if generate_btn and text_input.strip():
            with st.spinner("Generating speech..."):
                start_time = time.time()
                audio_data = synthesize_speech(text_input, language, voice)
                if audio_data:
                    generation_time = time.time() - start_time
                    st.audio(audio_data, format="audio/wav")
                    st.success(f"✅ Speech generated in {generation_time:.2f}s")
                    st.caption(f"Audio size: {len(audio_data):,} bytes")
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_data,
                        file_name=f"speech_{language}_{voice}_{int(time.time())}.wav",
                        mime="audio/wav"
                    )

    st.divider()
    st.subheader("🧪 API Testing")

    col_api1, col_api2 = st.columns(2)

    with col_api1:
        st.markdown("**Test Backend API Directly:**")
        api_text = st.text_input("API Test Text", placeholder="Enter text to test API")
        api_voice = st.selectbox("API Test Voice", options=available_voices, key="api_voice")
        test_api_btn = st.button("🔬 Test API", disabled=not api_text.strip())

    with col_api2:
        if test_api_btn and api_text.strip():
            with st.spinner("Testing API..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/v1/audio/speech",
                        json={
                            "model": "tts-1",
                            "input": api_text,
                            "voice": api_voice,
                            "response_format": "wav"
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        st.success("✅ API test successful!")
                        st.audio(response.content, format="audio/wav")
                        st.caption(f"Response size: {len(response.content):,} bytes")
                    else:
                        st.error(f"❌ API test failed: {response.status_code}")
                        if response.text:
                            st.code(response.text)
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend API")
                except Exception as e:
                    st.error(f"❌ API test error: {str(e)}")

    st.divider()
    with st.expander("📊 System Information"):
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown("**Frontend Configuration:**")
            st.json({
                "Backend URL": BACKEND_URL,
                "Frontend Port": 5000,
                "Supported Languages": supported_languages,
                "Connection Status": "Connected" if backend_online else "Disconnected"
            })
        with col_info2:
            st.markdown("**Available Voices:**")
            st.json(supported_voices)

    with st.expander("📖 Usage Instructions"):
        st.markdown("""
        ### How to use this application:

        1. **Ensure Backend is Running**: The backend server must be running
        2. **Select Language**: Choose between English and Hindi in the sidebar
        3. **Select Voice**: Pick from available voices
        4. **Enter Text**: Type or paste your text in the input area
        5. **Generate Speech**: Click the "Generate Speech" button
        6. **Play Audio**: Use the audio player to listen to the result
        7. **Download**: Save the audio file using the download button

        ### API Integration:
        - `GET {BACKEND_URL}/health`
        - `POST {BACKEND_URL}/v1/audio/speech`
        """)

if __name__ == "__main__":
    main()
