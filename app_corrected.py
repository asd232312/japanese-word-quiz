
import streamlit as st
import pandas as pd
import random
import csv
import os

WORDS_FILE = "N3.csv"
FAV_FILE = "favorites.csv"

def load_words():
    return pd.read_csv(WORDS_FILE, quoting=csv.QUOTE_MINIMAL, encoding='utf-8')

def load_favorites():
    if os.path.exists(FAV_FILE):
        return pd.read_csv(FAV_FILE)
    return pd.DataFrame(columns=["히라가나", "뜻"])

def save_favorites(df):
    df.to_csv(FAV_FILE, index=False)

def main():
    st.title("🈶 일본어 단어장 & 퀴즈 앱")

    menu = ["단어 검색", "즐겨찾기", "퀴즈"]
    choice = st.sidebar.selectbox("메뉴 선택", menu)

    words = load_words()
    favorites = load_favorites()

    if choice == "단어 검색":
        query = st.text_input("단어 또는 뜻을 검색하세요")
        if query:
            results = words[words["히라가나"].str.contains(query) | words["뜻"].str.contains(query)]
            if not results.empty:
                st.write(f"🔍 {len(results)}개 검색됨")
                for _, row in results.iterrows():
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"- {row['히라가나']} : {row['뜻']}")
                    if col2.button("⭐ 추가", key="add_" + row['히라가나']):
                        if not ((favorites['히라가나'] == row['히라가나']) & (favorites['뜻'] == row['뜻'])).any():
                            favorites = pd.concat([favorites, pd.DataFrame([row])], ignore_index=True)
                            save_favorites(favorites)
                            st.success(f"{row['히라가나']} 추가됨")
                            st.experimental_rerun()

    elif choice == "즐겨찾기":
        st.subheader("📌 즐겨찾기 목록")
        if favorites.empty:
            st.info("즐겨찾기된 단어가 없습니다.")
        else:
            to_remove = st.multiselect("제거할 단어 선택", favorites['히라가나'] + " : " + favorites['뜻'])
            if st.button("선택한 단어 제거"):
                mask = ~(favorites['히라가나'] + " : " + favorites['뜻']).isin(to_remove)
                favorites = favorites[mask]
                save_favorites(favorites)
                st.success("제거 완료")
                st.experimental_rerun()
            for _, row in favorites.iterrows():
                st.write(f"- {row['히라가나']} : {row['뜻']}")

    elif choice == "퀴즈":
        st.subheader("🧠 일본어 퀴즈 (뜻 → 히라가나)")

        if "quiz_set" not in st.session_state:
            st.session_state.quiz_set = random.sample(words.to_dict(orient="records"), 10)
        quiz_set = st.session_state.quiz_set
        correct, incorrect = [], []

        with st.form("quiz_form"):
            answers = {}
            for i, q in enumerate(quiz_set):
                answers[i] = st.text_input(f"{i+1}. {q['뜻']}", key=f"q{i}")
            submitted = st.form_submit_button("제출")

        if submitted:
            for i, q in enumerate(quiz_set):
                user_answer = answers[i].strip()
                if user_answer == q['히라가나']:
                    correct.append(q)
                else:
                    incorrect.append((q, user_answer))

            st.success(f"✅ 정답: {len(correct)}개")
            st.error(f"❌ 오답: {len(incorrect)}개")

            if correct:
                st.markdown("### ✅ 맞힌 문제:")
                for q in correct:
                    st.write(f"- {q['뜻']} → {q['히라가나']}")

            if incorrect:
                st.markdown("### ❌ 틀린 문제:")
                for q, user_answer in incorrect:
                    st.write(f"- {q['뜻']} → ❌ {user_answer} (정답: {q['히라가나']})")

            del st.session_state.quiz_set  # 퀴즈 제출 후 새 문제 가능

if __name__ == "__main__":
    main()
