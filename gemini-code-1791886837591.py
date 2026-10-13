import streamlit as st
import openai

# 페이지 설정
st.set_page_config(
    page_title="문학 감상평 교사 피드백 시스템",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화 (결과 저장용)
if "feedback_result" not in st.session_state:
    st.session_state.feedback_result = None

# 앱 타이틀 및 설명
st.title("📚 문학 감상평 교사 관점 피드백 시스템")
st.markdown("학생의 문학 감상평을 입력하면, 교사의 관점에서 텍스트 근거성, 비판적 사고, 표현력 및 소크라테스식 발문을 포함한 입체적인 피드백을 생성합니다.")

# 사이드바: API 키 및 기본 설정
with st.sidebar:
    st.header("⚙️ 설정")
    api_key_input = st.text_input("OpenAI API Key", type="password", value="")
    if api_key_input:
        openai.api_key = api_key_input
    else:
        # 환경 변수나 기본 설정이 있다면 활용
        pass
    
    st.markdown("---")
    st.markdown("### 💡 활용 팁")
    st.markdown("""
    - **갈래별 맞춤 분석**: 소설, 시, 극 등 장르에 알맞은 요소를 고려해 피드백합니다.
    - **소크라테스식 발문**: 정답을 바로 알려주기보다 학생의 사고를 확장하는 질문을 던집니다.
    """)

# 메인 입력 레이아웃 (2단 분할)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 1. 수업 및 작품 정보 입력")
    genre = st.selectbox(
        "문학 갈래 선택",
        ["현대시", "고전시가", "현대소설", "고전소설", "극·수필"]
    )
    work_title = st.text_input("작품명 및 작가", placeholder="예: 정현종, 「떨어져도 튀는 공처럼」")
    learning_objective = st.text_input(
        "수업 학습 목표 (선택)", 
        placeholder="예: 화자가 마주한 시련과 그것을 극복하는 태도 이해하기"
    )

with col2:
    st.subheader("✍️ 2. 학생 감상평 입력")
    student_name = st.text_input("학생 이름 또는 ID (선택)", placeholder="예: 홍길동")
    student_review = st.text_area(
        "학생 감상평 내용", 
        height=180,
        placeholder="학생이 작성한 감상평을 여기에 붙여넣으세요..."
    )

st.markdown("---")

# 피드백 생성 버튼
if st.button("🔍 교사 피드백 리포트 생성하기", type="primary", use_container_width=True):
    if not openai.api_key:
        st.error("⚠️ 사이드바에 OpenAI API Key를 입력해주세요.")
    elif not work_title or not student_review:
        st.warning("⚠️ '작품명 및 작가'와 '학생 감상평 내용'은 필수 입력 항목입니다.")
    else:
        with st.spinner("AI 교사가 감상평을 다각도로 분석하고 피드백을 작성하는 중입니다... 잠시만 기다려주세요!"):
            try:
                # 프롬프트 엔지니어링 설계
                prompt = f"""
                당신은 유능하고 통찰력 있는 고등학교 국어 교사입니다. 학생이 제출한 문학 작품 감상평을 다음 4가지 관점에서 면밀하게 분석하고, 교육적이고 따뜻하면서도 날카로운 피드백 리포트를 작성해 주세요.

                [입력 정보]
                - 문학 갈래: {genre}
                - 작품명/작가: {work_title}
                - 학습 목표: {learning_objective if learning_objective else "작품의 내적 의미 파악 및 주체적 수용"}
                - 학생 감상평: {student_review}

                [출력 양식 (마크다운 형식으로 작성)]
                ### 1. 감상 지평 분석 (텍스트 근거성)
                - 작품의 원문 텍스트나 문학적 맥락에 근거하여 타당하게 감상했는지 평가해주세요.

                ### 2. 비판적·창의적 사고력 평가
                - 상투적인 감상에 머무르지 않고 자신만의 삶의 경험이나 사회적 맥락과 연결해 주체적으로 수용했는지 진단해주세요.

                ### 3. 표현 및 문장 구조 피드백
                - 글의 논리 전개 방식, 문단 구성, 어휘 선택의 적절성을 국어과 서·논술형 평가 관점에서 점검해주세요.

                ### 4. 교사의 티칭 멘트 & 소크라테스식 발문
                - 학생을 격려하는 따뜻한 총평과 함께, 학생이 더 깊이 있게 사고할 수 있도록 유도하는 추가 질문(발문) 1~2가지를 던져주세요.
                """

                client = openai.OpenAI(api_key=openai.api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",  # 혹은 gpt-4o-mini 등 상황에 맞는 모델
                    messages=[
                        {"role": "system", "content": "당신은 전문적이고 따뜻한 국어과 교사입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                st.session_state.feedback_result = response.choices[0].message.content

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# 결과 출력 영역
if st.session_state.feedback_result:
    st.markdown("---")
    st.subheader(f"📊 [{student_name if student_name else '학생'}] 감상평 교사 피드백 리포트")
    st.markdown(st.session_state.feedback_result)
    
    # 다운로드 버튼 기능
    st.download_button(
        label="📥 피드백 리포트 다운로드 (Markdown)",
        data=st.session_state.feedback_result,
        file_name=f"{work_title}_감상평_피드백.md",
        mime="text/markdown"
    )