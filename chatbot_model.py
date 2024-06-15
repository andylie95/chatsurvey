import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer

class ChatbotModel:
    def __init__(self, questions_file, model_name='microsoft/DialoGPT-medium'):
        self.questions = self.load_survey_questions(questions_file)
        self.tokenizer, self.model = self.initialize_model(model_name)

    def load_survey_questions(self, file_path):
        return pd.read_csv(file_path)

    def initialize_model(self, model_name):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        return tokenizer, model

    def get_chatbot_response(self, user_input):
        inputs = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')
        outputs = self.model.generate(inputs, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
        return response
