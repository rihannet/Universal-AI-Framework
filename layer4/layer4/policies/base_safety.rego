package base_safety

# Default deny
default allow = false

# Block destructive commands
deny[msg] {
    input.action
    contains(input.action, "rm -rf /")
    msg := "Destructive command blocked: rm -rf /"
}

deny[msg] {
    input.action
    contains(input.action, "dd if=/dev/zero")
    msg := "Destructive command blocked: dd"
}

deny[msg] {
    input.action
    contains(input.action, "mkfs")
    msg := "Destructive command blocked: mkfs"
}

# Allow safe commands
allow {
    input.action
    not deny[_]
}
