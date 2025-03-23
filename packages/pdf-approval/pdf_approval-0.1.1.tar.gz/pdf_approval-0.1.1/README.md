# pdf-approval

A lightweight Python library for **approval (snapshot) testing** of PDF outputs by comparing raw bytes.  

## Features

- **Binary Compare**: Verifies exact byte-for-byte match between newly generated PDFs and their approved versions.  
- **Easy Baseline Management**: Stores `.approved.pdf` in source control, creates a `.received.pdf` on mismatch.  
- **Auto-Approve**: Allows updating baselines automatically if desired.  
- **Cross-Platform**: Works on Windows, macOS, and Linux.  
- **Test Runner Agnostic**: Raises `AssertionError` on mismatch (works with Pytest, Unittest, or any runner).

## Installation

pip install pdf-approval

## Quick Start

1. **Generate or obtain** your PDF in bytes (e.g., from a report generator).  
2. **Call** `verify_pdf(pdf_bytes, "my_report")`. This looks for `my_report.approved.pdf` and compares it to the new PDF bytes.  
3. If no `.approved.pdf` is found or they differ, the library writes a `.received.pdf` file and raises an error:  
   - Inspect the new PDF to ensure it’s correct.  
   - Approve by renaming it or calling `approve_received("my_report")`.

### Example
```python
from pdf_approval.approval_util import verify_pdf, approve_received

def test_generate_monthly_report():
    # Suppose we create some PDF data
    pdf_data = create_monthly_report()  # returns raw PDF bytes
    
    # Compare to an approved file named 'monthly_report.approved.pdf'
    verify_pdf(pdf_data, "monthly_report")

    # If mismatch => test fails, a 'monthly_report.received.pdf' is produced.
    # If it doesn't exist => also fails, instructing you to approve.
    # To approve changes (after checking them):
    # approve_received("monthly_report")
```

## Auto-Approve

If you want the library to automatically update the `.approved.pdf` file when a mismatch is detected (bypassing the test failure), set an environment variable or use the library function:

export APPROVAL_AUTO_APPROVE=1
pytest

Or in code:
```python
from pdf_approval.approval_util import set_auto_approve
set_auto_approve(True)
```
Use with caution – always inspect changes to ensure they’re valid.

## Best Practices

1. **Commit Approved Files**: Check `*.approved.pdf` into version control.  
2. **Ignore Received Files**: Add `*.received.pdf` to your `.gitignore`.  
3. **Review Mismatches**: Don’t just blindly approve – open a diff or PDF viewer to confirm changes are valid.  
4. **Stable PDF Generation**: Remove timestamps, IDs, or other variable data from your PDF if possible to avoid spurious diffs.  
5. **Auto-Approve in CI?** Usually not recommended; you want test failures for unexpected changes.

## Contributing

1. Fork or clone this repository.  
2. Make changes in a dedicated branch.  
3. Add or update tests as needed.  
4. Submit a pull request.  

All contributions, big or small, are welcome!

## License

[MIT License](LICENSE)
