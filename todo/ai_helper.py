import ollama

def ask_cyber_assistant(incident_type, description):
    # Prompt 9sir w dhabet bch el model sghir may-dokh-ch
    system_prompt = "Tu es un expert SOC. Réponds brièvement en Français ou en Arabe Tunisien (Darija). Sois précis."
    
    user_input = f"Incident: {incident_type}. Détails: {description}. Donnez 3 étapes de remédiation."

    try:
        response = ollama.chat(model='llama3.2:1b', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input},
        ], options={
            "temperature": 0.4, # Khallih jiddi mouch creative
            "num_predict": 150   # Ma-tkhallihch yekteb barch bch may-rzinch
        })
        return response['message']['content']
    except Exception as e:
        return f"Erreur : {str(e)}"