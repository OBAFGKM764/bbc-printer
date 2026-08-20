import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

st.title("🗞️ BBC 뉴스 A4 인쇄 도우미")

# 글자 크기 조절 바
font_size = st.slider("🔍 본문 글자 크기를 조절하세요 (기본 14pt)", min_value=10, max_value=24, value=14)

# 인쇄할 때 보기 좋게 만드는 디자인(CSS) 코드
# !important 를 추가해서 무조건 우리가 설정한 글자 크기가 우선 적용되도록 마법을 걸어줍니다.
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
.article-date {{
    font-size: 12pt !important;
    color: gray;
    margin-bottom: 30px;
    border-bottom: 2px solid black;
    padding-bottom: 10px;
}}
</style>
"""
st.markdown(dynamic_style, unsafe_allow_html=True)

# 💡 핵심 해결책: 프로그램이 기사를 까먹지 않도록 '기억 장치(메모리)' 만들기
if 'article_extracted' not in st.session_state:
    st.session_state.article_extracted = False
    st.session_state.title = ""
    st.session_state.date_text = ""
    st.session_state.article_text = ""

# 링크 입력 창
url = st.text_input("BBC 뉴스 링크를 붙여넣으세요:", placeholder="https://www.bbc.com/news/...")

if st.button("기사 추출하기"):
    if url:
        try:
            # BBC 사이트에 접속
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 제목 찾기
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "제목을 찾을 수 없습니다"

            # 날짜 찾기
            time_tag = soup.find('time')
            if time_tag:
                date_text = time_tag.get_text(strip=True)
            else:
                date_text = "날짜 정보를 찾을 수 없습니다"

            # 본문 찾기
            paragraphs = soup.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 40: 
                    article_text += f"<p class='article-text'>{text}</p>"

            if not article_text:
                st.error("본문을 찾을 수 없습니다. 올바른 기사 링크인지 확인해주세요.")
            else:
                # 💡 핵심: 화면에 그리기 전에 메모리에 먼저 저장하기!
                st.session_state.title = title
                st.session_state.date_text = date_text
                st.session_state.article_text = article_text
                st.session_state.article_extracted = True

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 메모리에 기사가 저장되어 있다면, 언제든(슬라이더를 움직여도) 화면에 다시 그려주기
if st.session_state.article_extracted:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='article-title'>{st.session_state.title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='article-date'>🕒 기사 날짜: {st.session_state.date_text}</div>", unsafe_allow_html=True)
    st.markdown(st.session_state.article_text, unsafe_allow_html=True)
    
    st.success("✅ 이제 글자 크기를 조절해 보세요! 실시간으로 변합니다. 마음에 드는 크기가 되면 브라우저 메뉴에서 '인쇄'를 누르세요.")
