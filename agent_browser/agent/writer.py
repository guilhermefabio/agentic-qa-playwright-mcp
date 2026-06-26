import re
from pathlib import Path


def write_generated_files(text: str, output_dir: Path = Path(".")) -> None:
    saved = False

    # Primary format: <file path="pages/foo.py"> ... </file>
    for rel_path, content in re.findall(r'<file path="([^"]+)">(.*?)</file>', text, re.DOTALL):
        _save(rel_path, content, output_dir)
        saved = True

    # Fallback: markdown fenced block with a leading comment like # pages/foo.py
    if not saved:
        for block in re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL):
            lines = block.splitlines()
            if lines and lines[0].strip().startswith("#"):
                candidate = lines[0].strip().lstrip("# ").strip()
                if "/" in candidate and candidate.endswith(".py"):
                    _save(candidate, "\n".join(lines[1:]), output_dir)
                    saved = True

    if not saved:
        print("  (nenhum arquivo gerado — o LLM não usou o formato <file path=...>)")


def _save(rel_path: str, content: str, output_dir: Path) -> None:
    target = output_dir / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  Arquivo salvo: {target}")
