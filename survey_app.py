import os
import pandas as pd
import streamlit as st

class SurveyApp:
    def __init__(self, questions_file):
        self.questions_file = questions_file
        self.questions = None
        self.language = None
    
    def load_survey_questions(self):
        lang_sheet = 'EN' if self.language == 'English' else 'ID'
        self.questions = pd.read_excel(self.questions_file, sheet_name=lang_sheet)
        self.questions.columns = [col.strip().lower() for col in self.questions.columns]  # Normalize column names
    
    def display_question(self):
        if st.session_state.current_question < len(self.questions):
            question_row = self.questions.iloc[st.session_state.current_question]
            prompt = f"🤖: {question_row['prompt']} {question_row['question']}"
            st.session_state.chat_history.append({"role": "bot", "text": prompt})
            
            q_type = question_row['type']
            answer = None
            if q_type == 'alternative':
                answer = st.radio("Your answer:", [question_row['option1'], question_row['option2']], key=f"q{st.session_state.current_question}")
            elif q_type == 'fill_blank':
                answer = st.text_input("Your answer:", key=f"q{st.session_state.current_question}")
            elif q_type == 'rating':
                answer = st.radio("Your rating:", ['1', '2', '3', '4', '5'], key=f"q{st.session_state.current_question}")
            
            if st.button("Submit"):
                if answer:
                    st.session_state.answers.append(answer)
                    st.session_state.chat_history.append({"role": "user", "text": answer})
                    st.session_state.current_question += 1
                    st.experimental_rerun()
        else:
            st.write("Survey Completed! Thank you for your responses.")
            self.save_conversation()

    def save_conversation(self):
        if st.button("Download Conversation as CSV"):
            df = pd.DataFrame(st.session_state.chat_history)
            df.to_csv("survey_conversation.csv", index=False)
            with open("survey_conversation.csv") as f:
                st.download_button('Download CSV', f, file_name='survey_conversation.csv')
        
        if st.button("Download Conversation as XLSX"):
            df = pd.DataFrame(st.session_state.chat_history)
            df.to_excel("survey_conversation.xlsx", index=False)
            with open("survey_conversation.xlsx", "rb") as f:
                st.download_button('Download XLSX', f, file_name='survey_conversation.xlsx')

if __name__ == "__main__":
    st.title("Survey Application")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    questions_file = os.path.join(script_dir, "survey_questions.xlsx")
    app = SurveyApp(questions_file)
    
    if 'language_selected' not in st.session_state:
        st.session_state.language_selected = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.language_selected:
        lang = st.selectbox("Select Language:", ["English", "Indonesian"])
        if st.button("Start Survey"):
            st.session_state.language_selected = True
            app.language = lang
            app.load_survey_questions()
            st.experimental_rerun()
    else:
        app.display_question()
        
    for entry in st.session_state.chat_history:
        if entry["role"] == "bot":
            st.write(f"🤖: {entry['text']}")
        else:
            st.write(f"👤: {entry['text']}")
