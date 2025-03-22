import os
import json
import requests
import base64
import tempfile
import streamlit as st
from datetime import datetime

def github_deploy():
    st.title("🚀 GitHub Deployment")
    
    try:
        # Validate previous steps
        required_keys = ["generated_json", "faiss_created"]
        if not all(key in st.session_state for key in required_keys):
            st.error("Complete Steps 1-3 first!")
            return
        
        # Get credentials
        gh_token = st.secrets.get("GITHUB_TOKEN")
        gh_user = st.secrets.get("GITHUB_USERNAME")
        if not gh_token or not gh_user:
            st.error("GitHub credentials missing in secrets!")
            return
        
        # Get user data
        user_data = st.session_state.generated_json["personal_info"]
        repo_base = st.text_input("Repository base name (e.g., MyChatBot)")
        user_name = user_data["name"].replace(" ", "_")
        
        if not repo_base:
            return
        
        # Generate repo name
        timestamp = datetime.now().strftime("%d%m%Y_%H%M")
        repo_name = f"{repo_base}_{user_name}_{timestamp}"
        
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check for existing repo
        def repo_exists():
            response = requests.get(
                f"https://api.github.com/repos/{gh_user}/{repo_name}",
                headers=headers
            )
            return response.status_code == 200
        
        if st.button("Deploy to GitHub"):
            if repo_exists():
                st.error(f"Repository {repo_name} already exists!")
                return
            
            # Create repository
            repo_creation = requests.post(
                "https://api.github.com/user/repos",
                json={"name": repo_name, "private": False},
                headers=headers
            )
            
            if repo_creation.status_code not in [200, 201]:
                st.error(f"Repo creation failed: {repo_creation.json().get('message')}")
                return
            
            # Create temp directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Prepare files
                files_to_upload = {
                    "user_profile.json": json.dumps(
                        st.session_state.generated_json,
                        indent=4,
                        default=str  # Handle dates as strings
                    ).encode(),
                    "rag_chatbot.py": open("deployed_files/rag_chatbot.py", "rb").read(),
                    "README.md": open("deployed_files/README.md", "rb").read(),
                    "requirements.txt": open("deployed_files/requirements.txt", "rb").read(),
                }
                
                # Add FAISS files
                faiss_files = {
                    "index.faiss": open("faiss_index/index.faiss", "rb").read(),
                    "index.pkl": open("faiss_index/index.pkl", "rb").read()
                }
                
                # Upload files
                commit_msg = f"Initial commit for {user_name} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                # Upload main files
                for path, content in files_to_upload.items():
                    response = requests.put(
                        f"https://api.github.com/repos/{gh_user}/{repo_name}/contents/{path}",
                        json={
                            "message": commit_msg,
                            "content": base64.b64encode(content).decode("utf-8")
                        },
                        headers=headers
                    )
                    if response.status_code not in [200, 201]:
                        error = response.json().get("message", "Unknown error")
                        st.error(f"Failed to upload {path}: {error}")
                        return
                
                # Upload FAISS files
                for fname, content in faiss_files.items():
                    response = requests.put(
                        f"https://api.github.com/repos/{gh_user}/{repo_name}/contents/faiss_index/{fname}",
                        json={
                            "message": commit_msg,
                            "content": base64.b64encode(content).decode("utf-8")
                        },
                        headers=headers
                    )
                    if response.status_code not in [200, 201]:
                        error = response.json().get("message", "Unknown error")
                        st.error(f"Failed to upload faiss_index/{fname}: {error}")
                        return
            
            # Show success
            repo_url = f"https://github.com/{gh_user}/{repo_name}"
            st.success("✅ Deployment Successful!")
            st.markdown(f"""
                **Your ChatBot Repository:**  
                [{repo_url}]({repo_url})
                
                Next Steps:  
                1. Fork repository  
                2. Deploy on [Streamlit Cloud](https://share.streamlit.io/)  
                3. Add secrets in app settings  
            """)
            
    except Exception as e:
        st.error(f"Deployment failed: {str(e)}")