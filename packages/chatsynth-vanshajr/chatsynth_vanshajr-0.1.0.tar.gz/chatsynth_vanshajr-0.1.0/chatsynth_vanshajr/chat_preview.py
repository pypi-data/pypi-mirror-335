import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from chatsynth_vanshajr.retriever import ChatSynthRetriever

def chat_preview():
    if "faiss_created" not in st.session_state:
        st.warning("Please complete Steps 1 & 2 first!")
        return
    
    try:
        # Initialize session states
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
            
        if "api_keys" not in st.session_state:
            st.session_state.api_keys = {"groq": "", "hf": ""}
        
        user_data = st.session_state.generated_json
        user_name = user_data["personal_info"]["name"]
        
        st.title(f"Chat with {user_name}'s AI Assistant (Preview)")
        
        # Sidebar for API key input
        with st.sidebar:
            st.header("🔑 Temporary API Keys")
            groq_key = st.text_input("Groq API Key", 
                                    type="password",
                                    value=st.session_state.api_keys["groq"],
                                    key="preview_groq_key")
            hf_token = st.text_input("HuggingFace Token", 
                                   type="password",
                                   value=st.session_state.api_keys["hf"],
                                   key="preview_hf_token")
            
            st.session_state.api_keys.update({
                "groq": groq_key,
                "hf": hf_token
            })
            
            if not (groq_key and hf_token):
                st.warning("Enter both API keys to continue")
                return
                
            model_name = st.selectbox("Model", ["Llama3-70b-8192", "mixtral-8x7b-32768"])
        
        # Ensure FAISS index exists
        if not os.path.exists("faiss_index"):
            st.error("FAISS index not found! Complete Step 2 first.")
            return
        
        # Initialize components
        llm = ChatGroq(model_name=model_name, api_key=groq_key)
        retriever = ChatSynthRetriever().get_retriever()  # Use the retriever from the package

        # Create RAG chain
        prompt_template = ChatPromptTemplate.from_template("""
            You are an AI assistant created to answer questions about {name}. You are **not** {name}, but you use the provided context to give accurate responses.

            Context about {name}:
            {context}

            Conversation History:
            {history}

            **Rules:**
            1. Be respectful and professional.
            2. Answer only using the given context.
            3. If unsure, say "I don't have that information."
            4. Keep responses professional and concise.

            **User's Question:** {input}
        """)

        chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt_template))

        # Display chat messages
        for msg in st.session_state.chat_messages:
            st.chat_message(msg["role"]).write(msg["content"])
            
        # User input handling
        if prompt := st.chat_input("Ask me anything..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            try:
                with st.spinner("Thinking..."):
                    # Retrieve relevant documents from FAISS
                    retrieved_docs = retriever.get_relevant_documents(prompt)
                    
                    # Check if we actually got context
                    if not retrieved_docs:
                        st.warning("No relevant context found in FAISS! The chatbot may not provide a good answer.")

                    # Get conversation history
                    history = "\n".join(
                        [f"{msg['role']}: {msg['content']}" 
                         for msg in st.session_state.chat_messages[-5:]]
                    )
                    
                    response = chain.invoke({
                        "input": prompt,
                        "history": history,
                        "name": user_name,
                        "context": "\n\n".join([doc.page_content for doc in retrieved_docs])
                    })
                    
                    # Ensure correct key for the response
                    answer = response.get("answer", "I don't have that information.")
                    
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                    st.chat_message("assistant").write(answer)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
    except Exception as e:
        st.error(f"Preview error: {str(e)}")