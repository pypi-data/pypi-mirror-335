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

def intelligence_profiler(user_content: str, role: str, model_provider: str = MODEL_PROVIDER, model_name: str = MODEL_NAME,
                          show_token_usage: Optional[bool] = True) -> dict:
    #### LIVE -- LIVE---LIVE -- LIVE
    system_message = f"""
    You are an expert AI assistant. First, analyze the user query and determine optimal intelligence parameters between (0.1-1.0):
        - Reasoning(r): Logical depth
        - Creativity(c): Imagination level
        - Precision(p): Specificity required

         Calculate Temperature(T) as follows:
            S = 1.2 * c + 0.8 * r - 1.5 * p
           (T) = (0.2 * (p >= 0.8 and c <= 0.2) +
                   0.9 * (c >= 0.8 and r <= 0.3) +
                   0.6 * (r >= 0.8 and 0.4 <= c <= 0.7) +
                   0.3 * (p >= 0.8 and r <= 0.3) +
                   0.7 * (r >= 0.8 and c >= 0.8 and p >= 0.8) +
                   1.0 * (not (p >= 0.8 and c <= 0.2) and
                          not (c >= 0.8 and r <= 0.3) and
                          not (r >= 0.8 and 0.4 <= c <= 0.7) and
                          not (p >= 0.8 and r <= 0.3) and
                          not (r >= 0.8 and c >= 0.8 and p >= 0.8))) * (1 - (1 / (1 + math.exp(-S))))

    Use the computed (T) to generate responses ensuring coherence with the intelligence profile.
    Then, generate a response based on these parameters.  

        Return ONLY the following JSON format:  
        {{
            "optimized_response": "<AI-generated response>",
            "intelligence_profile": {{ "reasoning": <value>, "creativity": <value>, "precision": <value>, "temperature": <value> # Internally used}}
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

    - Generate a coherent and informative response based on the user's request.
    - Ensure responses remain relevant to the given context.

    Return ONLY the following JSON format:  
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
    