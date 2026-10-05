# -*- coding: utf-8 -*-
"""Read-only PDF helpers for the regression suite (pypdf, BSD-3-Clause).

Historical tests inspected generated PDFs through PyMuPDF. PyMuPDF is banned
in Taxo (PROJECT_RULES.md §17), so the suite reads page count, page text and
embedded raster images through pypdf with the same small surface.
"""
from pypdf import PdfReader


class _Page:
    def __init__(self, page):
        self._page = page

    def get_text(self):
        return self._page.extract_text() or ""

    def get_images(self, full=True):
        return list(self._page.images)


class PdfFile:
    def __init__(self, path):
        self._reader = PdfReader(str(path))
        self._pages = [_Page(page) for page in self._reader.pages]

    @property
    def page_count(self):
        return len(self._pages)

    def __len__(self):
        return len(self._pages)

    def __iter__(self):
        return iter(self._pages)

    def __getitem__(self, index):
        return self._pages[index]

    def close(self):
        self._pages = []

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


def open_pdf(path):
    return PdfFile(path)
