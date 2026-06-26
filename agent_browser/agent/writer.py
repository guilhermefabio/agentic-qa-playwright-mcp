import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def write_generated_files(text: str) -> None:
    saved = False

    # Primary format: <file path="pages/foo.py"> ... </file>
    for rel_path, content in re.findall(r'<file path="([^"]+)">(.*?)</file>', text, re.DOTALL):
        _save(rel_path, content)
        saved = True

    # Fallback: markdown fenced block with a leading comment like # pages/foo.py
    if not saved:
        for block in re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL):
            lines = block.splitlines()
            if lines and lines[0].strip().startswith("#"):
                candidate = lines[0].strip().lstrip("# ").strip()
                if "/" in candidate and candidate.endswith(".py"):
                    _save(candidate, "\n".join(lines[1:]))
                    saved = True

    if not saved:
        print("  (nenhum arquivo gerado — o LLM não usou o formato <file path=...>)")


def _save(rel_path: str, content: str) -> None:
    target = BASE_DIR / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  Arquivo salvo: {rel_path}")
