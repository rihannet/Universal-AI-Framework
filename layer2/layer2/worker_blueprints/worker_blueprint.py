"""
WORKER BLUEPRINT - Edit this to create your worker
===================================================
Copy this file, edit the values, and run it.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from layer2.layer2.layer2_main import create_layer2


async def create_my_worker():
    """Edit the values below to create your worker"""
    
    layer2 = create_layer2()
    
    # ============================================
    # EDIT THESE VALUES
    # ============================================
    
    worker = layer2.create_worker(
        
        # 1. WORKER ID (unique name, no spaces)
        worker_id="my_worker_1",
        
        # 2. WORKER NAME (display name)
        name="My First Worker",
        
        # 3. WORKER TYPE (create your own type)
        #    Examples: "browser", "terminal", "email", "sms", "video", "audio"
        #    You can use ANY type name you want!
        worker_type="browser",
        
        # 4. CAPABILITIES (what it can do)
        capabilities=["web_scraping", "browser_automation"],
        
        # 5. API KEYS (if needed, otherwise leave empty {})
        api_keys={},
        # Example with API key:
        # api_keys={"api_key": "your_api_key_here"},
        
        # 6. ENDPOINTS (if needed, otherwise leave empty {})
        endpoints={},
        # Example with endpoint:
        # endpoints={"default": "https://api.example.com"},
        
        # 7. MODEL CONFIG (optional, can leave as is)
        model_config={
            "temperature": 0.3,    # 0.0 = precise, 1.0 = creative
            "max_tokens": 1024     # response length
        }
    )
    
    print(f"✅ Worker created: {worker['worker_id']}")
    print(f"   Saved to: layer2/layer2/workers/{worker['worker_id']}.json")


if __name__ == "__main__":
    asyncio.run(create_my_worker())
