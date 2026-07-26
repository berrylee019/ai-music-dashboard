import os
import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="AI 음원 자동화 대시보드",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 AI 음원 수익화 파이프라인 대시보드")
st.markdown("클로드(Claude)와 AI 툴을 연동하여 기획부터 유통 패키징까지 탭을 이동하며 진행하는 대시보드입니다.")

# 세션 상태 초기화
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = None
if "selected_track" not in st.session_state:
    st.session_state.selected_track = None

# 사이드바: API 설정
st.sidebar.header("🔑 설정")
api_key_input = st.sidebar.text_input("Anthropic API Key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))

client = None
if api_key_input:
    try:
        client = anthropic.Anthropic(api_key=api_key_input)
    except Exception as e:
        st.sidebar.error("API Key 초기화 오류")
else:
    st.sidebar.warning("Claude API Key를 입력해주세요.")

# --- 상단 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["📌 Step 1: 기획 및 프롬프트", "🎨 Step 2: 음원/커버 생성 요청", "📦 Step 3: 유통 패키징"])

# --- TAB 1: 기획 및 프롬프트 생성 ---
with tab1:
    st.subheader("Step 1: 트렌드 키워드 및 Suno 프롬프트 기획")
    
    target_category = st.selectbox(
        "타겟 카테고리를 선택하세요",
        ["SNS 숏폼 (릴스/틱톡 배경음악)", "라이프스타일 / 카페 Lo-Fi", "운동/러닝용 비트", "시즌성 챌린지 (명절/휴가)"],
        key="cat_select"
    )

    custom_keyword = st.text_input("추가하고 싶은 세부 키워드나 느낌 (선택사항)", placeholder="예: 몽환적인 밤 감성, 신나는 댄스 비트 등", key="keyword_input")

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
                    
                    text_blocks = [block.text for block in message.content if block.type == "text"]
                    st.session_state.generated_ideas = "\n".join(text_blocks)
                    st.success("기획안이 성공적으로 생성되었습니다! 상단의 [Step 2] 탭으로 이동하세요.")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
                    
    if st.session_state.generated_ideas:
        st.markdown("---")
        st.markdown("#### 💡 현재 생성된 기획안 미리보기")
        st.text_area("기획안 내용", st.session_state.generated_ideas, height=200, disabled=True)

# --- TAB 2: 음원 및 커버 생성 요청 ---
with tab2:
    st.subheader("Step 2: 기획안 확인 및 AI 음원/커버 생성 요청")
    
    if not st.session_state.generated_ideas:
        st.warning("⚠️ 아직 Step 1에서 생성된 기획안이 없습니다. Step 1 탭에서 먼저 기획안을 생성해 주세요.")
    else:
        st.text_area("클로드의 기획안 결과 (3선)", st.session_state.generated_ideas, height=250)
        
        st.markdown("---")
        st.markdown("#### 🎵 제작할 곡 선택 및 세부 설정")
        
        selected_option = st.selectbox(
            "진행할 아이디어 번호를 선택하세요",
            ["아이디어 1번", "아이디어 2번", "아이디어 3번"],
            key="track_option"
        )
        
        track_title_input = st.text_input("선택한 곡의 영문 제목 (Title)", placeholder="예: Midnight Lo-Fi Rain", key="title_input")
        style_prompt_input = st.text_area("Suno AI 입력용 스타일 프롬프트", placeholder="Lo-Fi hip hop, calm, original, distinct...", key="style_input")
        cover_prompt_input = st.text_area("ChatGPT 앨범 커버 생성용 프롬프트", placeholder="A minimalist square album cover, abstract art, no text...", key="cover_input")

        if st.button("🎨 AI 음원 및 커버 생성 요청하기", type="primary"):
            if not track_title_input or not style_prompt_input:
                st.warning("곡 제목과 스타일 프롬프트를 입력해 주세요.")
            else:
                st.session_state.selected_track = {
                    "option": selected_option,
                    "title": track_title_input,
                    "style_prompt": style_prompt_input,
                    "cover_prompt": cover_prompt_input
                }
                st.success(f"'{track_title_input}' 생성 요청 완료! 상단의 [Step 3] 탭으로 이동하세요.")

# --- TAB 3: 유통 메타데이터 정리 및 패키징 ---
with tab3:
    st.subheader("Step 3: 배급사(DistroKid 등) 업로드 메타데이터 정리")
    
    if not st.session_state.selected_track:
        st.warning("⚠️ 아직 Step 2에서 생성 요청된 트랙이 없습니다. Step 2 탭에서 곡을 선택하고 생성 요청을 완료해 주세요.")
    else:
        track_info = st.session_state.selected_track
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**선택한 아이디어:** {track_info['option']}")
            final_title = st.text_input("최종 곡 제목", value=track_info['title'], key="final_title_input")
            artist_name = st.text_input("아티스트 명 (Artist)", key="artist_input")
            genre = st.selectbox("장르", ["Lo-Fi", "Hip-Hop", "Electronic", "Pop", "Ambient", "Jazz"], key="genre_select")
        
        with col2:
            st.info(f"""
            💡 **Suno / 커버 생성 프롬프트 참고**
            - **스타일:** `{track_info['style_prompt']}`
            - **커버 프롬프트:** `{track_info['cover_prompt']}`
            
            **체크리스트**
            - Suno에서 다운로드한 음원 파일(.mp3) 준비
            - ChatGPT로 생성한 1:1 정사각형 커버 이미지 저장 완료
            """)
        
        if st.button("📦 유통 패키지 정보 최종 확정", type="primary"):
            st.success(f"'{final_title}' (아티스트: {artist_name}) 배급사 업로드 패키지가 완성되었습니다! DistroKid 등에 업로드하세요.")
            st.balloons()
