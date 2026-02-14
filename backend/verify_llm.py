import asyncio
import os
import litellm
from app.services.llm import llm_service
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Enable debug logging for valid request visibility
litellm.set_verbose=True

async def verify_models():
    print("Starting LLM Verification...")
    
    # Test the default fast model (should be gemini-2.5-flash-lite)
    print(f"\nTesting Default Fast Model ({llm_service.model_fast})...")
    try:
        response = await llm_service.complete(
            prompt="Hello, are you working?",
            tier="fast",
            max_tokens=50
        )
        print(f"✅ Fast Model Response: {response}")
    except Exception as e:
        print(f"❌ Fast Model Failed: {e}")

    # Test the fallback list from audit_agent
    print("\nTesting Audit Agent Model List...")
    models = [
        "gemini/gemini-2.5-flash-lite", 
        "gemini/gemini-2.5-flash", 
        "gemini/gemini-2.0-flash"
    ]
    
    for model in models:
        print(f"\nTesting {model}...")
        try:
            response = await llm_service.complete(
                prompt="Just say 'OK'",
                model=model,
                max_tokens=10
            )
            print(f"✅ {model} Response: {response}")
        except Exception as e:
            print(f"❌ {model} Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_models())
