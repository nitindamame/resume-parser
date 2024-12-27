import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
import pandas as pd
import json
import re
import pypdf


api_key = os.getenv("GOOGLE_API_KEY")


llm_config = {"config_list": [{'model': 'gemini-1.5-flash', 'api_key': {api_key}, 'api_type': 'google'}]}


def extract_json(input_string):
    json_match = re.search(r'\{.*\}', input_string, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    else:
        print("No JSON data found")
        return None    

def get_gemini_response(pdf_content, input_text, response_schema):
    prompt = f"""
    You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    Assign the percentage matching based on the job description and list the missing keywords with high accuracy.

    ## Input:
    - Resume: {pdf_content}
    - Job Description: {input_text}

    ## Objective:
    - Understand and Identify important skills and requirements from Job description. 
    - Based on the job description generate list of important required_skills for the role.
    - Extract all the key skills, expiriences and other important details from CV
    - Match the extracted data from CV to the job description, the match might not be direct but relevant
    - Generate score based on the percentage of identified required skill from job description and the importance of the skill and the percentage of matching skills from the CV 
    - Generate the reason for the score generated

    ## Rules:
    - Evaluate the resume based on the job description.
    - Identify strengths and weekness in the CV from the job description's required skills and experience.
    - Identify missing keywords based on the job description's required skills and experience.
    - Missing keywords should be listed as a single string, separated by commas.
    - Make sure that the JSON output is correctly formatted and does not contain any extra spaces or newline characters that might cause parsing errors.

    ##Output:
    - Provide output in JSON format only as per the {response_schema} format with any additional comments or tags

    """
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content(prompt)
    return response.text

def input_pdf_text(uploaded_files):
    
    reader = pypdf.PdfReader(uploaded_files)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

st.set_page_config(page_title="ATS Resume EXpert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_files=st.file_uploader("Upload your resume(PDF)...",type=["pdf"],accept_multiple_files=True)


if uploaded_files is not None:
    st.write("PDF Uploaded Successfully")

response_schema ={
    "resume_score": "80%", 
    "required_skills": "",
    "strengths":"",
    "weaknesses":"",
    "missing_keywords": "",
    "reason_for_score": ""

}

if st.button("Percentage match"):
    data = []
    if uploaded_files is not None:
        print("Uploaded CVs")	
        for uploaded_file in uploaded_files:
            print("Processing the resume", uploaded_file)	
            pdf_content=input_pdf_text(uploaded_file)
            #response= resume_agent.analyse_resume(pdf_content, input_text, response_schema)
            response=get_gemini_response(pdf_content, input_text, response_schema)
            print("Response from agent", response)

            try:
                agent_response = extract_json(response)
                jd_match = agent_response.get("resume_score")
                missing_keywords = agent_response.get("missing_keywords")
                skills_to_match = agent_response.get("required_skills")
                strenghts = agent_response.get("strengths")
                weakness = agent_response.get("weaknesses")
                reason_for_score = agent_response.get("reason_for_score")
                #print(jd_match, missing_keywords, strenghts, weakness)
        
                data.append([uploaded_file.name, jd_match,strenghts,skills_to_match, weakness,missing_keywords,reason_for_score ] )
                print("extracted_data......")
                print(agent_response)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                agent_response = None

        st.subheader("The Repsonse is")
        df = pd.DataFrame(data, columns=["File Name", "Match %", "Strenghts","required_skills", "Weakness", "Missing Keywords","reason_for_score"])  
        st.write(df) 
    else:
        
        st.write("Please uplaod the resume")

# title = st.text_area("Job Title: ",key="input tile")
# location = st.text_area("location: ",key="input location")
# additional_keywords = st.text_area("keywords: ",key="input keywords")

# if st.button("Search Profiles"):
#     job_title = title
#     location = location
#     additional_keywords = additional_keywords

#     keywords = f"{job_title} {location} {additional_keywords}"
#     # Perform the search
#     results = api.search_people(
#     keywords=keywords,
#     include_private_profiles=True,
#     limit=10  # arbitrary limit to stop test taking too long
#     )

#     print(results)
#     people_list=[]
#     for person in results:
#         name = person.get('name')
#         location = person.get('location')
#         jobtitle = person.get('jobtitle')
#         urn_id = person.get('urn_id')
#         distance = person.get('distance')
#         linkedin_id = "https://www.linkedin.com/in/" + urn_id
    

#         people_list.append([name, location,jobtitle, linkedin_id])
        
#         # st.write(f"Name: {name}")
#         # st.write(f"Location: {location}")
#         # st.write(f"Job Title: {jobtitle}")
#         # st.write(f"URN ID: https://www.linkedin.com/in/{urn_id}")
#         # st.write(f"Distance: {distance}")
#         # st.write('-' * 20)
    
#     #st.write("Search Completed")
#     st.subheader("List of relevant people")
#     df = pd.DataFrame(people_list, columns=["Name", "Location","Job Title", "LinkedIn Profile"])  
#     st.write(df) 


