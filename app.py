import os
import re
import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="AI 음원 자동화 대시보드",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 AI 음원 수익화 파이프라인 대시보드")
st.markdown("클로드(Claude)와 AI 툴을 연동하여 기획부터 최종 유통 패키징까지 탭을 이동하며 진행하는 대시보드입니다.")

# 세션 상태 초기화
if "generated_ideas" not in st.session_state:
    st.session_state.generated_ideas = None
if "selected_track" not in st.session_state:
    st.session_state.selected_track = None
if "final_package" not in st.session_state:
    st.session_state.final_package = None

# --- 사이드바 설정 ---
with st.sidebar:
    st.title("🛰️ AI Music Factory Dashboard")
    st.subheader("Welcome, 형님!") # 필요한 환영 문구
    
    st.markdown("---")
    st.subheader("🔑 API 및 외부 툴")
    
    # 기존 API 키 입력 란 (필요시 위치)
    api_key_input = st.text_input("Anthropic API Key", type="password")
    
    st.markdown("---")
    
    # Suno AI 바로가기 링크 버튼
    st.link_button("📂 Suno-AI for Music Creators", "https://www.suno.com", use_container_width=True)
    st.link_button("📂 Distrokid for Music Distributor", "https://distrokid.com/", use_container_width=True)
    st.link_button("📂 Ditto Music for Release unlimited music", "https://dittomusic.com/en", use_container_width=True)

# --- 상단 탭 구성 (Tab 4 추가) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Step 1: 기획 및 프롬프트", 
    "🎨 Step 2: 음원/커버 생성", 
    "📦 Step 3: 메타데이터 정리",
    "🚀 Step 4: 최종 패키지 및 다운로드"
])

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
                    반드시 아래 포맷에 맞춰서 3개를 작성해 주세요.

                    [아이디어 1]
                    - 곡 제목: (영문 제목 작성)
                    - 장르/분위기: (내용)
                    - Suno 프롬프트: (영어 프롬프트, 'Original, Distinct' 포함)
                    - 커버 프롬프트: (영어 프롬프트, 저작권 회피)

                    [아이디어 2]
                    - 곡 제목: (영문 제목 작성)
                    - 장르/분위기: (내용)
                    - Suno 프롬프트: (영어 프롬프트, 'Original, Distinct' 포함)
                    - 커버 프롬프트: (영어 프롬프트, 저작권 회피)

                    [아이디어 3]
                    - 곡 제목: (영문 제목 작성)
                    - 장르/분위기: (내용)
                    - Suno 프롬프트: (영어 프롬프트, 'Original, Distinct' 포함)
                    - 커버 프롬프트: (영어 프롬프트, 저작권 회피)
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
        st.text_area("기획안 내용", st.session_state.generated_ideas, height=250, disabled=True)

# --- TAB 2: 음원 및 커버 생성 요청 ---
with tab2:
    st.subheader("Step 2: 기획안 확인 및 AI 음원/커버 생성 요청")
    
    if not st.session_state.generated_ideas:
        st.warning("⚠️ 아직 Step 1에서 생성된 기획안이 없습니다. Step 1 탭에서 먼저 기획안을 생성해 주세요.")
    else:
        ideas_text = st.session_state.generated_ideas
        
        with st.expander("📄 클로드 전체 기획안 보기", expanded=False):
            st.text_area("전체 내용", ideas_text, height=200, disabled=True)
            
        st.markdown("---")
        st.markdown("#### 🎵 제작할 곡 선택 (클릭 시 자동 연동)")
        
        chosen_idea_tab = st.radio(
            "원하는 아이디어를 선택하세요",
            ["아이디어 1", "아이디어 2", "아이디어 3"],
            horizontal=True
        )
        
        default_title = f"AI Music - {chosen_idea_tab}"
        default_style = "Lo-Fi, Chill, Original, Distinct, 120bpm"
        default_cover = "A minimalist abstract square album cover, vibrant colors, no text"
        
        try:
            parts = ideas_text.split(f"[{chosen_idea_tab}]")
            if len(parts) > 1:
                target_block = parts[1].split("[아이디어")[0]
                title_match = re.search(r"곡 제목\s*[:\-]\s*(.*)", target_block)
                if title_match:
                    default_title = title_match.group(1).strip()
                suno_match = re.search(r"Suno 프롬프트\s*[:\-]\s*(.*)", target_block)
                if suno_match:
                    default_style = suno_match.group(1).strip()
                cover_match = re.search(r"커버 프롬프트\s*[:\-]\s*(.*)", target_block)
                if cover_match:
                    default_cover = cover_match.group(1).strip()
        except Exception:
            pass

        track_title_input = st.text_input("선택한 곡의 영문 제목 (Title)", value=default_title, key="title_input")
        style_prompt_input = st.text_area("Suno AI 입력용 스타일 프롬프트", value=default_style, key="style_input")
        cover_prompt_input = st.text_area("ChatGPT 앨범 커버 생성용 프롬프트", value=default_cover, key="cover_input")

        if st.button("🎨 AI 음원 및 커버 생성 요청하기", type="primary"):
            if not track_title_input or not style_prompt_input:
                st.warning("곡 제목과 스타일 프롬프트를 입력해 주세요.")
            else:
                st.session_state.selected_track = {
                    "option": chosen_idea_tab,
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
            # Step 4에서 사용할 최종 데이터 패키지 저장
            st.session_state.final_package = {
                "title": final_title,
                "artist": artist_name,
                "genre": genre,
                "style_prompt": track_info['style_prompt'],
                "cover_prompt": track_info['cover_prompt']
            }
            st.success("유통 패키지 정보가 확정되었습니다! 상단의 [Step 4] 탭으로 이동하여 최종 파일을 확인하세요.")

# --- TAB 4: 최종 패키지 및 다운로드 ---
with tab4:
    st.subheader("Step 4: 최종 유통 패키지 및 파일 다운로드")
    
    if not st.session_state.final_package:
        st.warning("⚠️ 아직 Step 3에서 패키지 정보가 확정되지 않았습니다. Step 3 탭에서 정보를 확정해 주세요.")
    else:
        pkg = st.session_state.final_package
        
        st.markdown("### 🎉 배급사 업로드 준비 완료!")
        st.success(f"**곡 제목:** {pkg['title']} | **아티스트:** {pkg['artist']} | **장르:** {pkg['genre']}")
        
        # 업로드용 텍스트 파일 내용 생성
        package_text = f"""=== AI 음원 유통 메타데이터 패키지 ===
- 곡 제목 (Title): {pkg['title']}
- 아티스트 명 (Artist): {pkg['artist']}
- 장르 (Genre): {pkg['genre']}

[Suno 생성 프롬프트]
{pkg['style_prompt']}

[ChatGPT 커버 이미지 생성 프롬프트]
{pkg['cover_prompt']}
=====================================
"""
        
        st.text_area("배급사 입력용 최종 요약", package_text, height=200)
        
        # 파일 다운로드 버튼 제공
        st.download_button(
            label="📥 업로드 정보(TXT) 다운로드하기",
            data=package_text,
            file_name=f"{pkg['title'].replace(' ', '_')}_metadata.txt",
            mime="text/plain",
            type="primary"
        )
        
        st.info("💡 **다음 단계 가이드:** DistroKid(또는 디토뮤직 등 배급사) 사이트에 접속하여, Suno에서 다운로드한 음원 파일(.mp3/.wav), ChatGPT로 만든 1:1 커버 이미지, 그리고 위에서 다운로드한 텍스트의 정보를 입력하시면 등록이 완료됩니다!")
