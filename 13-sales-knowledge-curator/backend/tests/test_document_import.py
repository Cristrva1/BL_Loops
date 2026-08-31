from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from sales_curator.config import lab_root
from sales_curator.connectors.documents import DocumentImportError, import_document
from sales_curator.contracts.research import DocumentRights, RightsStatus
from sales_curator.hashing import sha256_bytes, sha256_text


def _rights() -> DocumentRights:
    return DocumentRights(
        rights_status=RightsStatus.EXPLICIT_PERMISSION,
        license="school-permission",
        usage_basis="Permiso escrito de la escuela",
        jurisdiction="MX",
        retention_allowed=True,
        extraction_allowed=True,
        quotation_allowed=True,
        redistribution_allowed=False,
        notebooklm_upload_allowed=False,
        evidence="Carta local verificada por el operador",
    )


def test_authorized_document_keeps_original_hash_and_writes_auditable_markdown(
    tmp_path: Path,
) -> None:
    inbox = tmp_path / "inbox"
    output = tmp_path / "output"
    inbox.mkdir()
    source = inbox / "lesson.docx"
    original = b"synthetic-docx-bytes"
    source.write_bytes(original)

    record = import_document(
        source,
        allowed_root=inbox,
        output_root=output,
        title="Leccion autorizada",
        author="Escuela local",
        language="es",
        rights=_rights(),
        topics=("ventas", "educacion"),
        converter=lambda _data, _suffix: "# Leccion\n\nTexto extraido y verificable.",
        extractor_version="test-1",
    )

    assert source.read_bytes() == original
    assert record.original_sha256 == sha256_bytes(original)
    markdown = (output / record.markdown_path).read_text(encoding="utf-8")
    assert record.markdown_sha256 == sha256_text(markdown)
    assert "original_sha256:" in markdown
    manifest = json.loads((output / record.manifest_path).read_text(encoding="utf-8"))
    assert manifest["rights"]["notebooklm_upload_allowed"] is False
    assert "synthetic-docx-bytes" not in json.dumps(manifest)


def test_document_outside_inbox_is_rejected(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"pdf")
    with pytest.raises(DocumentImportError, match="directorio permitido"):
        import_document(
            outside,
            allowed_root=inbox,
            output_root=tmp_path / "output",
            title="Documento externo",
            author="Autor",
            language="es",
            rights=_rights(),
            converter=lambda _data, _suffix: "texto",
            extractor_version="test-1",
        )


def test_document_output_outside_lab_is_rejected_before_conversion(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    source = inbox / "lesson.pdf"
    source.write_bytes(b"pdf")
    called = False

    def converter(_data: bytes, _suffix: str) -> str:
        nonlocal called
        called = True
        return "texto"

    with pytest.raises(DocumentImportError, match="laboratorio"):
        import_document(
            source,
            allowed_root=inbox,
            output_root=lab_root().parent / "forbidden-research-output",
            title="Documento externo",
            author="Autor",
            language="es",
            rights=_rights(),
            converter=converter,
            extractor_version="test-1",
        )
    assert called is False


def test_empty_document_projection_fails_closed(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    source = inbox / "empty.pdf"
    source.write_bytes(b"pdf")
    with pytest.raises(DocumentImportError, match="vacía"):
        import_document(
            source,
            allowed_root=inbox,
            output_root=tmp_path / "output",
            title="Documento vacio",
            author="Autor",
            language="es",
            rights=_rights(),
            converter=lambda _data, _suffix: "   ",
            extractor_version="test-1",
        )


def test_source_mutation_during_conversion_leaves_no_derived_artifacts(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    output = tmp_path / "output"
    inbox.mkdir()
    source = inbox / "lesson.pdf"
    source.write_bytes(b"synthetic-pdf")

    def mutating_converter(_data: bytes, _suffix: str) -> str:
        source.write_bytes(b"changed-during-conversion")
        return "# Derived content"

    with pytest.raises(DocumentImportError, match="consistencia"):
        import_document(
            source,
            allowed_root=inbox,
            output_root=output,
            title="Documento mutable",
            author="Escuela",
            language="es",
            rights=_rights(),
            converter=mutating_converter,
            extractor_version="test-1",
        )
    assert not output.exists() or list(output.rglob("*")) == []


def _synthetic_docx(text: str) -> bytes:
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
            'officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>",
        )
        archive.writestr(
            "word/document.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>",
        )
    return stream.getvalue()


def _synthetic_pdf(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, payload in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode() + payload + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(data)


@pytest.mark.parametrize(
    ("suffix", "contents", "expected"),
    [
        (".docx", _synthetic_docx("Authorized synthetic DOCX lesson"), "synthetic DOCX"),
        (".pdf", _synthetic_pdf("Authorized synthetic PDF lesson"), "synthetic PDF"),
    ],
)
def test_real_markitdown_extracts_synthetic_pdf_and_docx(
    tmp_path: Path, suffix: str, contents: bytes, expected: str
) -> None:
    inbox = tmp_path / "inbox"
    output = tmp_path / "output"
    inbox.mkdir()
    source = inbox / f"lesson{suffix}"
    source.write_bytes(contents)
    record = import_document(
        source,
        allowed_root=inbox,
        output_root=output,
        title="Authorized synthetic lesson",
        author="Synthetic school fixture",
        language="en",
        rights=_rights(),
    )
    markdown = (output / record.markdown_path).read_text("utf-8")
    assert expected in markdown
    assert record.extractor_version == "0.1.7"
