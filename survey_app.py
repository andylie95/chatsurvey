import os
import pandas as pd
import streamlit as st

class SurveyApp:
    def __init__(self, questions_file):
        self.questions_file = questions_file
        self.questions = None
        self.language = None
    
    def load_survey_questions(self):
        lang_sheet = 'EN' if st.session_state.language == 'English' else 'ID'
        self.questions = pd.read_excel(self.questions_file, sheet_name=lang_sheet)
        self.questions.columns = [col.strip().lower() for col in self.questions.columns]  # Normalize column names
    
    def display_question(self):
        if st.session_state.current_question < len(self.questions):
            question_row = self.questions.iloc[st.session_state.current_question]
            prompt = f"🤖: {question_row['prompt']} {question_row['question']}"
            st.write(prompt)
            
            q_type = question_row['type']
            answer = None

            if q_type == 'alternative':
                answer = st.radio("Your answer:", [question_row['option1'], question_row['option2']], key=f"q{st.session_state.current_question}")
                if st.button("Next", key=f"next{st.session_state.current_question}"):
                    self.submit_answer(answer)
            elif q_type == 'fillblank':
                answer = st.text_input("Your answer:", key=f"q{st.session_state.current_question}")
                if answer:
                    self.submit_answer(answer)
            elif q_type == 'rating':
                answer = st.radio("Your rating:", ['1', '2', '3', '4', '5'], key=f"q{st.session_state.current_question}")
                if st.button("Next", key=f"next{st.session_state.current_question}"):
                    self.submit_answer(answer)
        else:
            st.write("Survey Completed! Thank you for your responses.")
            self.save_conversation()

    def submit_answer(self, answer):
        st.session_state.answers.append(answer)
        st.session_state.current_question += 1
        st.experimental_rerun()

    def save_conversation(self):
        df = pd.DataFrame(st.session_state.answers, columns=["answer"])
        csv_file = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Responses as CSV", data=csv_file, file_name='survey_responses.csv', mime='text/csv')
        
        with pd.ExcelWriter('survey_responses.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
            writer.save()
        
        with open("survey_responses.xlsx", "rb") as f:
            st.download_button("Download Responses as XLSX", data=f, file_name='survey_responses.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    st.title("Survey Application")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    questions_file = os.path.join(script_dir, "survey_questions.xlsx")
    app = SurveyApp(questions_file)
    
    if 'language_selected' not in st.session_state:
        st.session_state.language_selected = False
    if 'language' not in st.session_state:
        st.session_state.language = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []

    if not st.session_state.language_selected:
        lang = st.selectbox("Select Language:", ["English", "Indonesian"])
        if st.button("Start Survey"):
            st.session_state.language_selected = True
            st.session_state.language = lang
            app.language = lang
            app.load_survey_questions()
            st.experimental_rerun()
    else:
        if app.questions is None:
            app.load_survey_questions()
        
        # Show instructions
        instructions = "Please answer the questions below:" if app.language == "English" else "Silahkan jawab pertanyaan di bawah:"
        st.write(instructions)

        app.display_question()

    if st.session_state.language_selected and st.session_state.current_question >= len(app.questions):
        app.save_conversation()
