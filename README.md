# Universal AI Framework - 5-Layer Orchestration System

> **⚠️ PROTOTYPE NOTICE**: This is a prototype/demonstration system. Layer-5 Web3 features (wallet authentication, blockchain anchoring, IPFS storage) use mock implementations for testing. For production use, integrate real Web3 services.

## 📌 Post-Submission Improvements (Non-Evaluated)

After submission, we experimented with optional enhancements in **main2.py**:
- LLM-based automatic worker selection
- Always-on planner mode

These changes do NOT alter the core architecture or design goals. The original rule-based routing and conditional planner logic in **main.py** remain valid and were the basis of the hackathon submission.

**📄 For details on the enhanced version, see [main2.py](main2.py) and [README2.md](README2.md)**

---

Multi-layer AI orchestration framework with natural language interface, worker management, safety governance, and blockchain audit trails.

## 🎯 Features

- ✅ **5-Layer Architecture** - Planner, Workers, MCP, Safety, Audit
- ✅ **Natural Language Interface** - Talk to your system naturally
- ✅ **30+ Commands** - Memory, audit, policies, Web3, admin controls
- ✅ **5 Built-in Workers** - Browser, Terminal, App, File, API
- ✅ **Custom Worker Creation** - Create ANY worker type via blueprints
- ✅ **Safety & Governance** - Policy engine with CBAC
- ✅ **Blockchain Audit** - Tamper-proof execution logs
- ✅ **Memory System** - Redis-backed episodic memory
- ✅ **Web3 Authentication** - Wallet-based identity

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start services
docker-compose up -d

# 3. Configure environment
cp .env.example .env
        # Redis Configuration
        REDIS_HOST=
        REDIS_PORT=

        # PostgreSQL Configuration
        POSTGRES_HOST=
        POSTGRES_PORT=
        POSTGRES_DB=
        POSTGRES_USER=
        POSTGRES_PASSWORD=

        # LM Studio Configuration (DeepSeek R1)
        LMSTUDIO_BASE_URL=
        LM_STUDIO_HOST=
        LM_STUDIO_PORT=
        # Pinecone Configuration (Optional - for vector memory)
        PINECONE_API_KEY=

        # Worker Configuration
        WORKER_ID=
        REDIS_URL=

        # Optional: IPFS and Ethereum
        IPFS_API_URL=
        ETH_RPC_URL=

        # Edit .env with your settings

# 4. Setup LLM
# Download DeepSeek R1 from LM Studio or use OpenAI API
# Update LMSTUDIO_BASE_URL in .env

# 5. Run system (original version)
python main.py

# OR run enhanced version
python main2.py
```

## 💬 How to Use

### Basic Commands
```bash
You: open google.com          # Opens browser
You: launch notepad           # Launches app
You: list files               # Lists files
You: echo hello world         # Terminal command
You: remember important data  # Store in memory
You: recall                   # Retrieve memory
You: status                   # System status
You: workers                  # List all workers
You: help                     # Show all commands
```

### Create Custom Worker
```bash
# 1. Copy blueprint
cp layer2/layer2/worker_blueprints/worker_blueprint.py my_worker.py

# 2. Edit these 7 fields:
worker_id = "my_worker"
name = "My Worker"
worker_type = "custom"
capabilities = ["capability1"]
api_keys = {}
endpoints = {}
model_config = {"temperature": 0.7, "max_tokens": 2048}

# 3. Run to create
python my_worker.py

# 4. Restart system
python main.py

# 5. Use your worker
You: <command for your worker>
```

## 🏗️ System Architecture

```
User Input
    ↓
main.py (Natural Language Interface)
    ↓
Layer-2 (Worker Orchestration)
    ↓
Layer-4 (Safety Check) → Layer-3 (Tool Execution) → Layer-5 (Audit Log)
    ↓
Layer-1 (Planner + Memory + LLM)
    ↓
Result
```

### 5 Layers Explained

**Layer-1**: Planner + Memory + LLM
- Plans workflows
- Stores memory (Redis)
- LLM integration

**Layer-2**: Worker Orchestration
- Manages workers
- Routes tasks
- Integrates all layers

**Layer-3**: MCP Tools
- Executes commands
- 5 tools: shell, browser, app, http_api, file

**Layer-4**: Safety & Governance
- Validates actions
- Enforces policies
- CBAC access control

**Layer-5**: Web3 Identity & Audit
- Blockchain audit trail
- IPFS storage
- Wallet authentication

## 📖 Documentation

- **TECHNICAL_DOCUMENTATION.md** - Complete technical specs
- **QUICK_REFERENCE.md** - Command reference
- **DOCUMENTATION_INDEX.md** - Navigation guide
- **README2.md** - Enhanced version details (main2.py)

## 🧪 Testing

```bash
python SYSTEM_TEST.py
```

Expected:
```
[OK] Layer-1: WORKING
[OK] Layer-2: WORKING
[OK] Layer-4: WORKING
[OK] Layer-5: WORKING
[OK] Workers: 5 available
```

## ⚙️ Configuration

### .env File
```bash
LMSTUDIO_BASE_URL=
REDIS_HOST=
REDIS_PORT=
POSTGRES_HOST=
POSTGRES_PORT=
```

### LLM Setup
**Note**: Model files NOT included.

Options:
1. LM Studio + DeepSeek R1 model
2. OpenAI API
3. Any compatible LLM endpoint

Update `LMSTUDIO_BASE_URL` in `.env`

## 📁 Project Structure

```
AWS HACKATHON/
├── main.py                    # Main entry point (original)
├── main2.py                   # Enhanced version (post-submission)
├── README.md                  # This file
├── README2.md                 # Enhanced version documentation
├── SYSTEM_TEST.py             # System tests
├── requirements.txt           # Dependencies
├── docker-compose.yml         # Docker services
├── .env.example               # Config template
│
├── layer1/                    # Planner + Memory + LLM
│   ├── main/
│   ├── planner/
│   ├── memory/
│   ├── llm_engine/
│   └── state_manager/
│
├── layer2/                    # Worker Orchestration
│   └── layer2/
│       ├── layer2_main.py
│       ├── workers/           # 5 worker configs
│       └── worker_blueprints/ # Templates
│
├── layer4/                    # Safety & Governance
│   └── layer4/
│       ├── layer4_main.py
│       └── policies/          # OPA Rego policies
│
├── layer5/                    # Web3 Identity & Audit
│   └── layer5/
│       ├── layer5_main.py
│       └── services/
│
└── mcp/                       # MCP Layer-3
    └── app/
```

## 🔧 Advanced Usage

### All Commands (30+)

**Worker Execution**
- `open <url>` - Browser
- `launch <app>` - App launcher
- `list files` - File operations
- `echo <text>` - Terminal
- Any shell command

**Memory Management**
- `remember <text>` - Store
- `recall` - Retrieve
- `history` - Show history
- `forget` - Clear

**System Commands**
- `status` - System status
- `health` - Health check
- `workers` - List workers
- `policies` - Show policies
- `audit` - Audit logs

**Web3 Commands**
- `authenticate` - Wallet auth
- `sign <message>` - Sign
- `verify <hash>` - Verify

**Admin Commands**
- `add-policy <rule>` - Add policy
- `enable-planner` - Enable planner
- `reload` - Reload workers

### Running Individual Layers

```bash
# Layer-1 only
python -c "from layer1.main.layer1_main import Layer1Main; l1 = Layer1Main()"

# Layer-2 only
python -c "from layer2.layer2.layer2_main import create_layer2; l2 = create_layer2()"

# Layer-4 only
python -c "from layer4.layer4.layer4_main import create_layer4; l4 = create_layer4()"

# Layer-5 only
python -c "from layer5.layer5.layer5_main import create_layer5; l5 = create_layer5()"

# Full system (original)
python main.py

# Full system (enhanced)
python main2.py
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

MIT License

## 🎉 Acknowledgments

Built for AWS Hackathon 2025

---

**Version**: 1.0.0  
**Documentation**: Complete
