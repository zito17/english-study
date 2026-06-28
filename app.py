
import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from pydub import AudioSegment
import os

# 앱 설정
st.set_page_config(page_title="전문 영어 발음 교정 AI", page_icon="🎤")
st.title("🎤 전문 영어 발음 분석 및 교정")

# 사이드바 설정
with st.sidebar:
    st.title("설정")
    api_key = st.text_input("Google API Key", type="password")

uploaded_file = st.file_uploader("음성 파일을 업로드하세요 (m4a, mp3, wav)", type=['wav', 'm4a', 'mp3'])

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    try:
        st.markdown("### 🎧 내 발음 다시 듣기")
        st.audio(uploaded_file)

        with open("temp_audio", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 서버 환경에서는 시스템 ffmpeg를 사용하므로 별도 경로 지정이 필요 없음
        sound = AudioSegment.from_file("temp_audio")
        sound.export("converted.wav", format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile("converted.wav") as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language="en-US")

        st.success(f"🤖 인식된 문장: {recognized_text}")

        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        너는 언어학 박사 학위를 가진 전문 영어 발음 코치야.
        다음 인식된 문장을 바탕으로 학생의 발음을 정밀 분석해줘.
        인식된 문장: '{recognized_text}'

        [분석 항목]
        1. 종합 발음 점수: 100점 만점으로 평가.
        2. 음성학적 정밀 진단: R vs L, Th, F/V 등 주요 발음 정확성.
        3. 음절 강세 및 억양 분석.
        4. 언어학적 교정 가이드: 조음 위치(Place of Articulation) 기반 조언.
        """
        
        response = model.generate_content(prompt)
        st.divider()
        st.markdown("### 📊 전문 발음 분석 보고서")
        st.write(response.text)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
