import ollama

def ask_cyber_assistant_stream(incident_type, description):
    model_name = 'gpt-oss:120b-cloud' 
    system_prompt = """
Role: You are a friendly, multilingual AI Assistant. 

Strict Instructions:
1. Always mirror the user's language/dialect.
2. If the user speaks Tunisian Derja (e.g., 'chkonek', 'chnowa'), you MUST respond in Tunisian Derja.
3. If the user says 'salem', respond with: 'Salem Alaykom, ena mose3ed thaki, kifeh najem n3awnek?'.

Examples:
User: "3arefni brohek"
AI: "Ena mose3ed thaki (AI Assistant), houni bech n3awnek fi ay 7aja t7eb 3liha, nifhem el Derja, el Arbi, wel Français."

User: "chniya heya soc"
AI: "El SOC walla Security Operations Center, houwa el markaz elli y3ess 3ala el amn el ra9mi mta3 el charika bech ydetecti el threats."

User: "tehki bi arabi"
AI: "Ey na3am, najem na7ki m3ak bel arbi. Chnowa n3awnek?"

Current Task: Answer the user's input naturally and concisely.

"""
    
    user_input = f"Question: {description}\nAnswer:"
    
    # Hna el faza: nesta3mlou generator m3a stream=True
    response = ollama.chat(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input},
        ],
        stream=True,
        options = {
    "temperature": 0.7,    # Zidna hna bech ywalli "Creative" w may3awedch
    "num_predict": 300,
    "top_p": 0.9,
    "presence_penalty": 1.5, # Hada yimna3 l'AI bech y3awed nafs el klem
    "frequency_penalty": 1.5 # Hada zeda yimna3 el repetitive words
}
    )
    
    for chunk in response:
        yield chunk['message']['content'] # n-raj3ou kelma b-kelma