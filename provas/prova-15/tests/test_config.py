from pathlib import Path


def test_registrou_cinco_questões_no_prova_py():
    path = Path(__file__).parent.parent / "prova.py"

    exec(path.read_text(), {"__name__": "prova"}, ns := {})
    questoes = ns["questoes"]
    assert len(questoes) <= 5, f"Lembre-se de comentar uma questão no prova.py"
    assert len(questoes) != 5, f"Não se esqueça de selecionar as 5 questões desejadas no prova.py"