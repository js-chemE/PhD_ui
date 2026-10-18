"""
Text helpers shared by figures, slides and notes.

The one thing here is the house citation string (set 2026-10-18, see
``CLAUDE.md``, "Text & plot style conventions"):

    <first author> et al. (<group lead>), <journal abbreviation> <year>

e.g. ``Vico van Berkel et al. (Urakawa), J. Catal. 2024``. The bracket names
the professor or well-known name behind the paper, usually the last author,
and is dropped when the first author is that name.
"""

__all__ = ["cite"]


def cite(
    first_author: str,
    journal: str,
    year: int | str,
    lead: str | None = None,
    *,
    second_author: str | None = None,
    et_al: bool = True,
) -> str:
    """
    Build the house citation string for a stand-alone reference (slide, figure).

    Parameters
    ----------
    first_author : str
        Surname of the first author, with its particles, e.g.
        ``"Vico van Berkel"``.
    journal : str
        Journal abbreviation as Zotero gives it (ISO 4, with dots), e.g.
        ``"J. Catal."``.
    year : int or str
        Year of publication.
    lead : str, optional
        Surname of the group lead (the professor or well-known name behind
        the paper, usually the last author). Omitted from the string when it
        equals `first_author` or is not given.
    second_author : str, optional
        Surname of the second author, for a two-author paper written
        ``A & B``. Requires ``et_al=False``.
    et_al : bool, optional
        ``True`` (default) for three or more authors (``A et al.``);
        ``False`` for one author (``A``) or, with `second_author`, two.

    Returns
    -------
    str
        The citation, e.g. ``"Vico van Berkel et al. (Urakawa), J. Catal. 2024"``,
        ``"Maeder & Zilian, Chemom. Intell. Lab. Syst. 1988"``,
        ``"Noda, Appl. Spectrosc. 1993"``.

    Raises
    ------
    ValueError
        If `second_author` is given together with ``et_al=True``.
    """
    if second_author is not None and et_al:
        raise ValueError("a two-author paper is written 'A & B': pass et_al=False with second_author")
    if et_al:
        authors = f"{first_author} et al."
    elif second_author is not None:
        authors = f"{first_author} & {second_author}"
    else:
        authors = first_author
    if lead is not None and lead.strip().casefold() != first_author.strip().casefold():
        authors = f"{authors} ({lead})"
    return f"{authors}, {journal} {year}"
