from functools import reduce

def document_generator(*args: str) -> tuple[bool, str]:
    if not args:
        return (False, "Document could not be empty")
    return (True, _document(*args))

def _document(*args: str) -> str:
    l = reduce(lambda acc, s: acc + [s], args, [_begin_doc()])
    l = l + [_end_doc()]
    return "\n".join(l)

def _begin_doc() -> str:
    return "\n".join(["\\documentclass{article}", "\\usepackage{graphicx}", "\\begin{document}"])

def _end_doc() -> str:
    return "\\end{document}"


def table_generator(data: list[list[str]]) -> tuple[bool, str]:
    if not data:
        return (False, "Table must have at least one row")
    new_data = list(map(_row, data))
    column_number = len(data[0])
    return (True, "\n".join([_begin_table(column_number), "\n".join(new_data), _end_table()]))

def _begin_table(column_number: int) -> str:
    return f"\\begin{{center}}\n\\begin{{tabular}}{_schema(column_number)}"

def _end_table() -> str:
    return "\\hline" + "\n" + "\\end{tabular}" + "\n" + "\\end{center}"

def _schema(column_number: int) -> str:
    return "{|" + "|".join(map(lambda _: "c", range(column_number))) + "|}"

def _row(data: list[str]) -> str:
    return "\\hline\n" + " & ".join(data) + " \\\\"


def image_generator(path: str, scale: float) -> tuple[bool,str]:
    return (True, f"$$\\includegraphics[scale={scale}]{{{path}}}$$")
