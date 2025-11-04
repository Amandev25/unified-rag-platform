import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def build_prompt(question: str, context_chunks: list[dict]) -> str:
    """
    Builds the prompt for the LLM based on the question and context chunks.
    Enhanced with better instructions and formatting.
    """
    
    # 1. Start with the enhanced system prompt template
    prompt_template = """You are a knowledgeable AI assistant specialized in answering questions based on provided context from a multimodal knowledge base containing text documents, images, and audio transcripts.

INSTRUCTIONS:
1. Answer the user's question using ONLY the information from the context provided below
2. ALWAYS cite your sources using [Citation N] notation at the end of each sentence where you use information
3. If the context contains information from multiple sources, synthesize them coherently
4. If the question cannot be answered from the context, clearly state: "I cannot find information about this in the provided context"
5. Be specific and precise - include relevant details like dates, numbers, names when available
6. For image sources, acknowledge their presence and describe what they likely contain based on their metadata
7. For audio transcript sources, mention the timestamp if relevant
8. Structure your answer clearly with proper paragraphs if the answer is long

CONTEXT INFORMATION:
---
[CONTEXT_BLOCK]
---

"""
    
    # 2. Build the [CONTEXT_BLOCK] with enhanced formatting
    context_block_parts = []
    for i, chunk in enumerate(context_chunks):
        citation = f"[Citation {i+1}]"
        source = chunk.get('source', 'Unknown Source')
        content = chunk.get('content', '')
        content_type = chunk.get('type', 'text')
        metadata = chunk.get('metadata', {})
        score = chunk.get('score', None)

        chunk_str = f"{citation}\n"
        chunk_str += f"Source: {source}\n"
        chunk_str += f"Type: {content_type.capitalize()}\n"
        
        # Add relevance score if available
        if score is not None:
            chunk_str += f"Relevance Score: {score:.4f}\n"
        
        # Add type-specific metadata
        if content_type == 'text':
            if 'page' in metadata:
                chunk_str += f"Page: {metadata['page']}\n"
            chunk_str += f"Content:\n{content}\n"
        
        elif content_type == 'audio':
            if 'start' in metadata and 'end' in metadata:
                chunk_str += f"Timestamp: {metadata['start']} - {metadata['end']}\n"
            chunk_str += f"Transcript:\n{content}\n"
        
        elif content_type == 'image':
            chunk_str += f"Description: A relevant image from the knowledge base\n"
            if 'size' in metadata:
                chunk_str += f"Image Size: {metadata['size']}\n"
            if content and content != 'N/A':
                chunk_str += f"Associated Text: {content}\n"
        
        else:
            chunk_str += f"Content:\n{content}\n"
            
        chunk_str += "---"
        context_block_parts.append(chunk_str)
    
    context_block_str = "\n".join(context_block_parts)

    # 3. Create the final prompt
    final_prompt = prompt_template.replace("[CONTEXT_BLOCK]", context_block_str)
    final_prompt += f"\nNow, please answer the following question using the context above:\n\n"
    final_prompt += f"QUESTION: {question}\n\n"
    final_prompt += f"ANSWER:"
    
    return final_prompt

def generate(prompt: str) -> str:
    """
    Calls the Ollama HTTP API with the specified prompt.

    Configuration via environment variables:
      - OLLAMA_URL (default: http://localhost:11434)
      - OLLAMA_MODEL (default: phi3:mini)
      - OLLAMA_TIMEOUT (seconds, default: 60)
      - NGROK_AUTH_TOKEN (optional, for ngrok tunnel support)
    """
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "phi3:mini")
    timeout = int(os.environ.get("OLLAMA_TIMEOUT", "60"))
    
    # Add headers for ngrok support (if using ngrok tunnel)
    headers = {}
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth:
        headers["ngrok-skip-browser-warning"] = "true"
        # Uncomment if using ngrok auth token
        # headers["Authorization"] = f"Bearer {ngrok_auth}"

    print(f"--- Sending Prompt to Ollama at {ollama_url} (model={model}) ---")
    
    # Only print prompt preview to avoid cluttering output (first 200 chars)
    if len(prompt) > 200:
        print(f"Prompt preview: {prompt[:200]}... (total length: {len(prompt)} chars)")
    else:
        print(f"Prompt: {prompt}")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        resp = requests.post(f"{ollama_url.rstrip('/')}/api/chat", json=payload, headers=headers, timeout=timeout)
        
        # Check status code before trying to parse JSON
        if resp.status_code != 200:
            print(f"\n--- Ollama HTTP Error ---")
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            
            if resp.status_code == 403:
                print("403 Forbidden - Authentication or access issue")
                print("If using ngrok, check tunnel authentication requirements")
                print("Or use local Ollama: set OLLAMA_URL=http://localhost:11434")
            elif resp.status_code == 500:
                print("500 Internal Server Error - Possible causes:")
                print("  1. Prompt might be too long for the model")
                print("  2. Model might not be loaded or available")
                print("  3. Server might be out of memory")
                print(f"  4. Try reducing the number of context chunks or prompt length")
                print(f"\nTry: ollama pull {model}")
                print(f"Or reduce DEFAULT_TOP_K in your .env file")
            
            return "Error: Could not get a response from the Ollama endpoint."
        
        data = resp.json()

        # Try common response shapes returned by Ollama
        # 1) { 'choices': [ { 'message': { 'role': 'assistant', 'content': '...' } } ] }
        if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            content = None
            if isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict):
                content = choice["message"].get("content")
            if not content:
                content = choice.get("content")
            if content:
                return content

        # 2) { 'message': { 'content': '...' } }
        if isinstance(data, dict) and "message" in data and isinstance(data["message"], dict):
            content = data["message"].get("content")
            if content:
                return content

        # 3) { 'text': '...' } or fallback to raw text
        if isinstance(data, dict) and "text" in data:
            return data["text"]

        # Fallback: return JSON string of the response
        return json.dumps(data)

    except requests.exceptions.RequestException as e:
        print("\n--- Ollama HTTP Error ---")
        print(f"Request error: {e}")
        if isinstance(e, requests.exceptions.ConnectionError):
            print("Could not connect to Ollama. Is the Ollama daemon running?")
            print("Try: ollama serve")
        elif isinstance(e, requests.exceptions.Timeout):
            print(f"Request timeout (>{timeout}s) - Prompt might be too long or model not loaded")
            print(f"Try: ollama pull {model}")
            print(f"Or reduce DEFAULT_TOP_K in your .env file")
        elif hasattr(e, 'response') and e.response is not None and e.response.status_code == 403:
            print("403 Forbidden - Authentication or access issue")
            print("If using ngrok, check tunnel authentication requirements")
            print("Or use local Ollama: set OLLAMA_URL=http://localhost:11434")
        return "Error: Could not get a response from the Ollama endpoint."
    except ValueError as e:
        # JSON decoding error
        print("\n--- Ollama Response Parse Error ---")
        print(f"Failed to parse JSON response: {e}")
        return "Error: Received an invalid response from Ollama."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred."

def get_grounded_answer(question: str, context_chunks: list[dict]) -> dict:
    """
    This is the main "deliverable" function for Person 3.
    """
    
    # 1. Build the prompt
    prompt = build_prompt(question, context_chunks)
    
    # 2. Generate the answer
    llm_text_output = generate(prompt)
    
    # 3. Return the final dictionary
    result = {
        "answer": llm_text_output,
        "sources": context_chunks
    }
    return result