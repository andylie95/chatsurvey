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
    df = pd.DataFrame(conversation, columns=['User', 'Chatbot'])
    df.to_csv(file_path, index=False)

# Main Streamlit app
def main():
    st.title('Survey Chatbot')

    # Load survey questions
    survey_questions = load_survey_questions('survey_questions.csv')

    # Initialize the chatbot model
    tokenizer, model = initialize_model()

    # Initialize conversation history
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Display survey questions and get responses
    for i, question in enumerate(survey_questions['Questions']):
        st.write(f"Q{i+1}: {question}")
        user_input = st.text_input(f'Your answer to Q{i+1}', key=f'q{i+1}')
        
        if user_input:
            # Get chatbot response
            response = get_chatbot_response(user_input, tokenizer, model)
            
            # Store the conversation
            st.session_state.conversation.append((user_input, response))
            
            # Display the response
            st.write(f"Chatbot: {response}")

    # Button to save and download the conversation
    if st.button('Save Conversation'):
        save_conversation_to_csv(st.session_state.conversation, 'conversation.csv')
        st.success('Conversation saved successfully!')

        # Provide a download link
        with open('conversation.csv', 'rb') as file:
            btn = st.download_button(
                label="Download conversation as CSV",
                data=file,
                file_name='conversation.csv',
                mime='text/csv'
            )

if __name__ == '__main__':
    main()
