import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


def parse_js_docs(file_path: str) -> Dict[str, Dict]:
    """Parse JavaScript file and extract documentation for function exports."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    docs = {}
    functions = content.split("export")

    for func in functions[1:]:
        name_match = re.search(r"(?:async\s+)?function\s+(\w+)", func)
        if not name_match:
            continue

        func_name = name_match.group(1)
        doc_block = extract_doc_block(func)
        if doc_block:
            docs[func_name] = doc_block

    return docs


def extract_doc_block(func_text: str) -> Optional[Dict]:
    """Extract documentation block from function text."""
    doc_lines = []
    in_doc = False

    lines = func_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "/**" in line:
            in_doc = True
            i += 1
            continue
        if "*/" in line:
            in_doc = False
            break
        if in_doc:
            cleaned = line.lstrip("*").strip()
            if cleaned:
                doc_lines.append(cleaned)
        i += 1

    if not doc_lines:
        return None

    doc_info = {
        "desc": doc_lines[0] if doc_lines else "",
        "params": [],
        "returns": None,
        "example": None,
    }

    i = 0
    while i < len(doc_lines):
        line = doc_lines[i]
        if line.startswith("@param"):
            param = parse_param(line)
            if param:
                doc_info["params"].append(param)
        elif line.startswith("@returns"):
            returns = parse_returns(line)
            if returns:
                doc_info["returns"] = returns
        elif line.startswith("@example"):
            # Collect all lines until the next @ or end of doc
            example_lines = []
            i += 1
            while i < len(doc_lines) and not doc_lines[i].startswith("@"):
                example_lines.append(doc_lines[i].strip())
                i += 1
            i -= 1  # Adjust for the outer loop increment
            if example_lines:
                doc_info["example"] = "\n".join(example_lines)
        i += 1

    return doc_info


def parse_param(line: str) -> Optional[Tuple[str, str, str]]:
    """Parse parameter line into (name, type, description)."""
    match = re.match(r"@param\s+{(.+?)}\s+(\w+)(?:,\s*(.+))?", line)
    if match:
        return (match.group(2), match.group(1), match.group(3) or "")
    return None


def parse_returns(line: str) -> Optional[Tuple[str, str]]:
    """Parse returns line into (type, description)."""
    match = re.match(r"@returns\s+{(.+?)}\s+(.+)", line)
    if match:
        return (match.group(1), match.group(2))
    return None


def generate_python_module(docs: Dict[str, Dict], module_name: str) -> str:
    """Generate Python module content with properly formatted documentation."""
    lines = [
        f"# Auto-generated documentation for {module_name}",
        "",
        f"{module_name}_docs = {{",
    ]

    for cmd_name, info in sorted(docs.items()):
        lines.append(f"    '{cmd_name}': {{")
        lines.append(f"        'desc': '''{info['desc']}''',")

        # Parameters
        lines.append("        'params': [")
        for param in info["params"]:
            lines.append(f"            ('{param[0]}', '{param[1]}', '''{param[2]}'''),")
        lines.append("        ],")

        # Returns
        if info["returns"]:
            lines.append(
                f"        'returns': ('{info['returns'][0]}', '''{info['returns'][1]}'''),"
            )
        else:
            lines.append("        'returns': None,")

        # Example
        if info["example"]:
            # Properly handle multiline examples
            example = info["example"].replace("'", "\\'")
            lines.append(f"        'example': '''{example}''',")
        else:
            lines.append("        'example': None,")

        lines.append("    },")

    lines.append("}")
    return "\n".join(lines)


def main():
    # Generate skills.py
    skills_docs = parse_js_docs("skills.js")
    with open("skills.py", "w", encoding="utf-8") as f:
        f.write(generate_python_module(skills_docs, "skills"))
    print("Generated skills.py")

    # Generate world.py
    world_docs = parse_js_docs("world.js")
    with open("world.py", "w", encoding="utf-8") as f:
        f.write(generate_python_module(world_docs, "world"))
    print("Generated world.py")


if __name__ == "__main__":
    main()
