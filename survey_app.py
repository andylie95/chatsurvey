import os
import pandas as pd
import streamlit as st

class SurveyApp:
    def __init__(self, questions_file):
        self.questions_file = questions_file
        self.questions = None
        self.current_question = 0
        self.language = 'English'
        self.load_survey_questions()
    
    def load_survey_questions(self):
        lang_sheet = 'EN' if self.language == 'English' else 'ID'
        self.questions = pd.read_excel(self.questions_file, sheet_name=lang_sheet)
        self.current_question = 0
    
    def display_question(self):
        if self.current_question < len(self.questions):
            question_row = self.questions.iloc[self.current_question]
            prompt = f"🤖: {question_row['Alright']} {question_row['prompt']} {question_row['question']}"
            st.write(prompt)
            
            q_type = question_row['type']
            if q_type == 'alternative':
                answer = st.radio("Your answer:", [question_row['option1'], question_row['option2']])
            elif q_type == 'fill_blank':
                answer = st.text_input("Your answer:")
            elif q_type == 'rating':
                answer = st.radio("Your rating:", ['1', '2', '3', '4', '5'])
            
            if st.button("Submit"):
                self.submit_answer(answer)
        else:
            st.write("Survey Completed! Thank you for your responses.")
    
    def submit_answer(self, answer):
        if self.current_question < len(self.questions):
            question_row = self.questions.iloc[self.current_question]
            st.write(f"👤: {answer}")
            # Store the answer if needed
            self.current_question += 1
            self.display_question()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    questions_file = os.path.join(script_dir, "survey_questions.xlsx")
    
    st.title("Survey Application")
    app = SurveyApp(questions_file)
    
    lang = st.selectbox("Select Language:", ["English", "Indonesian"])
    if lang != app.language:
        app.language = lang
        app.load_survey_questions()
    
    app.display_question()
