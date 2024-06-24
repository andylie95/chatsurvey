import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from googletrans import Translator

st.title("XPLORE ChatSurvey for Participant Feedback")

# Add a header for the section with questions
st.header("Please provide your responses to the following questions")

# Load the credentials from environment variable
google_credentials = st.secrets["GOOGLE_CREDENTIALS"]

# Define the questions for each language
questions = {
    "en": ["What is your name?", "This training is relevant to my needs and/or interests.", "I have learnt new skills and/or knowledge through this training.", "I can describe and explain what I learnt at this training to others.", "I can apply what I have learnt to improve my work and/or my organisation.", "This training will enable me to make positive changes to my organisation, sector and/or society.", "Please list 3 new skills or knowledge you have learnt from this training", "Please describe how you can apply what you have learnt to improve your work or benefit others.", "How do you plan to share your learning with others?", "If you did not agree with any of the statements from Q5, please feel free to share why as we would like to understand the challenges involved.", "Are you a repeat participant?"]
}

# Define the answers for each language
answers = {
    "en": ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"],
}

# Function to display the chat message with options as buttons
def chat_message_with_buttons(content, options):
    st.chat_message("assistant").write(content)
    selected_option = None
    button_cols = st.columns(len(options))
    for idx, option in enumerate(options):
        if button_cols[idx].button(option):
            selected_option = option
    return selected_option

# Function to display the chat message with text input
def chat_message_with_text_input(content):
    st.write(content)
    user_input = st.text_input("Your input:")
    return user_input

# Define the language options
languages = {"English": "en"}  # Add more languages as needed

# Select language
selected_language = st.selectbox("Select Language", list(languages.keys()))
selected_lang_code = languages[selected_language]

# Translator is defined to Google translator
trans = Translator()

# Original response of the user
responses_original = []

# Initialize session state
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
    st.session_state.responses = []

# Display previous questions and responses
for i in range(st.session_state.current_question):
    st.chat_message("assistant").write(questions[selected_lang_code][i])
    st.chat_message("user").write(st.session_state.responses[i])

# Display current question and collect response
if st.session_state.current_question < len(questions[selected_lang_code]):
    question = questions[selected_lang_code][st.session_state.current_question]
    
    if "?" in question:
        response = chat_message_with_buttons(question, answers[selected_lang_code])
    else:
        response = chat_message_with_text_input(question)

    responses_original.append(response)
    if response:
        translated = trans.translate(response, dest='en').text
        st.session_state.responses.append(translated)
        st.session_state.current_question += 1
        st.experimental_rerun()  # Rerun to display the next question

# Optionally, display a thank you message after all questions are answered
if st.session_state.current_question == len(questions[selected_lang_code]):
    st.write("Thank you for your feedback!")
    if google_credentials:
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_info(google_credentials, scopes=scopes)
        gc = gspread.authorize(credentials)
        gauth = GoogleAuth()
        gauth.credentials = credentials
        drive = GoogleDrive(gauth)
    
        # Open a Google sheet
        gs = gc.open_by_url('https://docs.google.com/spreadsheets/d/178sSyO5YpLNOVz8XtZJTif6Vc07-K7Nncjp56TB3qb8/edit?usp=sharing')
    
        # Select a work sheet from its name
        worksheet1 = gs.worksheet('Sheet1')
        worksheet2 = gs.worksheet('Sheet2')

        # Find the next empty row
        next_empty_row = len(worksheet1.col_values(1)) + 1
        next_empty_row_org = len(worksheet2.col_values(1)) + 1
    
        # Append the responses to the next empty row
        worksheet1.insert_row(st.session_state.responses, next_empty_row)
        worksheet2.insert_row(responses_original, next_empty_row_org)
    
        st.success('Responses submitted successfully!')
    else:
        st.error("Google credentials not found in environment variables")
