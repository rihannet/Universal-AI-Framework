"""System Test - Verify All Components"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("SYSTEM TEST - Universal AI Framework")
print("=" * 70)

print("\n[TEST 1] Checking imports...")
try:
    from layer1.main.layer1_main import Layer1Main
    from layer2.layer2.layer2_main import create_layer2
    from layer4.layer4.layer4_main import create_layer4
    from layer5.layer5.layer5_main import create_layer5
    print("[OK] All imports successful")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

print("\n[TEST 2] Initializing Layer-1...")
try:
    layer1 = Layer1Main(
        lmstudio_base_url="http://192.168.1.6:1234",
        redis_host="localhost",
        redis_port=6379
    )
    print("[OK] Layer-1 initialized")
except Exception as e:
    print(f"[FAIL] Layer-1 failed: {e}")
    sys.exit(1)

print("\n[TEST 3] Initializing Layer-4...")
try:
    layer4 = create_layer4()
    print("[OK] Layer-4 initialized")
except Exception as e:
    print(f"[FAIL] Layer-4 failed: {e}")
    sys.exit(1)

print("\n[TEST 4] Initializing Layer-5...")
try:
    layer5 = create_layer5()
    print("[OK] Layer-5 initialized")
except Exception as e:
    print(f"[FAIL] Layer-5 failed: {e}")
    sys.exit(1)

print("\n[TEST 5] Initializing Layer-2...")
try:
    layer2 = create_layer2(
        lmstudio_base_url="http://192.168.1.6:1234",
        redis_host="localhost",
        redis_port=6379,
        layer1_planner=layer1.planner,
        layer3_mcp=None,
        layer4_safety=layer4,
        layer5_audit=layer5
    )
    print(f"[OK] Layer-2 initialized with {len(layer2.workers)} workers")
except Exception as e:
    print(f"[FAIL] Layer-2 failed: {e}")
    sys.exit(1)

print("\n[TEST 6] Checking workers...")
try:
    workers = layer2.list_workers()
    if len(workers) >= 3:
        print(f"[OK] Found {len(workers)} workers:")
        for w in workers:
            print(f"   - {w['name']} ({w['type']})")
    else:
        print(f"[WARN] Only {len(workers)} workers found")
except Exception as e:
    print(f"[FAIL] Worker check failed: {e}")

print("\n[TEST 7] Checking file structure...")
required_files = [
    "main.py",
    "requirements.txt",
    ".env",
    "docker-compose.yml",
    "README.md",
    "TECHNICAL_DOCUMENTATION.md",
    "QUICK_REFERENCE.md"
]

missing = []
for file in required_files:
    if not Path(file).exists():
        missing.append(file)

if not missing:
    print("[OK] All required files present")
else:
    print(f"[WARN] Missing files: {', '.join(missing)}")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("[OK] Layer-1: WORKING")
print("[OK] Layer-2: WORKING")
print("[OK] Layer-4: WORKING")
print("[OK] Layer-5: WORKING")
print(f"[OK] Workers: {len(workers)} available")
print("=" * 70)
print("\nSystem is ready!")
print("\nRun: python main.py")
print("=" * 70)
