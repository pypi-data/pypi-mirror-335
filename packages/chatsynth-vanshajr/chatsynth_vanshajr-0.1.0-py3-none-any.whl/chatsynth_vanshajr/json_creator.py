import streamlit as st
import re
import json
import datetime

def is_valid_url(url):
    return bool(re.match(r"https?://[^\s]+", url))

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_phone(phone):
    return bool(re.match(r"^\+?\d{7,15}$", phone))

def is_valid_month_year(value):
    if value == "Present":
        return True
    return bool(re.match(r"^(0[1-9]|1[0-2])/\d{4}$", value))

def validate_dates(start, end):
    if end == "Present":
        return True
    try:
        start_month, start_year = map(int, start.split('/'))
        end_month, end_year = map(int, end.split('/'))
        return (end_year > start_year) or (end_year == start_year and end_month >= start_month)
    except:
        return False

def serialize_dates(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def add_entry(session_key, empty_entry):
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    st.session_state[session_key].append(empty_entry)
    st.rerun()

def remove_entry(session_key, index):
    del st.session_state[session_key][index]
    st.rerun()

def display_entries(session_key, fields, title):
    st.header(title)
    if session_key not in st.session_state:
        st.session_state[session_key] = []
    
    for i, entry in enumerate(st.session_state[session_key]):
        st.markdown(f"### {title} {i+1}")
        for field, label, field_type in fields:
            key = f"{session_key}_{field}_{i}"
            
            if field_type == "text":
                entry[field] = st.text_input(label, key=key, value=entry.get(field, ""))
            elif field_type == "number":
                entry[field] = st.number_input(label, min_value=1900, max_value=2100, step=1, key=key, value=entry.get(field, 2020))
            elif field_type == "month_year":
                current_value = entry.get(field, "")
                new_value = st.text_input(label, value=current_value,
                                        placeholder="MM/YYYY",
                                        help="Format: MM/YYYY (e.g. 03/2020)",
                                        key=key)
                entry[field] = new_value
            elif field_type == "textarea":
                entry[field] = st.text_area(label, key=key, value=entry.get(field, ""))
            
        if session_key == "work_entries":
            current_role = st.checkbox(f"Current Position", 
                                      value=entry.get("current", False),
                                      key=f"current_{i}")
            entry["current"] = current_role
            if current_role:
                entry["end_month_year"] = "Present"
            
        if st.button(f"Remove {title} {i+1}"):
            remove_entry(session_key, i)
    
    if st.button(f"Add {title}"):
        add_entry(session_key, {})

def json_creator():
    st.title("Step 1: 📃 Create Profile")
    
    st.header("Personal Information")
    name = st.text_input("Full Name *", value="").strip()
    email = st.text_input("Email Address", value="").strip().lower()
    phone = st.text_input("Phone Number", value="").strip()
    location = st.text_input("Location", value="").strip()
    bio = st.text_area("Short Bio", value="").strip()
    
    st.subheader("Skills")
    skills = st.text_input("Enter skills (comma separated)", 
                         help="Example: Python, Machine Learning, Project Management")
    
    display_entries("social_links", [
        ("platform", "Platform (e.g., LinkedIn)", "text"),
        ("url", "Profile URL", "text")
    ], "Social Links")
    
    display_entries("education_entries", [
        ("institution", "Institution", "text"),
        ("degree", "Degree", "text"),
        ("field_of_study", "Field of Study", "text"),
        ("start_year", "Start Year", "number"),
        ("end_year", "End Year", "number")
    ], "Education")
    
    display_entries("work_entries", [
        ("organization", "Organization", "text"),
        ("role", "Role", "text"),
        ("start_month_year", "Start Month/Year", "month_year"),
        ("end_month_year", "End Month/Year", "month_year"),
        ("description", "Description", "textarea")
    ], "Work Experience")
    
    display_entries("project_entries", [
        ("name", "Project Name", "text"),
        ("description", "Description", "textarea"),
        ("github", "GitHub Link", "text"),
        ("live_link", "Live Link", "text")
    ], "Projects")

    display_entries("achievement_entries", [
    ("title", "Achievement Title", "text"),
    ("date", "Date (MM/YYYY)", "month_year"),
    ("description", "Achievement Description", "textarea"),
    ("link", "Related Link (optional)", "text")
    ], "Achievements")
    
    if st.button("Generate JSON"):
        errors = []
        
        # Basic validations
        if not name:
            errors.append("Full Name is required!")
        if email and not is_valid_email(email):
            errors.append("Invalid email address!")
        if phone and not is_valid_phone(phone):
            errors.append("Invalid phone number!")
            
        # Validate social links
        invalid_links = [
            f"Social Link {i+1}: Invalid URL" 
            for i, link in enumerate(st.session_state.get("social_links", []))
            if not is_valid_url(link.get("url", ""))
        ]
        errors.extend(invalid_links)
        
        # Validate work experience dates
        for i, work in enumerate(st.session_state.get("work_entries", [])):
            if not is_valid_month_year(work.get("start_month_year", "")):
                errors.append(f"Work {i+1}: Invalid start date format")
            if not work.get("current", False) and not is_valid_month_year(work.get("end_month_year", "")):
                errors.append(f"Work {i+1}: Invalid end date format")
            if not validate_dates(work["start_month_year"], work.get("end_month_year", "Present")):
                errors.append(f"Work {i+1}: End date cannot be before start date")
        
        if errors:
            st.error("\n".join(errors))
            return
            
        try:
            # Process skills
            skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]
            
            user_data = {
                "personal_info": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "bio": bio,
                    "skills": skills_list
                },
                "social_links": st.session_state.get("social_links", []),
                "education": st.session_state.get("education_entries", []),
                "work_experience": st.session_state.get("work_entries", []),
                "projects": st.session_state.get("project_entries", []),
                "achievements": st.session_state.get("achievement_entries", []),
            }
            
            # Serialize dates properly
            json_str = json.dumps(user_data, indent=4, default=str)
            st.session_state.generated_json = json.loads(json_str)
            
            # Preview and download section
            st.subheader("JSON Preview")
            st.json(st.session_state.generated_json)
            
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="user_profile.json",
                mime="application/json"
            )
            
            st.success("JSON generated successfully! Please proceed to step 2!")
        except Exception as e:
            st.error(f"Error generating JSON: {e}")