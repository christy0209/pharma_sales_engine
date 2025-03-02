from utils.utils import LLM_GROQ
medicine_name = "Augmentin 625 Duo Tablet"
llm_response = LLM_GROQ(medicine_name)
print(llm_response)
