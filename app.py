import streamlit as st
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Function to load survey questions from CSV
def load_survey_questions(file_path):
    return pd.read_csv(file_path)

# Function to initialize the HuggingFace model
@st.cache_resource
def initialize_model(model_name='distilbert-base-uncased'):
    try:
        tokenizer = BertTokenizer.from_pretrained(model_name)
        model = BertForSequenceClassification.from_pretrained(model_name)
        st.success(f"Successfully loaded model {model_name}")
    except Exception as e:
        st.error(f"Failed to load model {model_name}: {e}")
        tokenizer, model = None, None
    return tokenizer, model

# Function to get the chatbot response
def get_chatbot_response(user_input, tokenizer, model):
    if not tokenizer or not model:
        return "Model not available."
    inputs = tokenizer(user_input, return_tensors='pt')
    outputs = model(**inputs)
    response = torch.argmax(outputs.logits, dim=1).item()
    return tokenizer.decode([response])

# Function to save the conversation to a CSV file
def save_conversation_to_csv(conversation, file_path):
    df = pd.DataFrame(conversation, columns=['SIF Contact Centre', 'User'])
    df.to_csv(file_path, index=False)

# Main Streamlit app
def main():
    st.title('SIF Contact Centre - Post-Survey Chatbot')

    # Load survey questions
    survey_questions = load_survey_questions('survey_questions.csv')

    # Initialize the chatbot model
    tokenizer, model = initialize_model()

    # Initialize conversation history
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    # Initialize current question index
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0

    # Get the current question
    if st.session_state.question_index < len(survey_questions):
        current_question = survey_questions['Questions'][st.session_state.question_index]
    else:
        current_question = None

    # Display previous conversation
    for entry in st.session_state.conversation:
        st.markdown(f"<div style='text-align: left; padding: 5px; border-radius: 10px; background-color: white; margin: 10px 0;'>SIF Contact Centre: {entry['SIF Contact Centre']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: right; padding: 5px; border-radius: 10px; background-color: #DCF8C6; margin: 10px 0;'>You: {entry['User']}</div>", unsafe_allow_html=True)

    # Ask new question if there are remaining questions
    if current_question:
        if st.session_state.question_index == 0:
            bot_message = f"Hello, welcome to SIF Post-Survey, please tell me your ID."
        else:
            # Generate natural transition response
            user_input = st.session_state.conversation[-1]['User'] if st.session_state.conversation else ""
            transition_message = get_chatbot_response(user_input, tokenizer, model)
            bot_message = f"{transition_message} Now, {current_question}"

        st.markdown(f"<div style='text-align: left; padding: 5px; border-radius: 10px; background-color: white; margin: 10px 0;'>SIF Contact Centre: {bot_message}</div>", unsafe_allow_html=True)
        user_input = st.text_input("reply:", key=f'input_{st.session_state.question_index}')

        if user_input:
            # Add conversation to the history
            st.session_state.conversation.append({
                'SIF Contact Centre': bot_message,
                'User': user_input
            })

            # Increment question index
            st.session_state.question_index += 1

            # Clear the input field
            st.experimental_rerun()
    else:
        st.markdown("<div style='text-align: left; padding: 5px; border-radius: 10px; background-color: white; margin: 10px 0;'>SIF Contact Centre: Thank you for completing the survey!</div>", unsafe_allow_html=True)
        
        # Button to save and download the conversation
        if st.button('Save Conversation'):
            save_conversation_to_csv(st.session_state.conversation, 'conversation.csv')
            st.success('Conversation saved successfully!')

            # Provide a download link
            with open('conversation.csv', 'rb') as file:
                st.download_button(
                    label="Download conversation as CSV",
                    data=file,
                    file_name='conversation.csv',
                    mime='text/csv'
                )

if __name__ == '__main__':
    main()
