# stop-azs

## Overview
This repository documents key allegations and participants in the alleged diversion of escrow funds from the City National Bank trust account controlled by Justin E. Zeig.

## Documentation

### Core Analysis
- **[analysis.md](analysis.md)** - Detailed background on trust account activity, shell entities, case metadata, red flags, forensic ledger exhibit (as of August 24, 2025), and synthesis of pass-through behavior

### Case Documentation
- **[docs/involved_parties.md](docs/involved_parties.md)** - Key actors, scheme highlights, law-enforcement contacts, and recommended next steps
- **[docs/external_resources.md](docs/external_resources.md)** - Index of AI-assisted narratives and drafting notes staged outside the repository
- **[docs/request_flow.md](docs/request_flow.md)** - End-to-end path for client submissions from API endpoint through validation to database

## Repository Structure

```
stop-azs/
├── sar_parser/          # SAR XML validation and parsing logic
├── tests/               # Automated test suite
├── tools/               # Utility scripts
├── docs/                # Additional documentation
└── windows-nas-bootstrap/  # Windows automation bundle
```

## Development

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/stopazus/stop-azs.git
cd stop-azs

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install pytest
```

### Running Tests

The project includes automated unit tests for SAR XML validation:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with quiet mode
pytest -q
```

Tests run automatically via GitHub Actions on every push and pull request.

### Test Coverage
- SAR XML validation (valid documents)
- Missing required sections detection
- Placeholder amount detection
- File I/O operations

## Windows NAS Bootstrap

The `windows-nas-bootstrap/` directory contains a Windows automation bundle that:
- Installs essential applications via winget (Python 3.12, Git, rclone, VS Code, 7-Zip, VLC, WinSCP, PuTTY)
- Configures Google Drive sync
- Performs optional network speed tests

See `windows-nas-bootstrap/README.md` for usage instructions.

## Security

See [SECURITY.md](SECURITY.md) for security policies and reporting vulnerabilities.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Ensure all tests pass before submitting:
```bash
pytest -v
```

## License

[Add your license information here]

## Contact

For questions or concerns about this case, refer to the contact information in [docs/involved_parties.md](docs/involved_parties.md).
