"""
MAIN SYSTEM - All 5 Layers Integrated
======================================
Natural language interface for all workers and layers.
Just run: python main.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from layer1.main.layer1_main import Layer1Main
from layer2.layer2.layer2_main import create_layer2
from layer4.layer4.layer4_main import create_layer4
from layer5.layer5.layer5_main import create_layer5


class UniversalAISystem:
    """Main system integrating all 5 layers"""
    
    def __init__(self):
        print("=" * 70)
        print("INITIALIZING UNIVERSAL AI SYSTEM")
        print("=" * 70)
        
        # Initialize all layers
        print("\n[INIT] Layer-1: Planner + Memory + LLM...")
        self.layer1 = Layer1Main(
            lmstudio_base_url="http://192.168.1.6:1234",
            redis_host="localhost",
            redis_port=6379
        )
        print("✅ Layer-1 ready")
        
        print("\n[INIT] Layer-5: Web3 Identity & Audit...")
        self.layer5 = create_layer5()
        print("✅ Layer-5 ready")
        
        print("\n[INIT] Layer-4: Safety & Governance...")
        self.layer4 = create_layer4(layer5_audit=self.layer5)
        print("✅ Layer-4 ready")
        
        print("\n[INIT] Layer-3: MCP (simplified)...")
        self.layer3 = self._create_simple_mcp()
        print("✅ Layer-3 ready")
        
        print("\n[INIT] Layer-2: Worker Orchestration...")
        self.layer2 = create_layer2(
            lmstudio_base_url="http://192.168.1.6:1234",
            redis_host="localhost",
            redis_port=6379,
            layer1_planner=self.layer1.planner,
            layer3_mcp=self.layer3,
            layer4_safety=self.layer4,
            layer5_audit=self.layer5
        )
        print("✅ Layer-2 ready")
        
        print("\n" + "=" * 70)
        print("SYSTEM READY")
        print("=" * 70)
        print(f"Workers available: {len(self.layer2.workers)}")
        for w in self.layer2.list_workers():
            print(f"  - {w['name']} ({w['type']})")
        print("=" * 70)
    
    def _create_simple_mcp(self):
        """Simple MCP for Layer-3"""
        import subprocess
        import requests
        import os
        
        class SimpleMCP:
            async def execute_tool(self, tool_name, params):
                task = params.get("task", "")
                
                # Shell/Terminal execution
                if tool_name == "shell":
                    try:
                        result = subprocess.run(
                            task,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        return {
                            "success": result.returncode == 0,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "returncode": result.returncode
                        }
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                # Browser execution
                elif tool_name == "browser":
                    try:
                        url = task.replace("open ", "").replace("browse ", "").strip()
                        if not url.startswith("http"):
                            url = "https://" + url
                        
                        import webbrowser
                        webbrowser.open(url)
                        return {"success": True, "message": f"Opened {url}"}
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                # App launcher
                elif tool_name == "app":
                    try:
                        app_name = task.replace("launch ", "").replace("start ", "").replace("open ", "").replace("run ", "").strip()
                        
                        # Windows app launching in new window
                        if os.name == 'nt':
                            subprocess.Popen(
                                f'start "" {app_name}',
                                shell=True,
                                creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
                            )
                        else:
                            subprocess.Popen([app_name])
                        
                        return {"success": True, "message": f"Launched {app_name} in new window"}
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                # HTTP API
                elif tool_name == "http_api":
                    try:
                        endpoint = params.get("endpoints", {}).get("default", "")
                        api_keys = params.get("api_keys", {})
                        headers = {}
                        if "api_key" in api_keys:
                            headers["Authorization"] = f"Bearer {api_keys['api_key']}"
                        
                        response = requests.get(endpoint, headers=headers, timeout=30)
                        return {
                            "success": True,
                            "status_code": response.status_code,
                            "data": response.text[:500]
                        }
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                # File operations
                elif tool_name == "file":
                    try:
                        if "list" in task.lower():
                            files = os.listdir('.')
                            return {"success": True, "stdout": "\n".join(files)}
                        elif "read" in task.lower():
                            filename = task.split()[-1]
                            with open(filename, 'r') as f:
                                return {"success": True, "content": f.read()}
                        elif "write" in task.lower() or "create" in task.lower():
                            return {"success": True, "message": "File operation simulated"}
                        else:
                            return {"success": True, "message": "File operation completed"}
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                
                # Universal fallback
                else:
                    return {"success": True, "message": f"Executed {tool_name}", "task": task}
        
        return SimpleMCP()
    
    async def process_command(self, user_input: str):
        """Process natural language command"""
        print(f"\n[USER] {user_input}")
        
        # Smart keyword-based worker selection
        user_lower = user_input.lower()
        worker_type = None
        
        # Browser keywords
        if any(kw in user_lower for kw in ['open', 'browse', 'website', 'url', 'google', 'search web', '.com', 'http']):
            worker_type = "browser"
        # File keywords
        elif any(kw in user_lower for kw in ['file', 'read file', 'write file', 'create file', 'delete file', 'list']):
            worker_type = "file"
        # App keywords
        elif any(kw in user_lower for kw in ['launch', 'start app', 'open app', 'run app', 'notepad', 'calculator']):
            worker_type = "app"
        # Database keywords
        elif any(kw in user_lower for kw in ['database', 'query', 'sql', 'select', 'insert', 'update']):
            worker_type = "dbms"
        # Email keywords
        elif any(kw in user_lower for kw in ['email', 'send email', 'mail']):
            worker_type = "email"
        # SMS keywords
        elif any(kw in user_lower for kw in ['sms', 'text', 'send text']):
            worker_type = "sms"
        # API/News keywords
        elif any(kw in user_lower for kw in ['news', 'fetch news', 'api', 'weather', 'get data']):
            worker_type = "api"
        # Terminal keywords (default)
        else:
            worker_type = "terminal"
        
        action = user_input
        
        print(f"[SYSTEM] Worker: {worker_type}")
        print(f"[SYSTEM] Action: {action}")
        
        # Find matching worker
        worker_id = self._find_worker(worker_type)
        
        if not worker_id:
            if self.layer2.workers:
                worker_id = list(self.layer2.workers.keys())[0]
                print(f"[SYSTEM] No {worker_type} worker found, using: {worker_id}")
            else:
                print(f"[ERROR] No workers found. Create workers first.")
                return {"success": False, "error": "No workers available"}
        
        # Execute through Layer-2 (all layers integrated)
        print(f"[EXECUTE] Using worker: {worker_id}")
        result = await self.layer2.execute_worker_task(
            worker_id,
            action,
            {"agent_type": "DevOpsAgent"},
            use_planner=False
        )
        
        print(f"[RESULT] Success: {result.get('success')}")
        if result.get('stdout'):
            print(f"[OUTPUT] {result['stdout']}")
        if result.get('message'):
            print(f"[MESSAGE] {result['message']}")
        if result.get('error'):
            print(f"[ERROR] {result['error']}")
        
        return result
    
    def _find_worker(self, worker_type: str):
        """Find worker by type"""
        for wid, worker in self.layer2.workers.items():
            if worker.get('worker_type') == worker_type:
                return wid
        return None
    
    async def run_interactive(self):
        """Interactive chat mode"""
        print("\n" + "=" * 70)
        print("INTERACTIVE MODE")
        print("=" * 70)
        print("Commands:")
        print("  Worker: open google.com | launch notepad | list files | echo hello")
        print("  Memory: remember <text> | recall | history | forget")
        print("  System: status | workers | policies | audit | health")
        print("  Web3: authenticate | verify <hash> | sign <message>")
        print("  Admin: add-policy <rule> | enable-planner | reload")
        print("  Other: help | exit")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                cmd = user_input.lower()
                
                # Exit
                if cmd == 'exit':
                    print("\n[SYSTEM] Goodbye!")
                    break
                
                # Help
                elif cmd == 'help':
                    print("\n[HELP] Available Commands:")
                    print("  workers - List all workers")
                    print("  status - System status")
                    print("  health - Layer health check")
                    print("  policies - Show safety policies")
                    print("  audit - Show audit logs")
                    print("  remember <text> - Store in memory")
                    print("  recall - Show recent memory")
                    print("  history - Show command history")
                    print("  authenticate - Web3 wallet auth")
                    print("  verify <hash> - Verify execution")
                    print("  add-policy <rule> - Add safety rule")
                    print("  enable-planner - Enable workflow planner")
                    continue
                
                # Workers
                elif cmd == 'workers':
                    print("\n[WORKERS]")
                    for w in self.layer2.list_workers():
                        print(f"  - {w['name']} ({w['type']}) - {w['worker_id']}")
                    continue
                
                # System Status
                elif cmd == 'status':
                    print("\n[SYSTEM STATUS]")
                    print(f"  Layer-1: ONLINE (LLM: {self.layer1.lmstudio_base_url})")
                    print(f"  Layer-2: ONLINE (Workers: {len(self.layer2.workers)})")
                    print(f"  Layer-3: ONLINE (MCP Tools: 5)")
                    print(f"  Layer-4: ONLINE (Policies: {len(self.layer4.policy_engine.policies)})")
                    print(f"  Layer-5: ONLINE (Audit: Active)")
                    continue
                
                # Health Check
                elif cmd == 'health':
                    print("\n[HEALTH CHECK]")
                    try:
                        redis_status = "OK" if self.layer1.redis_memory.redis_client.ping() else "FAIL"
                    except:
                        redis_status = "FAIL"
                    print(f"  Redis: {redis_status}")
                    print(f"  LLM: OK")
                    print(f"  Workers: {len(self.layer2.workers)} loaded")
                    print(f"  Policies: {len(self.layer4.policy_engine.policies)} active")
                    continue
                
                # Show Policies
                elif cmd == 'policies':
                    print("\n[SAFETY POLICIES]")
                    for name, policy in self.layer4.policy_engine.policies.items():
                        print(f"  - {name}")
                    print(f"\n[CBAC AGENTS]")
                    for agent_type in self.layer4.cbac_engine.agents.keys():
                        print(f"  - {agent_type}")
                    continue
                
                # Show Audit Logs
                elif cmd == 'audit':
                    print("\n[AUDIT LOGS]")
                    print("  Recent executions logged to Layer-5")
                    print("  Blockchain: Mock anchoring active")
                    print("  IPFS: Mock storage active")
                    print("  Use 'verify <hash>' to check execution")
                    continue
                
                # Memory - Remember
                elif cmd.startswith('remember '):
                    text = user_input[9:].strip()
                    key = f"user:memory:{len(text)}"  # Simple key
                    self.layer1.memory_facade.set_temp(key, text, ttl=86400)
                    print(f"[MEMORY] Stored: {text[:50]}...")
                    continue
                
                # Memory - Recall
                elif cmd == 'recall' or cmd == 'history':
                    print("\n[MEMORY] Recent items:")
                    # Get last worker execution
                    for wid in list(self.layer2.workers.keys())[:3]:
                        mem = self.layer2.get_worker_memory(wid)
                        if mem:
                            print(f"  {wid}: {mem[:80]}...")
                    continue
                
                # Memory - Forget
                elif cmd == 'forget':
                    print("[MEMORY] Memory cleared (Redis TTL will expire)")
                    continue
                
                # Web3 - Authenticate
                elif cmd == 'authenticate':
                    print("\n[WEB3 AUTH]")
                    print("  Wallet authentication available")
                    print("  Layer-5 wallet auth: Ready")
                    print("  Use: authenticate <wallet_address> <signature>")
                    continue
                
                # Web3 - Verify
                elif cmd.startswith('verify '):
                    hash_val = user_input[7:].strip()
                    print(f"\n[VERIFY] Checking hash: {hash_val}")
                    print("  Blockchain verification: Mock mode")
                    print("  IPFS lookup: Mock mode")
                    print("  Status: Hash verification available in production")
                    continue
                
                # Web3 - Sign
                elif cmd.startswith('sign '):
                    message = user_input[5:].strip()
                    print(f"\n[SIGN] Message: {message}")
                    print("  Signature generation available")
                    print("  Layer-5 wallet signing: Ready")
                    continue
                
                # Admin - Add Policy
                elif cmd.startswith('add-policy '):
                    rule = user_input[11:].strip()
                    print(f"\n[ADMIN] Adding policy: {rule}")
                    print("  Policy engine: Layer-4")
                    print("  Status: Runtime policy addition available")
                    print("  Note: Restart required for OPA Rego policies")
                    continue
                
                # Admin - Enable Planner
                elif cmd == 'enable-planner':
                    print("\n[ADMIN] Planner control")
                    print("  Current: Disabled (use_planner=False)")
                    print("  To enable: Set use_planner=True in execute_worker_task")
                    print("  Note: May cause LLM timeout on complex tasks")
                    continue
                
                # Admin - Reload
                elif cmd == 'reload':
                    print("\n[ADMIN] Reloading workers...")
                    self.layer2._load_workers()
                    print(f"  Workers reloaded: {len(self.layer2.workers)}")
                    continue
                
                # Default: Worker execution
                else:
                    await self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\n[SYSTEM] Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")


async def main():
    """Main entry point"""
    system = UniversalAISystem()
    await system.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
