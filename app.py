import os
import streamlit as st
import anthropic

# 페이지 설정
st.set_page_title_config = st.set_page_config(
    page_title="AI 음원 자동화 대시보드",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 AI 음원 수익화 파이프라인 대시보드")
st.markdown("클로드(Claude)와 AI 툴을 연동하여 음원 기획부터 메타데이터 정리까지 단계별로 진행하는 대시보드입니다.")

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 1
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = None
if "selected_track" not in st.session_state:
    st.session_state.selected_track = None

# 사이드바: API 설정
st.sidebar.header("🔑 설정")
api_key_input = st.sidebar.text_input("Anthropic API Key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))

client = None
if api_key_input:
    client = anthropic.Anthropic(api_key=api_key_input)
else:
    st.sidebar.warning("Claude API Key를 입력해주세요.")

# --- STEP 1: 트렌드 기획 및 프롬프트 생성 ---
st.markdown("---")
st.subheader("Step 1: 트렌드 키워드 및 Suno 프롬프트 기획")

target_category = st.selectbox(
    "타겟 카테고리를 선택하세요",
    ["SNS 숏폼 (릴스/틱톡 배경음악)", "라이프스타일 / 카페 Lo-Fi", "운동/러닝용 비트", "시즌성 챌린지 (명절/휴가)"]
)

custom_keyword = st.text_input("추가하고 싶은 세부 키워드나 느낌 (선택사항)", placeholder="예: 몽환적인 밤 감성, 신나는 댄스 비트 등")

if st.button("🚀 클로드 팀장에게 기획안 요청하기", type="primary"):
    if not client:
        st.error("먼저 사이드바에 Anthropic API Key를 입력해주세요.")
    else:
        with st.spinner("클로드가 트렌드 분석 및 프롬프트를 생성 중입니다..."):
            try:
                prompt = f"""
                당신은 프로 AI 음원 프로듀서이자 마케터입니다. 
                사용자가 선택한 카테고리: '{target_category}'
                추가 키워드: '{custom_keyword}'
                
                이 조건에 맞는 전 세계 스토어/SNS 유통용 AI 음원 아이디어 3가지를 추천해 주세요.
                각 아이디어마다 다음 항목을 포함해 주세요:
                1. 곡 제목 (영문)
                2. 장르 및 분위기
                3. Suno AI 입력용 스타일 프롬프트 (영어, 'Original, Distinct' 키워드 포함)
                4. 가사 초안 또는 구조 (Verse, Chorus 등)
                5. 앨범 커버 이미지 생성용 프롬프트 (영어, 저작권/상표권 회피 주의)
                
                가독성 좋게 번호 매겨서 출력해 주세요.
                """
                
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.session_state.generated_ideas = message.content[0].text
                st.session_state.step = 2
                st.success("기획안이 성공적으로 생성되었습니다!")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# --- STEP 2: 기획안 확인 및 프롬프트 복사 ---
if st.session_state.step >= 2 and st.session_state.generated_ideas:
    st.markdown("---")
    st.subheader("Step 2: 생성된 기획 및 Suno/ChatGPT 프롬프트 확인")
    st.markdown("아래 프롬프트를 복사하여 **Suno AI**와 **ChatGPT(이미지 생성)**에 각각 입력하여 음원과 커버를 제작하세요.")
    
    st.text_area("클로드의 기획안 결과", st.session_state.generated_ideas, height=300)
    
    if st.button("음원 및 커버 생성을 완료했습니다 (다음 단계로 ➡️)"):
        st.session_state.step = 3
        st.rerun()

# --- STEP 3: 유통 메타데이터 정리 및 패키징 ---
if st.session_state.step >= 3:
    st.markdown("---")
    st.subheader("Step 3: 배급사(DistroKid 등) 업로드 메타데이터 정리")
    
    col1, col2 = st.columns(2)
    with col1:
        track_title = st.text_input("최종 곡 제목 (Title)")
        artist_name = st.text_input("아티스트 명 (Artist)")
        genre = st.selectbox("장르", ["Hip-Hop", "Lo-Fi", "Electronic", "Pop", "Ambient"])
    
    with col2:
        st.info("💡 **체크리스트**\n- Suno에서 다운로드한 음원 파일(.mp3/.wav)\n- 1:1 정사각형 앨범 커버 이미지 (유명 상표/로고 없음 확인)\n- 메타데이터 정보 입력 완료")
    
    if st.button("📦 유통 패키지 정보 저장 및 완료"):
        st.success(f"'{track_title}' (아티스트: {artist_name}) 배급사 업로드 준비 완료! 이제 DistroKid 등에 업로드하시면 됩니다.")
        st.balloons()
