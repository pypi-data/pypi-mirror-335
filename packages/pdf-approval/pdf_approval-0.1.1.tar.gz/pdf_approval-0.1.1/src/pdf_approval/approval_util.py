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

def set_auto_approve(enable: bool = True):
    """
    Enable or disable auto-approval of received files.
    If enabled, differences won't cause a failure;
    instead the approved file is replaced automatically.
    """
    global AUTO_APPROVE
    AUTO_APPROVE = enable


def verify_pdf(content_bytes: bytes, name: str, diff_tool: str = None):
    """
    Compare the given PDF content (bytes) to an approved PDF file on disk.

    :param content_bytes: Newly generated PDF bytes to verify
    :param name: Base name/path for the approval files.
                 e.g. "reports/monthly_report" ->
                 uses "reports/monthly_report.approved.pdf" & ".received.pdf"
    :param diff_tool: Override or set the diff tool for this verification (if not None)
    :raises AssertionError: if mismatch found and auto-approve is off
    """
    base_path = name[:-4] if name.lower().endswith(".pdf") else name
    approved_path = base_path + ".approved.pdf"
    received_path = base_path + ".received.pdf"

    os.makedirs(os.path.dirname(approved_path) or ".", exist_ok=True)

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


def approve_received(name: str):
    """
    Manually promote a '.received.pdf' file to '.approved.pdf'.
    """
    base_path = name[:-4] if name.lower().endswith(".pdf") else name
    approved_path = base_path + ".approved.pdf"
    received_path = base_path + ".received.pdf"

    if not os.path.exists(received_path):
        raise FileNotFoundError(f"No received file found at '{received_path}' to approve.")

    os.makedirs(os.path.dirname(approved_path) or ".", exist_ok=True)
    shutil.move(received_path, approved_path)
    print(f"Promoted '{received_path}' to '{approved_path}'")
