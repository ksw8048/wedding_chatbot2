import streamlit as st
import google.generativeai as genai
import re

# 페이지 설정
st.set_page_config(
    page_title="💒 웨딩 예식 챗봇",
    page_icon="💒",
)

# 제목 표시
st.title("💒 웨딩 예식 챗봇")

# 하드코딩된 응답 정의
PREDEFINED_RESPONSES = {
    "parking": "예식장 지하 1층 전용 주차장을 이용하실 수 있습니다. 무료로 제공됩니다.",
    "location": "예식장은 서울 강남구 청담동에 위치한 청담웨딩홀 3층입니다.",
    "time": "예식은 2025년 10월 25일 토요일 오후 2시에 시작됩니다."
}

# 질문 패턴 정의
QUESTION_PATTERNS = {
    "parking": r"주차.*(어디|위치|가능|되나)",
    "location": r"(예식장|웨딩홀|장소).*(어디|위치|주소)",
    "time": r"(예식|결혼).*(시간|언제)"
}

def get_predefined_response(question):
    """사전 정의된 질문인지 확인하고 해당하는 응답을 반환"""
    question = question.strip()
    
    for key, pattern in QUESTION_PATTERNS.items():
        if re.search(pattern, question):
            return PREDEFINED_RESPONSES[key]
    
    return None

# Gemini API 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 채팅 기록을 저장할 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Gemini 채팅 세션 초기화
    st.session_state.chat = model.start_chat(history=[])

# 채팅 기록 표시
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 사용자 메시지를 채팅 기록에 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    try:
        # 사전 정의된 응답 확인
        predefined_response = get_predefined_response(prompt)
        
        if predefined_response:
            # 하드코딩된 응답 사용
            response_text = predefined_response
        else:
            # Gemini API로 응답 생성
            response = st.session_state.chat.send_message(prompt)
            response_text = response.text
            
            # 예식 정보 외 질문에 대한 기본 응답으로 변경
            if "죄송합니다" in response_text or "답변드리기 어렵" in response_text:
                response_text = "죄송합니다, 예식 정보 외의 답변은 드릴 수 없습니다."
        
        # 챗봇 응답 표시
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        # 챗봇 응답을 채팅 기록에 추가
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
