import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

st.title("🗞️ BBC 뉴스 A4 인쇄 도우미")

# [수정됨] 글자 크기 조절 바: 최소값을 8pt로 낮췄습니다.
font_size = st.slider("🔍 본문 글자 크기를 조절하세요 (기본 14pt)", min_value=8, max_value=24, value=14)

# 인쇄할 때 보기 좋게 만드는 디자인(CSS) 코드
dynamic_style = f"""
<style>
@media print {{
    header {{visibility: hidden;}} 
    .stApp {{margin-top: -50px;}}
    .stButton {{display: none;}} 
    .stTextInput {{display: none;}} 
    .stSlider {{display: none;}} 
    footer {{display: none;}}
}}
.article-text {{
    font-size: {font_size}pt !important;  
    line-height: 1.8;
    font-family: 'Times New Roman', serif;
    text-align: justify;
    margin-bottom: 15px;
}}
.article-title {{
    font-size: 24pt !important;
    font-weight: bold;
    margin-bottom: 10px;
}}
.article-info {{
    font-size: 11pt !important;
    color: #555555;
    margin-bottom: 30px;
    border-bottom: 2px solid black;
    padding-bottom: 10px;
    line-height: 1.5;
}}
</style>
"""
st.markdown(dynamic_style, unsafe_allow_html=True)

# 프로그램이 기사와 통계(글자 수 등)를 까먹지 않도록 메모리 만들기
if 'article_extracted' not in st.session_state:
    st.session_state.article_extracted = False
    st.session_state.title = ""
    st.session_state.date_text = ""
    st.session_state.article_html = ""
    st.session_state.word_count = 0
    st.session_state.char_count = 0

# 링크 입력 창
url = st.text_input("BBC 뉴스 링크를 붙여넣으세요:", placeholder="https://www.bbc.com/news/...")

if st.button("기사 추출하기"):
    if url:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 제목 찾기
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "제목을 찾을 수 없습니다"

            # 날짜 찾기
            time_tag = soup.find('time')
            date_text = time_tag.get_text(strip=True) if time_tag else "날짜 정보를 찾을 수 없습니다"

            # 본문 찾기 및 단어/글자 수 계산 준비
            paragraphs = soup.find_all('p')
            article_html = ""
            raw_text = "" # 글자 수 계산을 위해 순수 텍스트만 모아둘 바구니

            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 40: 
                    article_html += f"<p class='article-text'>{text}</p>"
                    raw_text += text + " " # 순수 텍스트 이어붙이기

            if not article_html:
                st.error("본문을 찾을 수 없습니다. 올바른 기사 링크인지 확인해주세요.")
            else:
                # [새로운 기능] 단어 수 및 글자 수 계산하기
                word_count = len(raw_text.split()) # 띄어쓰기 기준으로 단어 개수 세기
                char_count = len(raw_text.replace(" ", "")) # 띄어쓰기를 제외한 순수 글자 수 세기

                # 메모리에 저장
                st.session_state.title = title
                st.session_state.date_text = date_text
                st.session_state.article_html = article_html
                st.session_state.word_count = word_count
                st.session_state.char_count = char_count
                st.session_state.article_extracted = True

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 메모리에 기사가 있다면 화면에 그려주기
if st.session_state.article_extracted:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='article-title'>{st.session_state.title}</div>", unsafe_allow_html=True)
    
    # 날짜와 단어 수, 글자 수를 보기 좋게 한 줄에(또는 두 줄에) 출력
    info_text = f"""
    <div class='article-info'>
        🕒 기사 날짜: {st.session_state.date_text} <br>
        📝 단어 수: <b>{st.session_state.word_count:,}</b>개 &nbsp;|&nbsp; 🔤 글자 수(공백 제외): <b>{st.session_state.char_count:,}</b>자
    </div>
    """
    st.markdown(info_text, unsafe_allow_html=True)
    
    # 본문 출력
    st.markdown(st.session_state.article_html, unsafe_allow_html=True)
    
    st.success("✅ 완료되었습니다! 글자 크기를 조절한 뒤 브라우저 메뉴에서 '인쇄'를 누르세요.")
