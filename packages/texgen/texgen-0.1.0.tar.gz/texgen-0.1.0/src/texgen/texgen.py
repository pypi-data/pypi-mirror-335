import os
from functools import reduce
from typing import Any

__all__ = ["generate_table", "generate_image"]


def _table(inner: str) -> str:
    return "\\begin{table}\n" + inner + "\\end{table}\n"


def _centering(inner: str, do: bool = True) -> str:
    return ("\\centering\n" if do else "") + inner


def _tabular(inner: str, cols: int) -> str:
    return (
        "\\begin{tabular}{"
        + "l".join("|" * (cols + 1))
        + "}\n"
        + inner
        + "\\end{tabular}\n"
    )


def _caption(inner: str, caption: str | None = None) -> str:
    return inner + (f"\\caption{{{caption}}}\n" if caption else "")


def _tabular_rows(data: list[list[Any]]) -> str:
    return "\\hline\n" + "\\hline\n".join(map(_tabular_row, data)) + "\\hline\n"


def _tabular_row(data: list[Any]) -> str:
    return " & ".join(map(str, data)) + r" \\" + "\n"


def generate_table(
    data: list[list[Any]],
    centering: bool = False,
    caption: str | None = None,
) -> str:
    return _table(
        _centering(
            _caption(
                _tabular(
                    _tabular_rows(data),
                    len(data[0]),
                ),
                caption,
            ),
            centering,
        )
    )


def _figure_tags(inner: str) -> str:
    return "\\begin{figure}\n" + inner + "\\end{figure}\n"


def _image(path_to_image: str, width_factor: float) -> str:
    return f"\\includegraphics[width={width_factor}\linewidth]{{{path_to_image}}}\n"


def _package(inner: str, package: str) -> str:
    return f"\\usepackage{{{package}}}\n" + inner


def generate_image(
    path_to_image: str,
    width_factor: float = 0.25,
    centering: bool = False,
    caption: str | None = None,
) -> str:
    return _figure_tags(
        _centering(
            _caption(
                _image(
                    path_to_image,
                    width_factor,
                ),
                caption,
            ),
            centering,
        )
    )


def _article(inner: str) -> str:
    return "\\documentclass{article}\n" + inner


def _document(inner: str) -> str:
    return "\\begin{document}\n" + inner + "\\end{document}\n"


def generate_document(content_tex: str, packages: list[str] | None = None) -> str:
    return _article(reduce(_package, packages or [], _document(content_tex)))
