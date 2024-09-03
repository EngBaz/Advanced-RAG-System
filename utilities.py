import pandas as pd
import time
import streamlit as st

from PyPDF2 import PdfReader
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker 
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.document_compressors import CohereRerank



# Function to configure the retrieval with chat history
def configure_rag_chain(loader, llm):
    
    # Semantic chunking
    semantic_chunker = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="percentile")
    docs = semantic_chunker.create_documents([loader])
    vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
    
    # Hybrid search 
    similarity_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    keyword_retriever = BM25Retriever.from_documents(docs)
    keyword_retriever.k = 5
    ensemble_retriever = EnsembleRetriever(retrievers=[similarity_retriever, keyword_retriever], 
     
                                           weights=[0.5, 0.5])
    #Cohere AI Reranking
    compressor = CohereRerank()
    compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=ensemble_retriever)
    
    contextualize_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            ]
        )
        
    history_aware_retriever = create_history_aware_retriever(
        llm, compression_retriever, contextualize_prompt
        )

    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Keep the answer concise and clear.\
    {context}"""
        
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            ]
        )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    store = {}
    
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
            return store[session_id]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        )

    return conversational_rag_chain


# Function to stream the response
def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)


# Function to the data and provide a response
def process_file_and_answer(uploaded_file, file_format, llm, session_id="session1"):
    try:
        # Process the file based on the selected format
        if file_format == "pdf":
            pdf_reader = PdfReader(uploaded_file)
            data = "".join(page.extract_text() for page in pdf_reader.pages)
        elif file_format == "csv":
            df = pd.read_csv(uploaded_file)
            data = df.to_string()
        elif file_format == "txt":
            data = uploaded_file.read().decode("utf-8")
        elif file_format == "py":
            data = uploaded_file.read().decode("utf-8")
        else:
            raise ValueError("Unsupported file format selected.")
        
        # Configure the RAG chain
        conversational_rag_chain = configure_rag_chain(data, llm)
        
        # Ask the user for a question and get the answer
        question = st.text_input("Ask any question about the uploaded file!")
        if st.button("Answer!"):
            with st.spinner("Processing..."):
                response = conversational_rag_chain.invoke(
                    {"input": question},
                    config={"configurable": {"session_id": session_id}},
                )["answer"]
                st.write_stream(stream_data(response))
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
