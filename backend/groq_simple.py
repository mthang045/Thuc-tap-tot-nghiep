"""
Simple Groq API wrapper without langchain dependencies
Used as fallback for PageIndex when langchain has issues
"""

import os
import requests
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class LLMResponse:
    """Simple response container matching langchain interface"""
    content: str


class GroqSimpleLLM:
    """
    Simple Groq API wrapper without langchain
    Mimics langchain ChatGroq interface
    """
    
    def __init__(self, model="llama-3.1-8b-instant", temperature=0):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.model = model
        self.temperature = temperature
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def invoke(self, prompt: str) -> LLMResponse:
        """
        Call Groq API with prompt
        Returns LLMResponse with content field
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            return LLMResponse(content=content)
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Groq API error: {e}")
            # Return empty response as fallback
            return LLMResponse(content="")


if __name__ == '__main__':
    """Test simple Groq wrapper"""
    print("Testing simple Groq wrapper...")
    
    llm = GroqSimpleLLM()
    response = llm.invoke("Hello, what is 2+2?")
    
    print(f"Response: {response.content}")
