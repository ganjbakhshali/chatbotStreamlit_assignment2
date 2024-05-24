import streamlit as st

if "value" not in st.session_state.get("flag", True):
    st.session_state.value = "Title"

st.header(st.session_state.value)

if st.button("Foo"):
    st.session_state.value = "Foo"
    st.rerun()