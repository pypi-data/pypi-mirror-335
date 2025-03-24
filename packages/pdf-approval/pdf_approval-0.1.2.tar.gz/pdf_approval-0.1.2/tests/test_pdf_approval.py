import os
import pytest
import subprocess
from pdf_approval import approval_util

APPROVAL_DIR = "tests/approvals"

# Utility function to generate minimal PDF bytes for testing
def generate_mock_pdf(content=b"Hello World"):
    # A very basic (but valid enough) PDF structure in bytes.
    # Real PDFs are more complex, but this minimal example suffices for tests.
    pdf_header = b"%PDF-1.4\n"
    pdf_body = (
            b"1 0 obj\n"
            b"<< /Type /Catalog /Pages 2 0 R >>\n"
            b"endobj\n"
            b"2 0 obj\n"
            b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>\n"
            b"endobj\n"
            b"3 0 obj\n"
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>\n"
            b"endobj\n"
            b"4 0 obj\n"
            b"<< /Length 44 >>\n"
            b"stream\n"
            b"BT /F1 24 Tf 72 144 Td (" + content + b") Tj ET\n"
                                                    b"endstream\n"
                                                    b"endobj\n"
                                                    b"xref\n"
                                                    b"0 5\n"
                                                    b"0000000000 65535 f \n"
                                                    b"0000000010 00000 n \n"
                                                    b"0000000067 00000 n \n"
                                                    b"0000000118 00000 n \n"
                                                    b"0000000176 00000 n \n"
                                                    b"trailer\n"
                                                    b"<< /Size 5 /Root 1 0 R >>\n"
                                                    b"startxref\n"
                                                    b"250\n"
                                                    b"%%EOF"
    )
    return pdf_header + pdf_body



@pytest.fixture
def cleanup_files():
    """
    Fixture to clean up any approved/received PDFs created during tests
    in the default 'approvals' directory (or the root).
    """
    yield
    # Remove any approved/received files from the default approvals_dir
    if os.path.isdir(APPROVAL_DIR):
        for filename in os.listdir(APPROVAL_DIR):
            if filename.endswith(".approved.pdf") or filename.endswith(".received.pdf"):
                try:
                    os.remove(os.path.join(APPROVAL_DIR, filename))
                except OSError:
                    pass


def test_verify_pdf_no_approved_file_yet(cleanup_files):
    """
    Scenario: No approved file exists yet, so verify_pdf should create .received.pdf
    and raise AssertionError indicating we need to approve or rename.
    """
    # Generate PDF bytes
    pdf_bytes = generate_mock_pdf()
    base_name = "test_output"

    with pytest.raises(AssertionError) as exc_info:
        approval_util.verify_pdf(pdf_bytes, base_name)

    received_path = os.path.join(APPROVAL_DIR, "test_output.received.pdf")
    approved_path = os.path.join(APPROVAL_DIR, "test_output.approved.pdf")

    assert os.path.isfile(received_path), f"Expected .received.pdf to be created in {APPROVAL_DIR}."
    assert f"No approved file found at '{approved_path}'" in str(exc_info.value)


def test_verify_pdf_matches_approved(cleanup_files):
    """
    Scenario: We already have an approved file matching the new output.
    verify_pdf should pass silently (no AssertionError).
    """
    # Create a base PDF
    pdf_bytes = generate_mock_pdf()
    approved_path = os.path.join(APPROVAL_DIR, "test_match.approved.pdf")
    os.makedirs(APPROVAL_DIR, exist_ok=True)
    with open(approved_path, "wb") as f:
        f.write(pdf_bytes)

    approval_util.verify_pdf(pdf_bytes, "test_match")

    received_path = os.path.join(APPROVAL_DIR, "test_match.received.pdf")
    assert not os.path.isfile(received_path), "No received file should remain on a match."
    assert os.path.isfile(approved_path), "Approved file must remain."


def test_verify_pdf_mismatch(cleanup_files):
    """
    Scenario: An approved file exists, but the new PDF content is different.
    Expect an AssertionError and the creation of a .received.pdf file.
    """
    # Create an approved PDF
    approved_bytes = generate_mock_pdf(content=b"Approved Content")
    os.makedirs(APPROVAL_DIR, exist_ok=True)
    with open(os.path.join(APPROVAL_DIR, "test_mismatch.approved.pdf"), "wb") as f:
        f.write(approved_bytes)

    new_bytes = generate_mock_pdf(content=b"New Content")

    with pytest.raises(AssertionError) as exc_info:
        approval_util.verify_pdf(new_bytes, "test_mismatch")

    received_path = os.path.join(APPROVAL_DIR, "test_mismatch.received.pdf")
    assert os.path.isfile(received_path)
    assert "PDF mismatch detected!" in str(exc_info.value)


def test_approve_received(cleanup_files):
    """
    Scenario: We call verify_pdf, get a received file, then manually approve it
    using approve_received().
    """
    pdf_bytes = generate_mock_pdf(b"Initial content")
    base_name = "test_manual_approve"

    # This will fail because there's no approved file, creating .received.pdf
    with pytest.raises(AssertionError):
        approval_util.verify_pdf(pdf_bytes, base_name)

    received_path = os.path.join(APPROVAL_DIR, "test_manual_approve.received.pdf")
    assert os.path.isfile(received_path)

    approval_util.approve_received(base_name)

    approved_path = os.path.join(APPROVAL_DIR, "test_manual_approve.approved.pdf")
    assert os.path.isfile(approved_path)
    assert not os.path.isfile(received_path), "The .received.pdf file should have been promoted & removed."


    approval_util.verify_pdf(pdf_bytes, base_name)


def test_auto_approve(cleanup_files, monkeypatch):
    """
    Scenario: If auto-approve is enabled, mismatch does not raise an error.
    Instead, the .received.pdf file replaces .approved.pdf automatically.
    """
    monkeypatch.setenv("APPROVAL_AUTO_APPROVE", "1")

    old_bytes = generate_mock_pdf(content=b"Old Baseline")
    with open("auto_approve_test.approved.pdf", "wb") as f:
        f.write(old_bytes)

    new_bytes = generate_mock_pdf(content=b"Updated Content")
    approval_util.verify_pdf(new_bytes, "auto_approve_test")
    approved_path = os.path.join(APPROVAL_DIR, "auto_approve_test.approved.pdf")
    with open(approved_path, "rb") as f:
        updated_approved = f.read()

    assert updated_approved == new_bytes, "The auto-approved file should match new content."
    assert not os.path.exists(os.path.join(APPROVAL_DIR, "auto_approve_test.received.pdf"))

