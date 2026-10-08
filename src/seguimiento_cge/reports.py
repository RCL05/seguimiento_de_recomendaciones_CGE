from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from io import BytesIO
from typing import Iterable, List
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .models import InformeCGE, Recomendacion


@dataclass(frozen=True)
class MatrixRow:
    informe: str
    recomendacion: str
    estado: str
    fecha_maxima_cumplimiento: str


class ReportExporter:
    @staticmethod
    def build_matrix(
        informe: InformeCGE,
        recomendaciones: Iterable[Recomendacion],
    ) -> List[MatrixRow]:
        return [
            MatrixRow(
                informe=informe.numero_informe,
                recomendacion=r.numero_recomendacion,
                estado=r.estado_actual.value,
                fecha_maxima_cumplimiento=r.fecha_maxima_cumplimiento.isoformat(),
            )
            for r in recomendaciones
        ]

    @classmethod
    def export_matrix_to_pdf(
        cls,
        informe: InformeCGE,
        recomendaciones: Iterable[Recomendacion],
    ) -> bytes:
        matrix = cls.build_matrix(informe, recomendaciones)
        lines = [
            "Matriz Institucional de Seguimiento CGE",
            f"Informe: {informe.numero_informe} - {informe.titulo_examen}",
            "",
            "Rec | Estado | Fecha máxima",
        ]
        lines.extend(
            f"{row.recomendacion} | {row.estado} | {row.fecha_maxima_cumplimiento}"
            for row in matrix
        )
        return _SimplePdfWriter.from_lines(lines)

    @classmethod
    def export_matrix_to_excel(
        cls,
        informe: InformeCGE,
        recomendaciones: Iterable[Recomendacion],
    ) -> bytes:
        matrix = cls.build_matrix(informe, recomendaciones)
        headers = ["Informe", "Recomendación", "Estado", "Fecha Máxima"]
        rows = [
            [row.informe, row.recomendacion, row.estado, row.fecha_maxima_cumplimiento]
            for row in matrix
        ]
        return _SimpleXlsxWriter.create_sheet("Matriz", [headers, *rows])


class _SimplePdfWriter:
    @staticmethod
    def from_lines(lines: Iterable[str]) -> bytes:
        y = 780
        text_ops = ["BT", "/F1 10 Tf", "72 800 Td"]
        first = True
        for line in lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if first:
                text_ops.append(f"({safe}) Tj")
                first = False
            else:
                y -= 14
                text_ops.append(f"72 {y} Td")
                text_ops.append(f"({safe}) Tj")
        text_ops.append("ET")
        stream = "\n".join(text_ops).encode("utf-8")

        objects = [
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
            b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
            b"5 0 obj << /Length " + str(len(stream)).encode("utf-8") + b" >> stream\n" + stream + b"\nendstream endobj\n",
        ]

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(len(pdf))
            pdf.extend(obj)
        xref_pos = len(pdf)
        pdf.extend(f"xref\n0 {len(offsets)}\n".encode("utf-8"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("utf-8"))
        pdf.extend(
            (
                "trailer << /Root 1 0 R /Size "
                f"{len(offsets)} >>\nstartxref\n{xref_pos}\n%%EOF\n"
            ).encode("utf-8")
        )
        return bytes(pdf)


class _SimpleXlsxWriter:
    @staticmethod
    def create_sheet(sheet_name: str, rows: List[List[str]]) -> bytes:
        data = BytesIO()
        with ZipFile(data, "w", ZIP_DEFLATED) as zip_file:
            zip_file.writestr("[Content_Types].xml", _content_types_xml())
            zip_file.writestr("_rels/.rels", _rels_xml())
            zip_file.writestr("xl/workbook.xml", _workbook_xml(sheet_name))
            zip_file.writestr("xl/_rels/workbook.xml.rels", _workbook_rels_xml())
            zip_file.writestr("xl/worksheets/sheet1.xml", _sheet_xml(rows))
        return data.getvalue()


def _content_types_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
  <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
</Types>
"""


def _rels_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>
"""


def _workbook_xml(sheet_name: str) -> str:
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"{escape(sheet_name)}\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
</workbook>
"""


def _workbook_rels_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
</Relationships>
"""


def _sheet_xml(rows: List[List[str]]) -> str:
    row_fragments = []
    for i, row in enumerate(rows, start=1):
        cell_fragments = []
        for j, value in enumerate(row, start=1):
            col = _column_name(j)
            cell_fragments.append(
                f"<c r=\"{col}{i}\" t=\"inlineStr\"><is><t>{escape(str(value))}</t></is></c>"
            )
        row_fragments.append(f"<row r=\"{i}\">{''.join(cell_fragments)}</row>")

    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheetData>""" + "".join(row_fragments) + """</sheetData>
</worksheet>
"""


def _column_name(index: int) -> str:
    result = ""
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        result = chr(65 + remainder) + result
    return result
