# Test Commands - Layer-5 Security Verification

## ✅ Safe Commands (No Approval Needed)

```bash
# These should work immediately:
You: launch notepad
You: open google.com
You: list files
You: echo hello world
You: status
You: workers
```

## ⚠️ Risky Commands (Requires Wallet + Approval)

```bash
# These will ask for Layer-5 wallet verification + approval:

You: install python-package
# Expected:
# [APPROVAL REQUIRED] Action: install python-package
# [LAYER-5 VERIFICATION] Wallet authentication required
# [LAYER-5] Enter wallet address: 0x123...
# [LAYER-5] Enter signature: 0xabc...
# [APPROVAL REQUIRED] Allow this action? (yes/no):

You: update system
# Will ask for wallet + approval

You: modify config
# Will ask for wallet + approval

You: configure settings
# Will ask for wallet + approval

You: change password
# Will ask for wallet + approval
```

## ❌ Dangerous Commands (Blocked Immediately)

```bash
# These should be BLOCKED with no approval option:

You: delete important.txt
# Expected: [ERROR] Dangerous delete command blocked

You: remove file.txt
# Expected: [ERROR] Dangerous delete command blocked

You: rm -rf folder
# Expected: [ERROR] Dangerous delete command blocked

You: format drive
# Expected: [ERROR] Dangerous delete command blocked
```

## 🧪 Test Sequence

### Test 1: Safe Command
```bash
You: launch notepad
# Should open notepad in NEW WINDOW (not in terminal)
# Should succeed immediately
```

### Test 2: Dangerous Command
```bash
You: delete test.txt
# Should be BLOCKED immediately
# No approval option
```

### Test 3: Risky Command (Full Flow)
```bash
You: install new-package

# Step 1: System asks for wallet
[LAYER-5] Enter wallet address: 0x1234567890abcdef
[LAYER-5] Enter signature: 0xabcdef1234567890

# Step 2: System verifies (mock mode will skip)
[LAYER-5] ✅ Wallet verified

# Step 3: System asks for approval
[APPROVAL REQUIRED] Allow this action? (yes/no): yes

# Step 4: Action approved
[APPROVAL] ✅ Action approved by user
[LAYER-5] ✅ Approval logged to blockchain
```

### Test 4: Risky Command (Denied)
```bash
You: update critical-system

# Enter wallet details...
[LAYER-5] Enter wallet address: 0x123...
[LAYER-5] Enter signature: 0xabc...

# Deny approval
[APPROVAL REQUIRED] Allow this action? (yes/no): no

# Expected:
[APPROVAL] ❌ Action denied by user
[ERROR] User denied approval
```

## 📊 Expected Results

### Security Levels Working:
- ✅ **Level 1 (Safe)**: Immediate execution
- ✅ **Level 2 (Risky)**: Wallet verification + User approval
- ✅ **Level 3 (Dangerous)**: Blocked completely

### Layer-5 Integration:
- ✅ Wallet authentication requested
- ✅ Signature verification (mock mode)
- ✅ Blockchain logging of approvals
- ✅ Audit trail maintained

## 🔐 Mock Wallet Details (For Testing)

Since Layer-5 is in mock mode, you can use any values:

```
Wallet Address: 0x1234567890abcdef1234567890abcdef12345678
Signature: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

The system will accept these in mock mode and log the approval.

## 🎯 What to Verify

1. ✅ Apps launch in NEW WINDOW (not in terminal)
2. ✅ Safe commands execute immediately
3. ✅ Dangerous commands are blocked
4. ✅ Risky commands ask for wallet
5. ✅ Risky commands ask for approval
6. ✅ Approvals are logged to Layer-5
7. ✅ Denials are logged to Layer-5

---

**Run these tests to verify your 3-tier security system!** 🔐
