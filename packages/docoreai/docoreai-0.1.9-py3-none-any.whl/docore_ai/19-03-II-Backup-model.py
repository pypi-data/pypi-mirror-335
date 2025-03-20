import json
import os
from typing import Optional
import openai
from groq import Groq
from dotenv import load_dotenv

if not os.path.exists(".env"):
    raise FileNotFoundError("⚠️ Missing .env file! Please create one with API keys. Refer to the README.")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")  #'openai' , 'groq' etc
MODEL_NAME = os.getenv("MODEL_NAME")  # gpt-3.5-turbo, gemma2-9b-it 

import numpy as np

# Create a 3D array (100x100x100) for temperature lookup
T_values = np.zeros((100, 100, 100))

# Fill the table based on the logic you provided
for r in range(100):
    for c in range(100):
        for p in range(100):
            R, C, P = r / 100, c / 100, p / 100  # Convert index back to range 0.1 - 0.9
            
            if P >= 0.8 and C <= 0.2:
                T_values[r, c, p] = np.random.uniform(0.1, 0.3)  # Low temp, factual
            elif C >= 0.8 and R <= 0.3:
                T_values[r, c, p] = np.random.uniform(0.9, 1.0)  # High creativity
            elif 0.4 <= C <= 0.7 and 0.4 <= P <= 0.7:
                T_values[r, c, p] = np.random.uniform(0.4, 0.7)  # Balanced
            elif R >= 0.8 and 0.4 <= C <= 0.7:
                T_values[r, c, p] = np.random.uniform(0.3, 0.5)  # Logical
            elif P >= 0.8 and R <= 0.3:
                T_values[r, c, p] = np.random.uniform(0.2, 0.3)  # Fact-driven
            elif R >= 0.8 and C >= 0.8 and P >= 0.8:
                T_values[r, c, p] = np.random.uniform(0.6, 0.9)  # Balanced
            else:
                T_values[r, c, p] = 0.5  # Default value


def get_temperature_from_table(R, C, P):
    """Fetch temperature from the 3D table based on AI-predicted values."""
    
    # Convert to index (0-99)
    R_idx = min(max(int(R * 100), 0), 99)
    C_idx = min(max(int(C * 100), 0), 99)
    P_idx = min(max(int(P * 100), 0), 99)
    
    # Fetch temperature from predefined table
    T = T_values[R_idx, C_idx, P_idx]
    
    print(f"✅ Extracted Temperature: {T:.2f} for R={R}, C={C}, P={P}")
    
    return T

def extract_temperature_from_response(ai_response):
    """Extract R, C, P from AI response and fetch temperature from table."""
    try:
        extracted_data = json.loads(ai_response)
        R = extracted_data["intelligence_profile"]["reasoning"]
        C = extracted_data["intelligence_profile"]["creativity"]
        P = extracted_data["intelligence_profile"]["precision"]

        # **Fetch temperature from table**
        T = get_temperature_from_table(R, C, P)
        print("Temeprature VALUE" , T)
        return T
    
    except json.JSONDecodeError:
        print("⚠️ Error: AI did not return valid JSON. Using default temperature.")
        return 0.5  # Default temperature


def intelligence_profiler(user_content: str, role: str, model_provider: str = MODEL_PROVIDER, model_name: str = MODEL_NAME,
                          show_token_usage: Optional[bool] = True) -> dict:
    #### LIVE -- LIVE---LIVE -- LIVE
    system_message = f"""
        You are an expert AI assistant. First, analyze the user query and determine optimal intelligence parameters:
        - Reasoning (0.1-1.0): Logical depth
        - Creativity (0.1-1.0): Imagination level
        - Precision (0.1-1.0): Specificity required

    Based on these values, the system derives the optimal temperature.

    Intelligence Profile:
        - Reasoning: {{R}}
        - Creativity: {{C}}
        - Precision: {{P}}
        - Temperature: {{T({{R*100:.0f}},{{C*100:.0f}},{{P*100:.0f}})}}  # AI fills R,C,P, we fetch T

    Return **ONLY** the following JSON format:  
    {{
        "optimized_response": "<AI-generated response>",
        "intelligence_profile": {{ 
            "reasoning": {{R}}, 
            "creativity": {{C}}, 
            "precision": {{P}}, 
            "temperature": {{T({{R*100:.0f}},{{C*100:.0f}},{{P*100:.0f}})}} 
        }}
    }}
"""    
    user_message = f"""
    User Request: "{user_content}"
    Role: "{role}"
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    # Choose model provider
    if model_provider == "openai":
        openai.api_key = OPENAI_API_KEY

        # Append new user query to message history -MEMORY WIP ToDO
        #messages.append({"role": "user", "content": user_input})

        response = openai.Client().chat.completions.create(
            model=model_name,
            messages=messages,
            #temperature=0.3 #DO NOT SET THE TEMPERATURE HERE!
        )
        content = response.choices[0].message.content
        usage = response.usage  # Extract token usage

        # Append AI response to message history -MEMORY WIP ToDO
        #messages.append({"role": "assistant", "content": content})

        if show_token_usage:
            return {"response": content, "usage": usage}  # Return both content and usage
        else:
            return {"response": content}

    elif model_provider == "groq":
        client = Groq(api_key=GROQ_API_KEY) 

        # Append new user query to message history -MEMORY WIP ToDO
        #messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            #temperature=0.2 #DO NOT SET THE TEMPERATURE HERE!
        )       
        content = response.choices[0].message.content  
        usage = response.usage  # Extract token usage

        # Append AI response to message history -MEMORY WIP ToDO
        #messages.append({"role": "assistant", "content": content})        

        if show_token_usage:
            return {"response": content, "usage": usage}  # Return both content and usage
        else:
            return {"response": content}
    
def normal_prompt(user_content: str, role: str, model_provider: str = MODEL_PROVIDER, model_name: str = MODEL_NAME, 
                  show_token_usage: Optional[bool] = True) -> dict:
    """  Sends a normal prompt to the selected LLM (OpenAI or Groq) without intelligence parameters.
    """
    system_message = f"""
    You are an AI assistant. Your goal is to respond to user queries as accurately as possible.

    - Generate a **coherent and informative** response based on the user's request.
    - Ensure responses remain relevant to the given context.

    Return **ONLY** the following JSON format:  
    {{
        "response": "<AI-generated response>"
    }}
    """


    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_content}
    ]

    # Choose model provider
    if model_provider == "openai":
        openai.api_key = OPENAI_API_KEY

        # Append new user query to message history -MEMORY WIP ToDO
        #messages.append({"role": "user", "content": user_input})

        response = openai.Client().chat.completions.create(
            model=model_name,
            messages=messages,
            #temperature=0.3 #DO NOT SET THE TEMPERATURE HERE!

        )
        content = response.choices[0].message.content
        usage = response.usage  # Extract token usage

        # Append AI response to message history -MEMORY WIP ToDO
        #messages.append({"role": "assistant", "content": content})

        if show_token_usage:
            return {"response": content, "usage": usage}  # Return both content and usage
        else:
            return {"response": content}

    elif model_provider == "groq":
        client = Groq(api_key=GROQ_API_KEY) 

        # Append new user query to message history -MEMORY WIP ToDO
        #messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            #temperature=0.2 #DO NOT SET THE TEMPERATURE HERE!
        )       
        content = response.choices[0].message.content  
        usage = response.usage  # Extract token usage

        # Append AI response to message history -MEMORY WIP ToDO
        #messages.append({"role": "assistant", "content": content})        

        if show_token_usage:
            return {"response": content, "usage": usage}  # Return both content and usage
        else:
            return {"response": content}
    