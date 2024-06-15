import streamlit as st
import pandas as pd
from transformers import pipeline

def load_survey_questions(file_path):
    df = pd.read_excel(file_path)
    return df

# Load survey questions
df_questions = load_survey_questions('survey_questions.xlsx')

# Initialize the Hugging Face pipeline for text generation
generator = pipeline('text-generation', model='gpt2')

# Function to generate gamified responses
def generate_gamified_response(question, response):
    prompt = f"Q: {question}\nA: {response}\nGamify this:"
    result = generator(prompt, max_length=50, num_return_sequences=1)
    gamified_response = result[0]['generated_text'].replace(prompt, '').strip()
    return gamified_response

# Initialize Streamlit app
st.title('Gamified Survey Chatbot')

# Display survey questions and collect responses
responses = []
for index, row in df_questions.iterrows():
    question = row['Question']
    response = st.text_input(question)
    if response:
        gamified_response = generate_gamified_response(question, response)
        st.write(gamified_response)
        responses.append(response)

# Button to submit responses
if st.button('Submit'):
    df_responses = pd.DataFrame([responses], columns=df_questions['Question'].tolist())

    # Allow download of CSV
    st.download_button(
        label="Download CSV",
        data=df_responses.to_csv(index=False).encode('utf-8'),
        file_name='survey_responses.csv',
        mime='text/csv',
    )
    st.success('Responses recorded successfully!')
