import os
from typing import Optional
import openai
from groq import Groq
from dotenv import load_dotenv

if not os.path.exists(".env"):
    print("⚠️ Missing .env file! Please create one with API keys. Refer to the README.")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER")  #'openai' , 'groq' etc
MODEL_NAME = os.getenv("MODEL_NAME")  # gpt-3.5-turbo, gemma2-9b-it 

from scipy.interpolate import RegularGridInterpolator
import numpy as np

# Define key R, C, P values and corresponding Temperatures
R_vals = np.array([0.1, 0.5, 0.9])
C_vals = np.array([0.1, 0.5, 0.9])
P_vals = np.array([0.1, 0.5, 0.9])

# Temperature values for each (R, C, P) combination
T_values = np.array([
    [[0.3, 0.4, 0.5], [0.4, 0.5, 0.6], [0.9, 0.8, 0.7]],  # R=0.1
    [[0.3, 0.4, 0.5], [0.4, 0.5, 0.6], [0.6, 0.7, 0.8]],  # R=0.5
    [[0.2, 0.3, 0.4], [0.3, 0.4, 0.5], [0.6, 0.7, 0.9]]   # R=0.9
])

# Create interpolation function
interpolator = RegularGridInterpolator((R_vals, C_vals, P_vals), T_values)

# Function to get temperature for any (R, C, P)
def get_dynamic_temperature(R, C, P):
    """Interpolate temperature based on Reasoning, Creativity, and Precision"""
    T = interpolator([[R, C, P]])[0]  # Get interpolated temperature
    print(f"Interpolated Temperature for R={R}, C={C}, P={P}: {T:.2f}")
    return T




def intelligence_profiler(user_content: str, role: str, model_provider: str = MODEL_PROVIDER, model_name: str = MODEL_NAME,
                          show_token_usage: Optional[bool] = True) -> dict:
    #### LIVE -- LIVE---LIVE -- LIVE
    # Step 1: Compute intelligence parameters
    R = compute_reasoning(user_content, role)
    C = compute_creativity(user_content, role)
    P = compute_precision(user_content, role)
    # Step 2: Get dynamically computed Temperature (T)
    T = get_dynamic_temperature(R, C, P)    

    system_message = f"""
        You are an expert AI assistant. First, analyze the user query and determine optimal intelligence parameters:
        - Reasoning (0.1-1.0): Logical depth
        - Creativity (0.1-1.0): Imagination level
        - Precision (0.1-1.0): Specificity required

        Based on these values, the system **dynamically derives the optimal temperature** ensuring response consistency.

        Your response must align with the intelligence profile and use the dynamically assigned temperature.

        Intelligence Profile:
            - Reasoning: {R:.2f}
            - Creativity: {C:.2f}
            - Precision: {P:.2f}
            - Temperature: {T:.2f}

        Return **ONLY** the following JSON format:  
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

import re

def compute_reasoning(user_content: str, role: str) -> float:
    """
    Compute reasoning score based on the complexity of the query.
    Higher if query has multiple conditions, logical operations, or deep questions.
    """
    complexity_keywords = ["why", "explain", "cause", "analyze", "evaluate", "relationship"]
    logic_patterns = [r"if.*then", r"either.*or", r"not only.*but also"]
    
    score = 0.3  # Default low reasoning
    
    # Check for complexity keywords
    if any(word in user_content.lower() for word in complexity_keywords):
        score += 0.3  

    # Check for logical patterns
    if any(re.search(pattern, user_content.lower()) for pattern in logic_patterns):
        score += 0.3  

    return round(min(score, 0.9), 2)  # Cap max value at 0.9


def compute_creativity(user_content: str, role: str) -> float:
    """
    Compute creativity score based on the type of question.
    Higher if query is open-ended, imaginative, or requires novel thinking.
    """
    creative_keywords = ["imagine", "what if", "invent", "creative", "generate", "design"]
    
    score = 0.3  # Default low creativity

    if any(word in user_content.lower() for word in creative_keywords):
        score += 0.4  # Boost creativity for open-ended or innovative queries
    
    if "story" in user_content.lower() or "poem" in user_content.lower():
        score += 0.2  # Further boost for storytelling

    return round(min(score, 0.9), 2)


def compute_precision(user_content: str, role: str) -> float:
    """
    Compute precision score based on whether the query requires specific, factual, or technical details.
    """
    precise_keywords = ["define", "list", "exact", "steps", "data", "formula", "specific"]
    
    score = 0.3  # Default low precision

    if any(word in user_content.lower() for word in precise_keywords):
        score += 0.4  # Increase precision for fact-based queries

    if "how much" in user_content.lower() or "percentage" in user_content.lower():
        score += 0.2  # Boost for numerical precision

    return round(min(score, 0.9), 2)

    