"""
Independent Frontend for TTS Application
Streamlit-based web interface that connects to backend API
"""

import streamlit as st
import requests
import time
import io
import os

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def get_backend_status():
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_supported_languages():
    """Get supported languages from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('languages', ['en', 'hi'])
    except:
        pass
    return ['en', 'hi']

def get_supported_voices():
    """Get supported voices from backend"""
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
    """Call backend API to synthesize speech"""
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
    
    # Check backend status
    backend_online = get_backend_status()
    
    if not backend_online:
        st.error("⚠️ Backend server is not available. Please start the backend service.")
        st.info(f"Expected backend URL: {BACKEND_URL}")
        st.stop()
    
    # Get configuration from backend
    supported_languages = get_supported_languages()
    supported_voices = get_supported_voices()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend status
        st.success("✅ Backend Connected")
        
        # Language selection
        language = st.selectbox(
            "Select Language",
            options=supported_languages,
            format_func=lambda x: "English" if x == "en" else "Hindi" if x == "hi" else x.upper(),
            help="Choose the language for text-to-speech synthesis"
        )
        
        # Voice selection
        available_voices = supported_voices.get(language, ['alloy'])
        voice = st.selectbox(
            "Select Voice",
            options=available_voices,
            help=f"Choose voice for {language.upper()} language"
        )
        
        # Backend information
        st.subheader("🔗 Backend Info")
        st.code(f"{BACKEND_URL}", language="text")
        
        # API endpoint information
        st.subheader("📡 API Endpoints")
        st.caption("OpenAI-compatible:")
        st.code(f"{BACKEND_URL}/v1/audio/speech", language="text")
        st.caption("Health check:")
        st.code(f"{BACKEND_URL}/health", language="text")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Text Input")
        
        # Text input area
        text_input = st.text_area(
            "Enter text to convert to speech",
            height=150,
            placeholder="Type your text here... (English or Hindi)",
            help="Enter the text you want to convert to speech"
        )
        
        # Generation controls
        col_gen1, col_gen2, col_gen3 = st.columns(3)
        
        with col_gen1:
            generate_btn = st.button(
                "🎵 Generate Speech",
                type="primary",
                disabled=not text_input.strip()
            )
        
        with col_gen2:
            if text_input.strip():
                st.caption(f"Characters: {len(text_input)}")
        
        with col_gen3:
            if text_input.strip():
                estimated_time = len(text_input) * 0.05  # Rough estimate
                st.caption(f"Est. time: {estimated_time:.1f}s")
    
    with col2:
        st.subheader("🎧 Audio Output")
        
        # Audio generation and playback
        if generate_btn and text_input.strip():
            with st.spinner("Generating speech..."):
                start_time = time.time()
                
                # Generate audio using backend API
                audio_data = synthesize_speech(text_input, language, voice)
                
                if audio_data:
                    generation_time = time.time() - start_time
                    
                    # Display audio player
                    st.audio(audio_data, format="audio/wav")
                    
                    # Success message with stats
                    st.success(f"✅ Speech generated in {generation_time:.2f}s")
                    st.caption(f"Audio size: {len(audio_data):,} bytes")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_data,
                        file_name=f"speech_{language}_{voice}_{int(time.time())}.wav",
                        mime="audio/wav"
                    )
    
    # API Testing Section
    st.divider()
    st.subheader("🧪 API Testing")
    
    col_api1, col_api2 = st.columns(2)
    
    with col_api1:
        st.markdown("**Test Backend API Directly:**")
        
        api_text = st.text_input(
            "API Test Text",
            placeholder="Enter text to test API",
            help="Test the backend API endpoint directly"
        )
        
        api_voice = st.selectbox(
            "API Test Voice",
            options=available_voices,
            key="api_voice"
        )
        
        test_api_btn = st.button("🔬 Test API", disabled=not api_text.strip())
    
    with col_api2:
        if test_api_btn and api_text.strip():
            with st.spinner("Testing API..."):
                try:
                    # Test the API endpoint directly
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
    
    # System Information
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
    
    # Usage Instructions
    with st.expander("📖 Usage Instructions"):
        st.markdown("""
        ### How to use this application:
        
        1. **Ensure Backend is Running**: The backend server must be running on port 8000
        2. **Select Language**: Choose between English and Hindi in the sidebar
        3. **Select Voice**: Pick from available voices for your chosen language
        4. **Enter Text**: Type or paste your text in the input area
        5. **Generate Speech**: Click the "Generate Speech" button
        6. **Play Audio**: Use the audio player to listen to the generated speech
        7. **Download**: Save the audio file using the download button
        
        ### API Integration:
        
        This frontend connects to a backend API that provides OpenAI-compatible endpoints:
        
        ```bash
        # Health check
        GET http://localhost:8000/health
        
        # Text-to-speech synthesis
        POST http://localhost:8000/v1/audio/speech
        ```
        
        ### Architecture:
        
        - **Frontend**: Streamlit web interface (this application)
        - **Backend**: Flask API server with TTS processing
        - **Communication**: REST API calls with JSON payloads
        """)

if __name__ == "__main__":
    main()