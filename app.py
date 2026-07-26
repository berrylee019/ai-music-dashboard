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
                    model="claude-sonnet-5",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # content 블록 중 type이 'text'인 것만 안전하게 추출
                text_blocks = [block.text for block in message.content if block.type == "text"]
                st.session_state.generated_ideas = "\n".join(text_blocks)
                st.session_state.step = 2
                st.success("기획안이 성공적으로 생성되었습니다!")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# --- STEP 2: 기획안 확인 및 생성 요청 ---
if st.session_state.step >= 2 and st.session_state.generated_ideas:
    st.markdown("---")
    st.subheader("Step 2: 기획안 확인 및 AI 음원/커버 생성 요청")
    st.markdown("클로드가 추천한 3가지 아이디어 중 마음에 드는 곡을 선택하고, 생성 요청을 진행하세요.")
    
    # 기획안 출력
    st.text_area("클로드의 기획안 결과 (3선)", st.session_state.generated_ideas, height=250)
    
    st.markdown("---")
    st.markdown("#### 🎵 제작할 곡 선택 및 세부 설정")
    
    # 사용자가 어떤 곡을 진행할지 선택/입력하는 필드
    selected_option = st.selectbox(
        "진행할 아이디어 번호를 선택하세요",
        ["아이디어 1번", "아이디어 2번", "아이디어 3번"]
    )
    
    track_title_input = st.text_input("선택한 곡의 영문 제목 (Title)", placeholder="예: Midnight Lo-Fi Rain")
    style_prompt_input = st.text_area("Suno AI 입력용 스타일 프롬프트 (복사해서 Suno에 넣으세요)", placeholder="Lo-Fi hip hop, calm, original, distinct...")
    cover_prompt_input = st.text_area("ChatGPT 앨범 커버 생성용 프롬프트 (복사해서 DALL-E에 넣으세요)", placeholder="A minimalist square album cover, abstract art, no text...")

    # AI 음원 및 커버 생성 요청 버튼
    if st.button("🎨 AI 음원 및 커버 생성 요청하기", type="primary"):
        if not track_title_input or not style_prompt_input:
            st.warning("곡 제목과 스타일 프롬프트를 입력해 주세요.")
        else:
            with st.spinner("AI 툴(Suno/ChatGPT) 연동 및 패키징 시뮬레이션 중..."):
                # 세션에 현재 선택된 트랙 정보 저장
                st.session_state.selected_track = {
                    "option": selected_option,
                    "title": track_title_input,
                    "style_prompt": style_prompt_input,
                    "cover_prompt": cover_prompt_input
                }
            st.success(f"'{track_title_input}' 음원 및 커버 생성 요청이 완료되었습니다! 아래에서 최종 패키지를 확인하세요.")
            st.session_state.step = 3
            st.rerun()

# --- STEP 3: 유통 메타데이터 정리 및 패키징 ---
if st.session_state.step >= 3 and st.session_state.selected_track:
    st.markdown("---")
    st.subheader("Step 3: 배급사(DistroKid 등) 업로드 메타데이터 정리")
    
    track_info = st.session_state.selected_track
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**선택한 아이디어:** {track_info['option']}")
        final_title = st.text_input("최종 곡 제목", value=track_info['title'])
        artist_name = st.text_input("아티스트 명 (Artist)")
        genre = st.selectbox("장르", ["Lo-Fi", "Hip-Hop", "Electronic", "Pop", "Ambient", "Jazz"])
    
    with col2:
        st.info(f"""
        💡 **Suno / 커버 생성에 사용된 프롬프트 참고**
        - **스타일:** `{track_info['style_prompt']}`
        - **커버 프롬프트:** `{track_info['cover_prompt']}`
        
        **체크리스트**
        - Suno에서 다운로드한 음원 파일(.mp3) 준비
        - ChatGPT로 생성한 1:1 정사각형 커버 이미지 저장 완료
        """)
    
    if st.button("📦 유통 패키지 정보 최종 확정"):
        st.success(f"'{final_title}' (아티스트: {artist_name}) 배급사 업로드 패키지가 완성되었습니다! 이제 DistroKid 등에 업로드하시면 됩니다.")
        st.balloons()
