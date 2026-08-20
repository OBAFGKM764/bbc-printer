import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

# 화면에 보이는 제목
st.title("🗞️ BBC 뉴스 A4 인쇄 도우미")

# [새로운 기능 1] 글자 크기 조절 바 만들기
font_size = st.slider("🔍 본문 글자 크기를 조절하세요 (기본 14pt)", min_value=10, max_value=24, value=14)

# 인쇄할 때 보기 좋게 만드는 디자인(CSS) 코드 (글자 크기 변수 적용)
dynamic_style = f"""
<style>
@media print {{
    header {{visibility: hidden;}} /* 상단 메뉴 숨김 */
    .stApp {{margin-top: -50px;}}
    .stButton {{display: none;}} /* 버튼 숨김 */
    .stTextInput {{display: none;}} /* 입력창 숨김 */
    .stSlider {{display: none;}} /* 인쇄할 땐 슬라이더도 숨김 */
    footer {{display: none;}}
}}
.article-text {{
    font-size: {font_size}pt;  /* 슬라이더에서 선택한 글자 크기가 여기에 적용됨 */
    line-height: 1.8;
    font-family: 'Times New Roman', serif;
    text-align: justify;
    margin-bottom: 15px;
}}
.article-title {{
    font-size: 24pt;
    font-weight: bold;
    margin-bottom: 10px;
}}
.article-date {{
    font-size: 12pt;
    color: gray;
    margin-bottom: 30px;
    border-bottom: 2px solid black;
    padding-bottom: 10px;
}}
</style>
"""
st.markdown(dynamic_style, unsafe_allow_html=True)

# 링크 입력 창
url = st.text_input("BBC 뉴스 링크를 붙여넣으세요:", placeholder="https://www.bbc.com/news/...")

if st.button("기사 추출하기"):
    if url:
        try:
            # BBC 사이트에 접속해서 데이터를 가져옴
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 제목 찾기
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "제목을 찾을 수 없습니다"

            # [새로운 기능 2] 기사 날짜 찾기
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
                # 추출된 기사 화면에 그리기
                st.markdown("<br>", unsafe_allow_html=True)
                # 제목 출력
                st.markdown(f"<div class='article-title'>{title}</div>", unsafe_allow_html=True)
                # 날짜 출력
                st.markdown(f"<div class='article-date'>🕒 기사 날짜: {date_text}</div>", unsafe_allow_html=True)
                # 본문 출력
                st.markdown(article_text, unsafe_allow_html=True)
                
                st.success("✅ 성공! 글자 크기를 확인한 후, 우측 상단 브라우저 메뉴(점 3개) > '공유' > '인쇄'를 눌러주세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
