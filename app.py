import streamlit as st
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer

# Function to load survey questions from CSV
def load_survey_questions(file_path):
    return pd.read_csv(file_path)

# Function to initialize the HuggingFace model
def initialize_model(model_name='microsoft/DialoGPT-medium'):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

# Function to get the chatbot response
def get_chatbot_response(user_input, tokenizer, model):
    inputs = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    outputs = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    return response

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
        st.write(f"SIF Contact Centre: {entry['SIF Contact Centre']}")
        st.write(f"You: {entry['User']}")

    # Ask new question if there are remaining questions
    if current_question:
        if st.session_state.question_index == 0:
            bot_message = f"Hello, welcome to SIF Post-Survey, please tell me your ID."
        else:
            bot_message = f"Alright, what about: {current_question}"
        
        st.write(f"SIF Contact Centre: {bot_message}")
        user_input = st.text_input("Your answer:", key=f'input_{st.session_state.question_index}')

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
        st.write("SIF Contact Centre: Thank you for completing the survey!")
        
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
