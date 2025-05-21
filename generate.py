import json
import os
import random
import shutil
from pathlib import Path

random.seed("prova-1")
PATH = Path(__file__).parent
TEMPLATES = PATH / "templates" / "templates"
ROOT = PATH / "templates" / "root"
UNICODE_SPACES = ["\u200b ", " \u200b", "\u200b \u200b", " \u200a", " "]
KEYS: dict[str, int] = {}


def transform(src: str) -> tuple[str, str]:
    line, body = src.split("\n", 1)
    line, *words = line.split()
    for word in words:
        line += random.choice(UNICODE_SPACES) + word
    src = line + "\n" + body
    return (line, src)


for i in range(1, 17):
    path = PATH / "provas" / f"prova-{i}"
    (path / "lox").mkdir(exist_ok=True, parents=True)

    # Cria diretórios de saídas
    path.mkdir(exist_ok=True)

    # Copia arquivos na raiz dos templates
    shutil.copytree(ROOT, path, dirs_exist_ok=True)

    # Q2: alpha ou beta
    alpha, beta = list(random.choice(["ab", "ba", "01", "10"]))
    first, second = sorted([alpha + "'s", beta + "'s"])
    layout = random.choice(["dot", "fdp", "neato", "circo"])

    q2_data = (TEMPLATES / "q2-regex-dfa.py").read_text()
    for k, v in {"ɑ's": first, "β's": second}.items():
        q2_data = q2_data.replace(k, v)
    table = str.maketrans({"ɑ": alpha, "β": beta})
    q2_data = q2_data.translate(table)
    (path / "q2-regex-dfa.py").write_text(q2_data)

    q2_test = (TEMPLATES / "tests" / "test_q2.py").read_text()
    q2_test = q2_test.translate(table)
    (path / "tests" / "test_q2.py").write_text(q2_test)

    q2_dot = (TEMPLATES / "q2.dot").read_text()
    q2_dot = q2_dot.translate(table)
    q2_dot = q2_dot.replace('layout = "dot"', f'layout = "{layout}"')
    (path / "q2.dot").write_text(q2_dot)
    os.system(f"dot -Tpng {path}/q2.dot -o {path}/q2.png")

    # Q3: Escolhe entre listas/tuplas
    q3 = random.choice(["listas", "tuplas"])
    shutil.copyfile(
        TEMPLATES / f"q3-gramatica-{q3}.md",
        path / "q3-gramatica.md",
    )
    shutil.copyfile(
        TEMPLATES / "tests" / f"test_q3-{q3}.py",
        path / "tests" / "test_q3.py",
    )

    # Q5: Escolhe entre fib/maior
    q5 = random.choice(["fib", "maior"])
    shutil.copyfile(
        TEMPLATES / f"q5-while-eval-{q5}.md",
        path / "q5-while-eval.md",
    )
    shutil.copyfile(
        TEMPLATES / "tests" / f"test_q5-{q5}.py",
        path / "tests" / "test_q5.py",
    )
    shutil.copyfile(
        TEMPLATES / f"{q5}.lox",
        path / f"{q5}.lox",
    )

    # /lox
    orig = TEMPLATES / "lox"
    dest = path / "lox"

    for name in ["ast.py", "transformer.py", "grammar.lark"]:
        (key, src) = transform((orig / name).read_text())
        (dest / name).write_text(src)
        assert key not in KEYS, f"Chave {key} já existe"
        KEYS[key] = i

json.dump(KEYS, open(PATH / "templates/keys.json", "w"), indent=2)
