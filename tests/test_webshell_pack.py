#!/usr/bin/env python3
"""Tests for WebShell-Pack — webshell_pack.py"""

import os
import sys
import tempfile
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from webshell_pack import generate, save, obfuscate, PAYLOADS, __version__


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _check_shell_code(code, shell_type):
    """Verify shell contains language-appropriate markers."""
    markers = {
        "php": "<?php",
        "asp": "<%",
        "jsp": "<%@page",
    }
    assert markers[shell_type] in code, f"Missing {shell_type} marker in:\n{code}"


# ---------------------------------------------------------------------------
# Generation tests
# ---------------------------------------------------------------------------

def test_version():
    assert __version__ == "1.0.0"


def test_generate_php_raw():
    code = generate("php")
    _check_shell_code(code, "php")
    assert "system" in code or "exec" in code or "shell_exec" in code or "passthru" in code


def test_generate_asp_raw():
    code = generate("asp")
    _check_shell_code(code, "asp")
    assert "WScript.Shell" in code or "Shell" in code


def test_generate_jsp_raw():
    code = generate("jsp")
    _check_shell_code(code, "jsp")
    assert "Runtime.getRuntime().exec" in code


def test_generate_with_auth():
    code = generate("php", auth="hunter2")
    assert "hunter2" in code


def test_generate_minimal_php():
    code = generate("php", minimal=True)
    _check_shell_code(code, "php")
    # Minimal — no whitespace padding
    assert code.strip() == code


def test_generate_minimal_asp():
    code = generate("asp", minimal=True)
    assert "<%" in code
    assert "%>" in code


def test_generate_minimal_jsp():
    code = generate("jsp", minimal=True)
    assert "<%@page" in code


# ---------------------------------------------------------------------------
# Obfuscation tests
# ---------------------------------------------------------------------------

def test_obfuscate_none():
    raw = PAYLOADS["php"]["raw"]
    result = obfuscate(raw, "none")
    assert result == raw


def test_obfuscate_low():
    raw = PAYLOADS["php"]["raw"]
    result = obfuscate(raw, "low")
    # Should have renamed 'c' parameter
    assert result != raw


def test_obfuscate_high():
    raw = PAYLOADS["php"]["raw"]
    result = obfuscate(raw, "high")
    assert result != raw


# ---------------------------------------------------------------------------
# Save tests
# ---------------------------------------------------------------------------

def test_save_file():
    with tempfile.NamedTemporaryFile(suffix=".php", delete=False, mode="w") as f:
        tmp = f.name
    try:
        code = generate("php")
        save(code, tmp)
        with open(tmp) as f:
            content = f.read()
        assert content == code
        assert len(code) > 0
    finally:
        os.unlink(tmp)


def test_save_creates_directory():
    with tempfile.TemporaryDirectory() as d:
        nested = os.path.join(d, "sub", "out.php")
        code = generate("php")
        save(code, nested)
        assert os.path.isfile(nested)
        os.unlink(nested)


# ---------------------------------------------------------------------------
# Payload file tests
# ---------------------------------------------------------------------------

def test_payload_files_exist():
    for fname in ("shell.php", "shell.asp", "shell.jsp"):
        path = os.path.join(os.path.dirname(__file__), "..", "payloads", fname)
        assert os.path.isfile(path), f"Missing payload: {path}"
        with open(path) as f:
            assert len(f.read()) > 0


def test_payload_php_works():
    path = os.path.join(os.path.dirname(__file__), "..", "payloads", "shell.php")
    with open(path) as f:
        code = f.read()
    assert "<?php" in code
    # Should execute a command — check for system/exec/shell_exec/passthru
    assert any(kw in code for kw in ("system", "exec", "shell_exec", "passthru"))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_unsupported_type():
    import pytest
    with pytest.raises(ValueError, match="Unsupported shell type"):
        generate("python")
