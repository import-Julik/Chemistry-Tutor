# app.py
import streamlit as st
from main import run_chemistry_tutor
st.set_page_config(
    page_title="🧪 AI-Тьютор по химии",
    page_icon="🧪",
    layout="centered"
)
st.title("🧪 AI-Тьютор по химии")
st.caption("Задай любой вопрос по химии — от балансировки уравнений до расчётов!")
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("Например: Сколько граммов воды из 25 г CH₄?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Решаю задачу..."):
            try:
                response = run_chemistry_tutor(prompt)
                if not response.strip():
                    response = "Извините, не удалось сформулировать ответ. Попробуйте переформулировать вопрос."
            except Exception as e:
                response = f"⚠️ Ошибка: {str(e)}"
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})