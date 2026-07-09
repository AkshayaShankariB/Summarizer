import streamlit as st
from summary import split_text, summarize_chunk, final_summary, filter_chunks
from PyPDF2 import PdfReader

st.set_page_config(page_title="Smart Summarizer")

st.title("Smart Summarizer")
st.caption("Convert lecture text or PDF into bullet-point notes")

option = st.radio("Choose Input Type:", ["Text", "PDF"])

# ✅ Query is OPTIONAL
query = st.text_input("Enter topic or question (optional):")

text_input = ""

if option == "Text":
    text_input = st.text_area("Paste your lecture text here:", height=250)

elif option == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        pdf_reader = PdfReader(uploaded_file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        text_input = text
        st.success("✅ PDF text extracted!")

if st.button("✨ Generate Notes"):

    if text_input.strip() == "":
        st.warning("Please provide input!")

    else:
        with st.spinner("Processing... ⏳"):

            chunks = split_text(text_input)

            # ✅ Works only if query exists
            chunks = filter_chunks(chunks, query)

            summaries = []
            progress = st.progress(0)

            for i, chunk in enumerate(chunks):
                summaries.append(summarize_chunk(chunk, query))
                progress.progress((i + 1) / len(chunks))

            result = final_summary(summaries, query)

        st.success("✅ Notes Generated!")
        st.markdown("### 📌 Lecture Notes:")
        st.markdown(result)
if st.button("🗑️ Clear"):
    st.session_state.clear()
    st.rerun()