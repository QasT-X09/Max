from __future__ import annotations

from pathlib import Path

import pythoncom
import win32com.client

from jarvis.security.sandbox import SandboxSecurityLayer


class WordAgent:
    def __init__(self, sandbox: SandboxSecurityLayer):
        self.sandbox = sandbox

    def _open_word(self, file_path: str | Path):
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        safe_path = str(self.sandbox.ensure_parent(file_path))
        if Path(safe_path).exists():
            doc = word.Documents.Open(safe_path)
        else:
            doc = word.Documents.Add()
            doc.SaveAs(safe_path)
        return word, doc, safe_path

    def insert_text(self, file_path: str, text: str) -> str:
        word, doc, safe_path = self._open_word(file_path)
        try:
            doc.Content.InsertAfter(text)
            doc.Save()
            return f"Inserted text into {safe_path}"
        finally:
            doc.Close(SaveChanges=True)
            word.Quit()

    def replace_text(self, file_path: str, old_text: str, new_text: str) -> str:
        word, doc, safe_path = self._open_word(file_path)
        try:
            find = doc.Content.Find
            find.Text = old_text
            find.Replacement.Text = new_text
            find.Execute(Replace=2)  # wdReplaceAll
            doc.Save()
            return f"Replaced text in {safe_path}"
        finally:
            doc.Close(SaveChanges=True)
            word.Quit()

    def save_document(self, file_path: str) -> str:
        word, doc, safe_path = self._open_word(file_path)
        try:
            doc.Save()
            return f"Saved {safe_path}"
        finally:
            doc.Close(SaveChanges=True)
            word.Quit()
