# Google API Python Client Examples

This directory contains example scripts demonstrating how to work with various Google APIs using the `google-api-python-client` library.

## Available Examples

### `docs_unicode_dates_example.py`

**Addresses**: [GitHub Issue #2547](https://github.com/googleapis/google-api-python-client/issues/2547) - "Google doc dates returned as unicode (e.g., \\ue907)"

**Purpose**: Demonstrates how to properly handle Unicode placeholder characters returned by the Google Docs API for smart chips (dates, people, places, etc.).

**Key Concepts**:
- Understanding that `\ue907` is intentional API behavior, not a bug
- Extracting actual date/chip information from `richLink` properties
- Working with Google Docs API document structure
- Best practices for handling non-text elements

**Usage**:
```bash
# Run the demonstration (no authentication required)
python examples/docs_unicode_dates_example.py

# To analyze an actual document, modify the script with your document ID
# and uncomment the analysis function call
```

**Requirements**:
- `google-auth`
- `google-api-python-client`
- Valid Google Docs API credentials (for real document analysis)

## Contributing Examples

When contributing new examples:
1. Focus on common use cases or frequently asked questions
2. Include comprehensive comments and documentation
3. Provide both demonstration code and real-world usage examples
4. Follow the existing code style and structure
5. Test thoroughly before submitting

## Authentication

Most examples require Google API credentials. See the [authentication documentation](https://cloud.google.com/docs/authentication) for setup instructions.