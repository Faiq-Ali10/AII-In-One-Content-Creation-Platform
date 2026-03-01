from langchain_groq import ChatGroq

class LLM_Model():
    def __init__(self, temperature, model_name = "meta-llama/llama-4-scout-17b-16e-instruct") -> None:
        self.llm = ChatGroq(model=model_name, temperature=temperature)
        
    def get_model(self):
        return self.llm