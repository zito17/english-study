import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
import os

# FFmpeg 상세 경로 설정
ffmpeg_path = r"C:\ffmpeg_windows\ffmpeg-8.1.2-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path
AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg.exe")

st.set_page_config(page_title="전문 영어 발음 교정 AI", page_icon="🎤")
st.title("🎤 전문 영어 발음 분석 및 교정")

# API 키 입력
api_key = st.sidebar.text_input("Google API Key", type="password")

uploaded_file = st.file_uploader("음성 파일 업로드 (m4a, mp3, wav)", type=['wav', 'm4a', 'mp3'])

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    try:
        st.markdown("### 🎧 내 발음 다시 듣기")
        st.audio(uploaded_file)

        temp_filename = "temp_audio_file"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info("AI가 언어학적 관점에서 발음을 정밀 분석 중입니다...")
        
        sound = AudioSegment.from_file(temp_filename)
        sound.export("converted_for_ai.wav", format="wav")
        audio_source = "converted_for_ai.wav"

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_source) as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language="en-US")

        st.success(f"🤖 인식된 문장: {recognized_text}")

        # 언어학 전문성 강화 프롬프트
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        너는 언어학 박사 학위를 가진 전문 영어 발음 코치야. 
        다음 인식된 문장을 바탕으로 학생의 발음을 정밀 분석해줘.
        인식된 문장: '{recognized_text}'

        [분석 항목]
        1. 종합 발음 점수: 정확도, 유창성, 강세를 종합하여 100점 만점으로 평가.
        2. 음성학적 정밀 진단: R vs L 구분, Th 발음, F/V 소리 등 주요 자음과 모음의 조음 정확성.
        3. 음절 강세 및 억양: 단어의 강세(Word Stress) 위치와 문장의 자연스러운 높낮이(Intonation) 분석.
        4. 언어학적 교정 가이드: 한국어 화자가 틀리기 쉬운 조음 위치(Place of Articulation)를 기반으로 혀와 입술 사용법을 구체적으로 조언.
        
        답변은 한국어로 전문적이면서도 이해하기 쉽게 작성해줘.
        """
        
        response = model.generate_content(prompt)
        
        st.divider()
        st.markdown("### 📊 전문 발음 분석 보고서")
        st.write(response.text)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.info("FFmpeg 경로가 올바른지 확인해 보세요.")
