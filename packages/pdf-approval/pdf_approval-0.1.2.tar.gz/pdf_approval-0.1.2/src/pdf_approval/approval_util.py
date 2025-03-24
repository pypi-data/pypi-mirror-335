"""
Approval testing utility for comparing PDF outputs by raw bytes.

Features:
- Approved vs Received PDF files stored on disk.
- Raises an AssertionError on mismatch to fail tests.
- Allows easy promotion of 'received' files to 'approved' baselines.
"""

import os
import shutil

AUTO_APPROVE = False
DEFAULT_APPROVAL_DIR = "tests/approvals"

def set_auto_approve(enable: bool = True):
    """
    Enable or disable auto-approval of received files.
    If enabled, differences won't cause a failure;
    instead the approved file is replaced automatically.
    """
    global AUTO_APPROVE
    AUTO_APPROVE = enable


def verify_pdf(content_bytes: bytes, file_base_name: str, approvals_dir: str = DEFAULT_APPROVAL_DIR):
    """
    Compare the given PDF content (bytes) to an approved PDF file on disk.

    :param content_bytes: Newly generated PDF bytes to verify
    :param file_base_name: Base name/path for the approval files.
                 e.g. "reports/monthly_report" ->
                 uses "reports/monthly_report.approved.pdf" & ".received.pdf"
    :param approvals_dir: Folder where the library should place .approved.pdf and .received.pdf
                          if `name` isn't already an absolute path or includes its own directory.
                          Defaults to "tests/approvals" (relative to the current working directory).
    :raises AssertionError: if mismatch found and auto-approve is off
    """
    base_path = _build_base_path(file_base_name, approvals_dir)
    approved_path, received_path = _build_pdf_paths(base_path)
    approved_exists = os.path.isfile(approved_path)
    approved_bytes = None
    if approved_exists:
        with open(approved_path, "rb") as f:
            approved_bytes = f.read()

    files_match = (approved_bytes == content_bytes) if approved_exists else False

    if files_match:
        if os.path.exists(received_path):
            try:
                os.remove(received_path)
            except OSError:
                pass
        return  # All good, pass silently

    os.makedirs(os.path.dirname(received_path) or ".", exist_ok=True)
    with open(received_path, "wb") as f:
        f.write(content_bytes)

    auto_approve_env = (os.getenv("APPROVAL_AUTO_APPROVE", "0") == "1")
    if AUTO_APPROVE or auto_approve_env:
        shutil.move(received_path, approved_path)
        print(f"[pdf_approval] Auto-approved: {approved_path} updated.")
        return

    if not approved_exists:
        raise AssertionError(
            f"No approved file found at '{approved_path}'.\n"
            f"Received file written to '{received_path}'.\n"
            f"Inspect & rename (or approve) to proceed."
        )
    else:
        raise AssertionError(
            f"PDF mismatch detected!\n"
            f"Approved: '{approved_path}'\n"
            f"Received: '{received_path}'\n"
            f"Use a diff tool to review differences. If correct, approve by replacing or renaming."
        )


def approve_received(name: str, approvals_dir: str = DEFAULT_APPROVAL_DIR):
    """
    Manually promote a '.received.pdf' file to '.approved.pdf'.
    """
    base_path = _build_base_path(name, approvals_dir)
    approved_path, received_path = _build_pdf_paths(base_path)

    if not os.path.exists(received_path):
        raise FileNotFoundError(f"No received file found at '{received_path}' to approve.")

    os.makedirs(os.path.dirname(approved_path) or ".", exist_ok=True)
    shutil.move(received_path, approved_path)
    print(f"Promoted '{received_path}' to '{approved_path}'")

def _build_base_path(name: str, approvals_dir: str) -> str:
    """
    Given a user-supplied 'name', either:
      1) If it's a bare name (no directory, not absolute), prepend approvals_dir and create that folder.
      2) Otherwise, return 'name' as is (letting user define a custom path).

    Returns the 'base_path' (which might still include '.pdf' if user passed that).
    """
    if not os.path.isabs(name) and not os.path.dirname(name):
        os.makedirs(approvals_dir, exist_ok=True)
        return os.path.join(approvals_dir, name)
    else:
        return name

def _build_pdf_paths(base_path: str) -> (str, str):
    """
    If base_path ends with .pdf, remove it to avoid double-extensions like .pdf.approved.pdf.
    Then return two paths:
      - approved_path = <base>.approved.pdf
      - received_path = <base>.received.pdf
    """
    if base_path.lower().endswith(".pdf"):
        base_path = base_path[:-4]
    approved_path = base_path + ".approved.pdf"
    received_path = base_path + ".received.pdf"
    return approved_path, received_path