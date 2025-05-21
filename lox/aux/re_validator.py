import re
from types import SimpleNamespace

INSTANT_FEEDBACK = True
global_context = SimpleNamespace(n=0, results={})


def check_re(
    size: int,
    max_size: int,
    skip: bool = False,
    ctx=None,
):
    """
    Check regex patterns from decorated functions.
    """
    if ctx is None:
        ctx = global_context

    if skip:
        return lambda func: func

    def decorator(func):
        doc = func.__doc__
        name: str = func.__name__

        if name.startswith("_"):
            return report(name[1:], "ignorado", 0.0)

        try:
            regex = func()
        except Exception as e:
            print(f"Erro ao executar a função {name}:", e)
        accept, reject = parse_docstring(doc)

        n = len(accept)
        cheat_size = (n - 1) + sum(map(len, accept))
        assert (
            max_size < cheat_size
        ), f"{name}: {max_size=}, {cheat_size=} possível fazer ex1|ex2|ex3|...|exN e passar"

        name, _, weight = name.rpartition("_pt")
        weight = float(weight.replace("_", "."))

        def run_test():
            test_re_function(
                name,
                regex=regex,
                size=size,
                max_size=max_size,
                accept=accept,
                reject=reject,
                weight=weight,
                ctx=ctx,
            )

        func.run_test = run_test
        if INSTANT_FEEDBACK:
            run_test()

        return func

    return decorator


def setup_pytest():
    global INSTANT_FEEDBACK

    INSTANT_FEEDBACK = False


def reset_context():
    global global_context
    global_context = SimpleNamespace(n=0, results={})


def get_context():
    return global_context


def parse_docstring(doc: str) -> tuple[list[str], list[str]]:
    """
    Parse the docstring to extract accepted and rejected patterns.
    """
    accept = list[str]()
    reject = list[str]()

    lines = doc.strip().split("\n")
    current_list = None

    for line in lines:
        line = line.strip()

        if line == "aceita:":
            current_list = accept
        elif line == "recusa:":
            current_list = reject
        elif line and current_list is not None:
            current_list.append(line)

    return accept, reject


def test_re_function(
    name: str,
    regex: str,
    size: int,
    max_size: int,
    accept: list[str],
    reject: list[str],
    ctx: SimpleNamespace,
    weight: float = 1.0,
):
    """
    Test the regex function with the given size and max_size.
    """
    try:
        compiled = re.compile(regex)
    except re.error:
        return report(
            name, "erro", value=0.0, weight=weight, msg="regex inválida", ctx=ctx
        )

    for example in accept:
        if not compiled.fullmatch(example):
            msg = f"não aceitou exemplo '{example}'"
            return report(name, "erro", value=0.0, weight=weight, msg=msg, ctx=ctx)

    for example in reject:
        if compiled.fullmatch(example):
            msg = f"não recusou exemplo '{example}'"
            return report(name, "erro", value=0.0, weight=weight, msg=msg, ctx=ctx)

    if len(regex) <= size:
        report(name, "100%", value=1.0, weight=weight, ctx=ctx)
    elif len(regex) > max_size:
        n = len(regex) - max_size
        msg = f"excedeu o tamanho máximo por {n} caracteres"
        report(name, "erro", value=0.0, weight=weight, msg=msg, ctx=ctx)
    else:
        msg = f"regex {len(regex)} caracteres, tente fazer com {size}"
        report(name, "70%", value=0.7, weight=weight, msg=msg, ctx=ctx)


def report(
    name: str,
    result: str,
    value: float,
    weight: float,
    *,
    ctx,
    msg: str = "",
):
    name = name.replace("_", " ")
    ctx.n += 1
    ctx.results[name] = value * weight
    try:
        import rich
    except ImportError:
        msg = f" ({msg})" if msg else ""
        print(f"* [Q{ctx.n}] {name}: {result}")
        if msg:
            print(f"  - {msg}")
    else:
        style = "green" if value == 1.0 else ("yellow" if value > 0.7 else "red")
        rich.print(
            f"* [Q{ctx.n}] [bold blue]{name}:[/bold blue] [{style}]{result}[/{style}]"
        )
        if msg:
            print(f"  - {msg}")
    if value != 1.0:
        print()
