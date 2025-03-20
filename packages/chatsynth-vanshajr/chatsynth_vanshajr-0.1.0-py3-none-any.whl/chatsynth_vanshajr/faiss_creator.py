import os
import shutil
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def faiss_creator():
    st.title("Step 2: 📇 Create FAISS Index")
    
    if "generated_json" not in st.session_state:
        st.warning("Please complete Step 1 first!")
        return
    
    hf_token = st.text_input("Hugging Face Token", type="password")
    if not hf_token:
        st.warning("Please enter your Hugging Face token")
        return
    
    os.environ["HF_TOKEN"] = hf_token
    
    if st.button("Create FAISS Index"):
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            docs = []
            
            user_data = st.session_state.generated_json

            
            # Process education data
            for edu in user_data["education"]:
                docs.append(f"Education: {edu['institution']} - {edu['degree']} in {edu['field_of_study']} ({edu['start_year']}-{edu['end_year']})")
            
            # Process work experience
            for work in user_data["work_experience"]:
                duration = f"{work['start_month_year']} - {work.get('end_month_year', 'Present')}"
                docs.append(f"Work: {work['organization']} - {work['role']} ({duration}): {work['description']}")
            
            # Process projects
            for project in user_data["projects"]:
                docs.append(
                    f"Project: {project['name']}\n"
                    f"Description: {project['description']}\n"
                    f"GitHub: {project.get('github', '')}\n"
                    f"Live Demo: {project.get('live_link', '')}"
                )
            
            if user_data["personal_info"].get("skills"):
                docs.append("Skills: " + ", ".join(user_data["personal_info"]["skills"]))

            if user_data["personal_info"].get("email"):
                docs.append("Contact at email: " + "".join(user_data["personal_info"]["email"]))
            
            if user_data["personal_info"].get("phone"):
                docs.append("Contact at phone: " + "".join(user_data["personal_info"]["phone"]))
            
            if user_data["personal_info"].get("location"):
                docs.append("Location: " + "".join(user_data["personal_info"]["location"]))
            
            if user_data["personal_info"].get("bio"):
                docs.append("Summary: " + "".join(user_data["personal_info"]["bio"]))

            for link in user_data.get("social_links", []):
                docs.append(f"{link['platform']}: {link['url']}")

            for achievement in user_data.get("achievements", []):
                doc_lines = [
                    f"Achievement: {achievement['title']}",
                    f"Date: {achievement['date']}",
                    f"Description: {achievement['description']}"
                ]
                if achievement.get("link"):
                    doc_lines.append(f"Link: {achievement['link']}")
                docs.append("\n".join(doc_lines))

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            final_docs = text_splitter.create_documents(docs)
            
            if os.path.exists("faiss_index"):
                shutil.rmtree("faiss_index") 
            
            vector_store = FAISS.from_documents(final_docs, embeddings)
            vector_store.save_local("faiss_index")
            
            st.session_state.faiss_created = True
            st.success("FAISS index created successfully! Proceed to Step 3.")
        except Exception as e:
            st.error(f"Error creating FAISS index: {e}")