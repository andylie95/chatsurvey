import os
import pandas as pd
import streamlit as st

class SurveyApp:
    def __init__(self, questions_file):
        self.questions_file = questions_file
        self.questions = None
        self.language = None
    
    def load_survey_questions(self):
        lang_sheet = {
            'English': 'EN',
            'Indonesian': 'ID',
            'Malay': 'MY',
            'Hindi': 'HI'
        }[st.session_state.language]
        self.questions = pd.read_excel(self.questions_file, sheet_name=lang_sheet)
        self.questions.columns = [col.strip().lower() for col in self.questions.columns]  # Normalize column names
    
    def display_question(self):
        if st.session_state.current_question < len(self.questions):
            question_row = self.questions.iloc[st.session_state.current_question]
            prompt = question_row['prompt']
            question = question_row['question']
            
            # Handle empty prompt
            if pd.isna(prompt):
                prompt = ""
            
            question_text = f"{prompt} {question}"
            
            q_type = question_row['type']
            answer = None

            st.write(f"🤖: {question_text}")
            if q_type == 'alternative':
                answer = self.display_horizontal_radio([""] + [question_row['option1'], question_row['option2']], key=f"q{st.session_state.current_question}")
                if answer:
                    self.submit_answer(question_text, answer)
            elif q_type == 'fillblank':
                answer = st.text_input("Your answer:", key=f"q{st.session_state.current_question}")
                if answer and st.session_state.get(f"fillblank_{st.session_state.current_question}_submitted"):
                    self.submit_answer(question_text, answer)
            elif q_type == 'rating':
                options = [""] + [question_row['option1'], question_row['option2'], question_row['option3'], question_row['option4'], question_row['option5']]
                answer = self.display_horizontal_radio(options, key=f"q{st.session_state.current_question}")
                if answer:
                    self.submit_answer(question_text, answer)
    
    def display_horizontal_radio(self, options, key):
        selected_option = st.radio("", options, key=key)
        if selected_option:
            return selected_option
        return None
    
    def submit_answer(self, question, answer):
        st.session_state.answers.append({"question": question, "answer": answer})
        st.session_state.current_question += 1

    def save_conversation(self):
        df = pd.DataFrame(st.session_state.answers)
        csv_file = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Responses as CSV", data=csv_file, file_name='survey_responses.csv', mime='text/csv', key=f"download_csv_{st.session_state.current_question}")

if __name__ == "__main__":
    st.title("XPLORE Chat Survey")
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
        lang = st.selectbox("Select Language:", ["English", "Indonesian", "Malay", "Hindi"])
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
        instructions = "Welcome to XPLORE Chat Survey, please answer the questions below:"
        st.write(instructions)

        # Display previous questions and answers in a chat-like format
        for entry in st.session_state.answers:
            st.write(f"🤖: {entry['question']}")
            st.write(f"👦: {entry['answer']}")

        # Display the current question
        app.display_question()

        # Update the state outside the callback
        if st.session_state.get(f"fillblank_{st.session_state.current_question}_submitted"):
            st.session_state[f"fillblank_{st.session_state.current_question}_submitted"] = False
            st.experimental_rerun()

    # Auto scroll to the bottom
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

    if st.session_state.language_selected and st.session_state.current_question >= len(app.questions):
        app.save_conversation()
