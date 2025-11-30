# QUICK REFERENCE GUIDE

## System Architecture (5 Layers)

```
USER → main.py → Layer-2 → Layer-4 → Layer-3 → Layer-5 → RESULT
                    ↓
                 Layer-1
```

## Layer Summary

| Layer | Purpose | Key Files | Integration |
|-------|---------|-----------|-------------|
| Layer-1 | Planner + Memory + LLM | layer1_main.py | Shared with Layer-2 |
| Layer-2 | Worker Orchestration | layer2_main.py | Hub for all layers |
| Layer-3 | MCP Tools | main.py (SimpleMCP) | Called by Layer-2 |
| Layer-4 | Safety & Governance | layer4_main.py | Validates Layer-2 |
| Layer-5 | Web3 & Audit | layer5_main.py | Logs Layer-2 |

## Execution Flow

```
1. User types command
2. main.py detects worker type
3. Layer-2 finds worker
4. Layer-4 validates action
5. Layer-3 executes tool
6. Layer-1 stores in memory
7. Layer-5 logs to audit
8. Result returned to user
```

## Worker Creation (3 Steps)

```bash
# 1. Copy blueprint
cp layer2/layer2/worker_blueprints/worker_blueprint.py my_worker.py

# 2. Edit 7 fields
worker_id, name, worker_type, capabilities, api_keys, endpoints, model_config

# 3. Run
python my_worker.py
```

## Commands (30+)

### Worker Commands
- `open <url>` - Browser
- `launch <app>` - App
- `list files` - File
- `echo <text>` - Terminal

### Memory Commands
- `remember <text>` - Store
- `recall` - Retrieve
- `forget` - Clear

### System Commands
- `status` - System status
- `health` - Health check
- `workers` - List workers
- `policies` - Show policies
- `audit` - Show logs

### Web3 Commands
- `authenticate` - Wallet auth
- `sign <msg>` - Sign
- `verify <hash>` - Verify

### Admin Commands
- `add-policy <rule>` - Add policy
- `enable-planner` - Enable planner
- `reload` - Reload workers

## File Locations

```
main.py                              # Main entry point
layer1/main/layer1_main.py          # Layer-1 orchestrator
layer2/layer2/layer2_main.py        # Layer-2 orchestrator
layer2/layer2/workers/*.json        # Worker configs
layer4/layer4/layer4_main.py        # Layer-4 orchestrator
layer5/layer5/layer5_main.py        # Layer-5 orchestrator
```

## Configuration

```bash
# .env file
LMSTUDIO_BASE_URL=http://192.168.1.6:1234
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Testing

```bash
# Run system test
python SYSTEM_TEST.py

# Run main system
python main.py
```

## Integration Points

### Layer-1 → Layer-2
- Planner shared
- Memory shared
- LLM shared

### Layer-2 → Layer-3
- Tool execution
- Worker-to-tool mapping

### Layer-2 → Layer-4
- Action validation
- Safety checks

### Layer-2 → Layer-5
- Audit logging
- Blockchain anchoring

## Data Flow

### Worker Config
```
Blueprint → JSON → Layer-2 Registry → Memory
```

### Execution
```
Command → Worker → Tool → Result → Memory → Audit
```

### Memory
```
Store → Redis (TTL) → Retrieve
```

### Audit
```
Action → IPFS → Blockchain → Audit Store
```

## API Quick Reference

### Layer-1
```python
planner.create_workflow(user_id, goal, context)
memory_facade.set_temp(key, value, ttl)
llm_connector.llm(prompt, max_tokens, temperature)
```

### Layer-2
```python
layer2.create_worker(...)
layer2.execute_worker_task(worker_id, task, context)
layer2.list_workers()
```

### Layer-3
```python
mcp.execute_tool(tool_name, params)
```

### Layer-4
```python
layer4.validate_action(action, context)
```

### Layer-5
```python
layer5.log_layer_action(layer, action, data, user_id)
```

## Troubleshooting

### Issue: Worker not found
**Solution**: Check `layer2/layer2/workers/` for JSON file

### Issue: LLM timeout
**Solution**: Set `use_planner=False` in execute_worker_task

### Issue: Redis connection failed
**Solution**: Start Redis: `docker-compose up -d`

### Issue: Command not recognized
**Solution**: Type `help` to see all commands

## Performance

- **Startup**: ~2 seconds
- **Command execution**: <1 second
- **Worker creation**: <1 second
- **Memory operations**: <100ms

## Security

- Layer-4 validates all actions
- CBAC enforces capabilities
- Sandbox execution available
- Blockchain audit trail
- Wallet-based authentication

## Scalability

- Horizontal: Add more workers
- Vertical: Increase Redis/LLM resources
- Distributed: Deploy layers separately

---

**For full documentation, see**: TECHNICAL_DOCUMENTATION.md
