import re
from itertools import cycle, islice
from pathlib import Path
from random import choice, randint, random, randrange, shuffle
from types import SimpleNamespace

import pytest

MOD = Path(__file__).parent.parent / "q2-regex-dfa.py"

class NFA:
    def __init__(self, p_finish=0.25):
        self.start = "start"
        self.states = None
        self.transitions = {
            "start": {
                "b": {"A"},
            },
            "A": {
                "b": {"A", "C"},
                "a": {"B"},
            },
            "B": {
                "b": {"A", "B", "C"},
                "a": {"accept"},
            },
            "C": {},
            "accept": {},
        }
        self.p_finish = p_finish

    def accepts(self, data: str) -> bool:
        self.states = {self.start}
        for msg in data:
            if not self.step(msg):
                return False
        return "accept" in self.states

    def step(self, msg):
        if self.states is None:
            raise ValueError("NFA not initialized")
        elif not self.states:
            return False

        updated = set()
        for st in self.states:
            updated.update(self.transitions[st].get(msg, ()))

        self.states = updated
        return bool(self.states)

    def produce(self, n=None):
        yield from islice(self._produce(n, {self.start}, ""), n)

    def _produce(self, n, states, data):
        self.states = states

        while True:
            options = []

            if self.states == {"accept"}:
                yield data

            for st in self.states:
                if st == "accept" and random() < self.p_finish:
                    return data
                options.extend(self.transitions[st].keys())

            shuffle(options)
            for msg in options:
                new = NFA(p_finish=self.p_finish)
                new.states = self.states.copy()
                new.step(msg)
                yield from new._produce(n, new.states, data + msg)


ACCEPT: set[str] = set()

for ex in cycle(
    [NFA(0.15).produce(), NFA(0.25).produce(), NFA(0.5).produce(), NFA(0.75).produce()]
):
    ex = next(ex)
    if len(ACCEPT) >= 50:
        break
    elif ex not in ACCEPT:
        ACCEPT.add(ex)

REJECT: set[str] = set()
nfa = NFA()
for ex in ACCEPT:
    n = randrange(len(ex))
    ex1 = ex[:n] + choice("ba") + ex[n:]
    if not nfa.accepts(ex1):
        REJECT.add(ex1)

    n = max(n, 1)
    ex2 = ex[: n - 1] + ex[n:]
    if not nfa.accepts(ex2):
        REJECT.add(ex2)


while len(REJECT) < 200:
    n = randint(3, 15)
    ex = "".join(choice("ba") for _ in range(n))
    if not nfa.accepts(ex):
        REJECT.add(ex)


@pytest.fixture
def mod():
    src = MOD.read_text()
    exec(src, globals(), ns := {})
    ns.pop("__name__", None)
    ns.pop("__doc__", None)
    ns.pop("__module__", None)
    return SimpleNamespace(**ns)


def test_regex_pt15(mod):
    regex = re.compile(mod.regex)

    for exemplo in sorted(ACCEPT, key=len):
        assert (
            regex.fullmatch(exemplo) is not None
        ), f"Regex recusa exemplo correto: {exemplo}"

    for exemplo in sorted(REJECT, key=len):
        assert (
            regex.fullmatch(exemplo) is None
        ), f"Regex aceita exemplo incorreto: {exemplo}"


def test_menor_pt0_50(mod):
    assert len(mod.menor) == 3
    assert nfa.accepts(mod.menor)


def test_menor_ab_pt0_50(mod):
    assert len(mod.menor_ab) == 4
    assert nfa.accepts(mod.menor_ab)
    assert mod.menor_ab.count("b") == mod.menor_ab.count("a")


def test_string5_pt0_50(mod):
    assert len(mod.string_5) == 5
    assert nfa.accepts(mod.string_5)


def test_reject3_pt1_00(mod):
    assert len(mod.reject_3) >= 3
    for x in mod.reject_3:
        assert not nfa.accepts(x), f"A string {x} em reject_3 é válida"


def test_accept3_pt1_00(mod):
    assert len(mod.accept_3) >= 3
    for x in mod.accept_3:
        assert nfa.accepts(x), f"A string {x} em accept_3 é inválida"
