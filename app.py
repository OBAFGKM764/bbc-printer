import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

# 화면에 보이는 제목과 설명
st.title("🗞️ BBC 뉴스 A4 인쇄 도우미")
st.write("원하는 글자 크기를 맞춘 뒤 기사를 추출하고 인쇄하세요.")

# 1. 글자 크기 조절 기능 (슬라이더)
font_size = st.slider("글자 크기 조절 (기본 14)", min_value=10, max_value=24, value=14, step=1)

# 인쇄할 때 보기 좋게 만드는 디자인(CSS) 코드 (글자 크기 변수 적용)
hide_streamlit_style = f"""
<style>
@media print {{
    header {{visibility: hidden;}}
    .stApp {{margin-top: -50px;}}
    /* 인쇄 시 버튼, 입력창, 슬라이더 숨김 */
    .stButton {{display: none;}}
    .stTextInput {{display: none;}}
    div[data-testid="stSlider"] {{display: none;}}
    footer {{display: none;}}
}}
.article-text {{
    font-size: {font_size}pt;
    line-height: 1.8;
    font-family: 'Times New Roman', serif;
    text-align: justify;
    margin-bottom: 15px;
}}
.article-title {{
    font-size: {font_size + 10}pt;
    font-weight: bold;
    margin-bottom: 10px;
}}
.article-date {{
    font-size: {max(10, font_size - 4)}pt;
    color: gray;
    margin-bottom: 30px;
    border-bottom: 2px solid black;
    padding-bottom: 10px;
}}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 링크 입력 창
url = st.text_input("BBC 뉴스 링크를 붙여넣으세요:", placeholder="https://www.bbc.com/news/...")

if st.button("기사 추출하기"):
    if url:
        try:
            # BBC 사이트 접속
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 제목 찾기
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "제목을 찾을 수 없습니다"

            # 2. 날짜 찾기
            date_tag = soup.find('time')
            if date_tag and date_tag.has_attr('datetime'):
                # 기사에 작성일이 있으면 가져오기 (연-월-일)
                article_date = f"기사 작성일: {date_tag['datetime'][:10]}"
            else:
                # 못 찾으면 오늘 출력하는 날짜를 기록
                article_date = f"출력일: {datetime.now().strftime('%Y-%m-%d')}"

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
                # 추출된 기사 화면에 그리기
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='article-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='article-date'>{article_date}</div>", unsafe_allow_html=True)
                st.markdown(article_text, unsafe_allow_html=True)
                
                st.success("✅ 성공! 글자 크기가 마음에 든다면 브라우저 메뉴에서 '인쇄'를 눌러주세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
