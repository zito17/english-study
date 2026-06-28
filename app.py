
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
    st.info("💡 429 에러 발생 시 약 1분 후 다시 시도해 주세요.")

uploaded_file = st.file_uploader("음성 파일을 업로드하세요 (m4a, mp3, wav)", type=['wav', 'm4a', 'mp3'])

if uploaded_file and api_key:
    genai.configure(api_key=api_key)
    try:
        st.markdown("### 🎧 내 발음 다시 듣기")
        st.audio(uploaded_file)

        with open("temp_audio", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 오디오 변환
        sound = AudioSegment.from_file("temp_audio")
        sound.export("converted.wav", format="wav")

        # 음성 인식
        recognizer = sr.Recognizer()
        with sr.AudioFile("converted.wav") as source:
            audio_data = recognizer.record(source)
            recognized_text = recognizer.recognize_google(audio_data, language="en-US")

        st.success(f"🤖 인식된 문장: {recognized_text}")

        # Gemini 발음 분석 (안정적인 gemini-1.5-flash 모델 사용)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        너는 언어학 박사 학위를 가진 전문 영어 발음 코치야.
        다음 인식된 문장을 바탕으로 학생의 발음을 정밀 분석해줘.
        인식된 문장: '{recognized_text}'

        [분석 항목]
        1. 종합 발음 점수: 100점 만점 평가.
        2. 음성학적 정밀 진단: R/L, Th, F/V 등 조음 분석.
        3. 음절 강세 및 억양 분석.
        4. 언어학적 교정 가이드: 구체적인 조음 위치 조언.
        """

        response = model.generate_content(prompt)
        st.divider()
        st.markdown("### 📊 전문 발음 분석 보고서")
        st.write(response.text)

    except Exception as e:
        if '429' in str(e):
            st.error("🚨 API 할당량 초과입니다. 잠시 후 다시 시도해 주세요.")
        elif '404' in str(e):
            st.error("🚨 모델을 찾을 수 없습니다(404). 사용 중인 모델명이 'gemini-1.5-flash'인지 확인하세요.")
        else:
            st.error(f"오류 발생: {e}")
