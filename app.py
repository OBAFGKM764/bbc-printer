import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 기본 설정
st.set_page_config(page_title="BBC 기사 출력기", layout="centered")

# 글자 크기 조절 바
font_size = st.slider("🔍 본문 글자 크기를 조절하세요 (기본 14pt)", min_value=8, max_value=24, value=14)

# 인쇄할 때 보기 좋게 만드는 디자인(CSS) 코드
dynamic_style = f"""
<style>
/* 웹 화면에 보이는 앱 제목 디자인 */
.app-title {{
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 20px;
}}

@media print {{
    /* 💡 인쇄 시 불필요한 요소들 '완벽하게' 숨기기 */
    header {{display: none !important;}} 
    .app-title {{display: none !important;}} /* 'BBC 뉴스 인쇄 도우미' 앱 제목 숨김 */
    .stButton {{display: none !important;}} 
    .stTextInput {{display: none !important;}} 
    .stSlider {{display: none !important;}} 
    div[data-testid="stAlert"] {{display: none !important;}} /* 초록색 성공 안내 문구 숨김 */
    footer {{display: none !important;}}
    
    /* 💡 위쪽 쓸데없는 하얀 여백 싹 없애기 */
    .block-container {{
        padding-top: 0rem !important; 
        margin-top: 0rem !important;
    }}
}}

/* 기사 본문 디자인 */
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

# 기존 st.title 대신, 인쇄할 때 숨길 수 있는 이름표(class)를 달아서 화면에만 출력
st.markdown("<div class='app-title'>🗞️ BBC 뉴스 A4 인쇄 도우미</div>", unsafe_allow_html=True)

# 메모리 만들기
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

            # 본문 찾기 및 통계
            paragraphs = soup.find_all('p')
            article_html = ""
            raw_text = ""

            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 40: 
                    article_html += f"<p class='article-text'>{text}</p>"
                    raw_text += text + " "

            if not article_html:
                st.error("본문을 찾을 수 없습니다. 올바른 기사 링크인지 확인해주세요.")
            else:
                word_count = len(raw_text.split()) 
                char_count = len(raw_text.replace(" ", ""))

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
    # 기사 제목
    st.markdown(f"<div class='article-title'>{st.session_state.title}</div>", unsafe_allow_html=True)
    
    # 기사 날짜 및 단어수/글자수
    info_text = f"""
    <div class='article-info'>
        🕒 기사 날짜: {st.session_state.date_text} <br>
        📝 단어 수: <b>{st.session_state.word_count:,}</b>개 &nbsp;|&nbsp; 🔤 글자 수(공백 제외): <b>{st.session_state.char_count:,}</b>자
    </div>
    """
    st.markdown(info_text, unsafe_allow_html=True)
    
    # 본문 내용
    st.markdown(st.session_state.article_html, unsafe_allow_html=True)
    
    # 이 성공 메세지도 화면에만 보이고 인쇄할 땐 사라집니다!
    st.success("✅ 완료되었습니다! 글자 크기를 조절한 뒤 브라우저 메뉴에서 '인쇄'를 누르세요.")
