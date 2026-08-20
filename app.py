import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

# 인쇄할 때 보기 좋게 만드는 마법의 디자인(CSS) 코드
hide_streamlit_style = """
<style>
@media print {
    header {visibility: hidden;} /* 상단 메뉴 숨김 */
    .stApp {margin-top: -50px;}
    .stButton {display: none;} /* 버튼 숨김 */
    .stTextInput {display: none;} /* 입력창 숨김 */
    footer {display: none;}
}
.article-text {
    font-size: 14pt;
    line-height: 1.8;
    font-family: 'Times New Roman', serif;
    text-align: justify;
    margin-bottom: 15px;
}
.article-title {
    font-size: 24pt;
    font-weight: bold;
    margin-bottom: 30px;
    border-bottom: 2px solid black;
    padding-bottom: 10px;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 화면에 보이는 제목과 설명
st.title("🗞️ BBC 뉴스 A4 인쇄 도우미")
st.write("안드로이드 태블릿에서 BBC 뉴스 링크를 넣고, 기사가 추출되면 브라우저 메뉴에서 **'인쇄'**를 눌러주세요.")

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

            # 본문 찾기 (문단 태그인 <p>를 모두 찾아서 너무 짧은 문구는 제외)
            paragraphs = soup.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 40: # 40글자 이상인 문단만 실제 기사로 취급
                    article_text += f"<p class='article-text'>{text}</p>"

            if not article_text:
                st.error("본문을 찾을 수 없습니다. 올바른 기사 링크인지 확인해주세요.")
            else:
                # 추출된 기사 화면에 그리기
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='article-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(article_text, unsafe_allow_html=True)
                
                st.success("✅ 성공! 우측 상단 브라우저 메뉴(점 3개) > '공유' > '인쇄'를 눌러 A4로 출력하세요.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
