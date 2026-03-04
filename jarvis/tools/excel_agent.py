from __future__ import annotations

from pathlib import Path
from typing import Any

import pythoncom
import win32com.client

from jarvis.security.sandbox import SandboxSecurityLayer


class ExcelAgent:
    def __init__(self, sandbox: SandboxSecurityLayer):
        self.sandbox = sandbox

    def _open_excel(self, file_path: str | Path):
        pythoncom.CoInitialize()
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        safe_path = str(self.sandbox.ensure_parent(file_path))
        workbook = excel.Workbooks.Open(safe_path) if Path(safe_path).exists() else excel.Workbooks.Add()
        if not Path(safe_path).exists():
            workbook.SaveAs(safe_path)
        return excel, workbook, safe_path

    def write_cell(self, file_path: str, sheet_name: str, cell: str, value: Any) -> str:
        excel, workbook, safe_path = self._open_excel(file_path)
        try:
            sheet = self._get_or_create_sheet(workbook, sheet_name)
            sheet.Range(cell).Value = value
            workbook.Save()
            return f"Wrote value to {sheet_name}!{cell} in {safe_path}"
        finally:
            workbook.Close(SaveChanges=True)
            excel.Quit()

    def read_range(self, file_path: str, sheet_name: str, range_ref: str) -> list[list[Any]]:
        excel, workbook, _ = self._open_excel(file_path)
        try:
            sheet = workbook.Worksheets(sheet_name)
            values = sheet.Range(range_ref).Value
            if isinstance(values, tuple):
                return [list(row) if isinstance(row, tuple) else [row] for row in values]
            return [[values]]
        finally:
            workbook.Close(SaveChanges=False)
            excel.Quit()

    def set_formula(self, file_path: str, sheet_name: str, cell: str, formula: str) -> str:
        excel, workbook, safe_path = self._open_excel(file_path)
        try:
            sheet = self._get_or_create_sheet(workbook, sheet_name)
            sheet.Range(cell).Formula = formula
            workbook.Save()
            return f"Set formula in {sheet_name}!{cell} for {safe_path}"
        finally:
            workbook.Close(SaveChanges=True)
            excel.Quit()

    def create_sheet(self, file_path: str, sheet_name: str) -> str:
        excel, workbook, safe_path = self._open_excel(file_path)
        try:
            self._get_or_create_sheet(workbook, sheet_name)
            workbook.Save()
            return f"Created or reused sheet '{sheet_name}' in {safe_path}"
        finally:
            workbook.Close(SaveChanges=True)
            excel.Quit()

    @staticmethod
    def _get_or_create_sheet(workbook, sheet_name: str):
        for sheet in workbook.Worksheets:
            if sheet.Name == sheet_name:
                return sheet
        sheet = workbook.Worksheets.Add()
        sheet.Name = sheet_name
        return sheet
