# CTScan Code Scanner

Securin ASPM Code Scanner is a Python-based tool designed to download and execute a CLI from AWS S3, decrypt necessary credentials, and perform code scanning operations. This tool is intended to be used as a command-line utility.

## Features

- Download CLI executable from AWS S3
- Decrypt AWS credentials using AES encryption
- Perform code scanning with various configurable options
- Output results in different formats

## Installation

To install the package, use the following command:

```bash
pip install securin-aspm
```

## Usage

To use the Securin ASPM Code Scanner, run the following command:

```bash
python -m securin-aspm --api_key YOUR_API_KEY [options]
```

### Command-Line Arguments

- `--api_key` (required): API key for authentication
- `--app_id`: Application ID
- `--app_name`: Application name
- `--branch_name`: Branch name (default: 'default')
- `--enable_color`: Enable color in report
- `--format`: Output format
- `--is_console_report`: Enable console report (default: True)
- `--is_debug`: Enable debug logs
- `--output_file`: Output file path
- `--scan_types`: Types of scans to be triggered
- `--severity`: Severity level
- `--skip_build_fail`: Skip build fail
- `--source_dir`: Source directory (default: current working directory)
- `--version`: CLI version to use
- `--hostname`: API endpoint hostname (default: `custom-endpoint.yourdomain.io`)

## Example

```bash
python -m securin-aspm --api_key YOUR_API_KEY --app_name MyApp --branch_name main --format json --output_file results.json
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For any inquiries, please contact the project maintainers.
aspm@securin.io
