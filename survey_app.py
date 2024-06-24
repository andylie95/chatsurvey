import os
import pandas as pd
import streamlit as st

class SurveyApp:
    def __init__(self, questions_file):
        self.questions_file = questions_file
        self.questions = None
        self.language = st.selectbox("Select Language:", ["English", "Indonesian"])
        self.load_survey_questions()
    
    def load_survey_questions(self):
        lang_sheet = 'EN' if self.language == 'English' else 'ID'
        self.questions = pd.read_excel(self.questions_file, sheet_name=lang_sheet)
        self.questions.columns = [col.strip().lower() for col in self.questions.columns]  # Normalize column names
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
        if 'answers' not in st.session_state:
            st.session_state.answers = []

    def display_question(self):
        if st.session_state.current_question < len(self.questions):
            question_row = self.questions.iloc[st.session_state.current_question]
            prompt = f"🤖: {question_row['prompt']} {question_row['question']}"
            st.write(prompt)
            
            q_type = question_row['type']
            answer = None
            if q_type == 'alternative':
                answer = st.radio("Your answer:", [question_row['option1'], question_row['option2']], key=f"q{st.session_state.current_question}")
            elif q_type == 'fill_blank':
                answer = st.text_input("Your answer:", key=f"q{st.session_state.current_question}")
            elif q_type == 'rating':
                answer = st.radio("Your rating:", ['1', '2', '3', '4', '5'], key=f"q{st.session_state.current_question}")
            
            if st.button("Submit"):
                self.submit_answer(answer)
        else:
            st.write("Survey Completed! Thank you for your responses.")
    
    def submit_answer(self, answer):
        if answer:
            st.session_state.answers.append(answer)
            st.write(f"👤: {answer}")
            st.session_state.current_question += 1
            st.experimental_rerun()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    questions_file = os.path.join(script_dir, "survey_questions.xlsx")
    
    st.title("Survey Application")
    app = SurveyApp(questions_file)
    app.display_question()
