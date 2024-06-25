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
            if not any(entry["text"] == prompt for entry in st.session_state.chat_history):
                st.session_state.chat_history.append({"role": "bot", "text": prompt})
            
            q_type = question_row['type']
            if q_type == 'alternative':
                answer = st.radio("Your answer:", [question_row['option1'], question_row['option2']], key=f"q{st.session_state.current_question}")
                if st.button("Next", key=f"next{st.session_state.current_question}"):
                    self.submit_answer(answer)
            elif q_type == 'fillblank':
                answer = st.text_input("Your answer:", key=f"q{st.session_state.current_question}", on_change=self.submit_answer_fill_blank)
            elif q_type == 'rating':
                answer = st.radio("Your rating:", ['1', '2', '3', '4', '5'], key=f"q{st.session_state.current_question}")
                if st.button("Next", key=f"next{st.session_state.current_question}"):
                    self.submit_answer(answer)
        else:
            st.write("Survey Completed! Thank you for your responses.")
            self.save_conversation()

    def submit_answer_fill_blank(self):
        answer = st.session_state[f"q{st.session_state.current_question}"]
        st.session_state.answers.append(answer)
        st.session_state.chat_history.append({"role": "user", "text": answer})
        st.session_state.current_question += 1
        st.experimental_rerun()

    def submit_answer(self, answer):
        st.session_state.answers.append(answer)
        st.session_state.chat_history.append({"role": "user", "text": answer})
        st.session_state.current_question += 1
        st.experimental_rerun()

    def save_conversation(self):
        df = pd.DataFrame(st.session_state.chat_history)
        csv_file = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Conversation as CSV", data=csv_file, file_name='survey_conversation.csv', mime='text/csv')
        
        excel_file = df.to_excel(index=False)
        st.download_button("Download Conversation as XLSX", data=excel_file, file_name='survey_conversation.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

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
        if app.questions is None:
            app.load_survey_questions()
        app.display_question()
        
        for entry in st.session_state.chat_history:
            if entry["role"] == "bot":
                st.write(f"🤖: {entry['text']}")
            else:
                st.write(f"👤: {entry['text']}")

    if st.session_state.language_selected and st.session_state.current_question >= len(app.questions):
        app.save_conversation()
