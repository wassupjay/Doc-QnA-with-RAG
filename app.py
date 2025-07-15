import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Document Q&A with RAG", layout="centered")
st.title("📄 Document Q&A App")
st.markdown("Upload a text document (.txt) and ask questions about its content.")

if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

uploaded_file = st.file_uploader("Upload your document (TXT file)", type="txt")

if uploaded_file is not None:
    file_path = f"temp_doc_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    if st.button("Process Document"):
        with st.spinner("Processing document... This may take a moment."):
            loader = TextLoader(file_path)
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)

            embeddings = OpenAIEmbeddings()

            st.session_state.vectorstore = Chroma.from_documents(texts, embeddings)

            llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.3,api_key=openai_api_key)

            st.session_state.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=st.session_state.vectorstore.as_retriever()
            )
            st.success("Document processed and ready for questions!")

            if os.path.exists(file_path):
                os.remove(file_path)
else:
    st.session_state.vectorstore = None
    st.session_state.qa_chain = None
    st.info("Please upload a document to begin.")

st.markdown("---")
st.header("Ask a Question")
question = st.text_area("Enter your question here:", height=100, disabled=st.session_state.qa_chain is None)

if st.button("Get Answer", disabled=st.session_state.qa_chain is None):
    with st.spinner("Fetching answer..."):
        response = st.session_state.qa_chain.invoke({"query": question})
        st.success("Answer:")
        st.write(response["result"])

st.markdown("---")
st.caption("Powered by Jay, Langchain, Streamlit, and OpenAI API")
