# Hybrid RAG with LangChain, FAISS and OpenAI GPT-4

This project presents an example of a Q&A assistant using LangChain, OpenAI GPT-4, FAISS vectorstore, and Streamlit.
The assistant can handle conversational context and assist in answering questions related to an uploaded document.

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [Usage](#usage)
- [Implementation](#Implementation)

## Introduction
The project showcases the implementation of a custom question-answering RAG system that leverages LangChain, an open-source framework, to interact with users in a conversational manner. The assistant answers questions related to a specific uploaded document and uses GPT-4 for natural language understanding and generation.

## Setup

To setup this project on your local machine, follow the below steps:
1. Clone this repository: <code>git clone github.com/EngBaz/conversational-retrieval-agent.git</code>
    
2. Install the required dependencies by running <code>pip install -r requirements.txt</code>

3. Create a virtual enviromnent
   ```console
    $ python -m venv .venv
    $ .venv\Scripts\activate.bat
    ```

4. Obtain an API key from OpenAI and Cohere AI. Store the Cohere API key in a <code>.env</code> file with the corresponsding name <code>COHERE_API_KEY</code>.
    
5. Note that the project is built using OpenAI GPT-4. Thus, it is necessary to have an OpenAI API key. Otherwise, for the use of open-source LLMs on huggingface, import your model using the steps below.
    ```console
    
    $ pip install langchain huggingface_hub
    $ os.environ['HUGGINGFACE_API_TOKEN'] = 'your_hugging_face_api_token'
    $ llm = HuggingFaceHub(repo_id="model_name", model_kwargs={'temperature': 0.7, 'max_length': 64})
    ```

## Usage

To use the conversational agent:
1. In the terminal, run the streamlit app: <code> streamlit run app.py </code>
2. Select the appropriate format of your file 
3. Upload your file
4. Write a specific question about the uploaded file
5. The agent will process the input and respond with relevant information

## Implementation

This section provides a brief summary of the techniques used to develop this project.

#### 1. Semantic Chunking

<code>Semantic chunking</code> is employed in building RAG systems to enhance retrieval accuracy. Unlike <code>text chunking</code>, which simply divides documents based on separators, semantic chunking considers the relationships within the text, segmenting it into meaningful and semantically identical chunks.

#### 2. Hybrid Search

A <code>hybrid search</code> system is developed with <code>FAISS</code> (Facebook AI similarity search) as a vector database. This method merges <code>keyword search</code> with the contextual insights of <code>semantic search</code> to deliver more accurate and relevant results. The Langchain <code>EnsembleRetriever</code> tool integrates these two search approaches.

#### 3. Cohere Rerank model

To further improve retrieval quality, a reranking model from Cohere AI is applied after the hybrid search to reorder the most relevant documents based on a relevance score.

#### 4. Chat Memory

In many Q&A applications, it's important to enable a back-and-forth conversation, which requires the system to have "memory" of previous interactions and incorporate that context into its responses. To handle follow-up questions, it's essential to include a sub-chain that reformulates the latest user query in the context of prior conversations. This ensures that questions referencing earlier messages, such as "Can you elaborate on the second point?", are fully understood before retrieval is performed, since such questions would be unclear without past context.

## References

[1] https://arxiv.org/pdf/2408.05141

[2] https://python.langchain.com/v0.2/docs/introduction/

[3] https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/

   
