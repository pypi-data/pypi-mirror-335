# CodeGuard CLI - AI-Powered Code Security Auditor

CodeGuard CLI is a powerful command-line tool that analyzes code for security vulnerabilities, code quality issues, and best practices using AI-powered reviews. It supports both general programming languages and Solidity smart contract security auditing with tools like Slither.

## Features

- **AI-Powered Code Review**: Uses SecretLLM to provide security analysis and code quality feedback.
- **Solidity Security Analysis**: Runs Slither for Solidity smart contract security scanning.
- **Human-Readable Summaries**: Formats AI-generated output for better readability.
- **Environment Variable Support**: Uses `.env` file for API key configuration.

## Installation

### Prerequisites

Ensure you have Python 3.7+ installed on your system.

### Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/bhavyagor12/eth-global-trifecta.git codeguard-cli
   cd codeguard-cli
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   - Create a `.env` file in the root directory and add:
     ```ini
     SECRETLLM_API_URL=https://nilai-a779.nillion.network/v1/chat/completions
     SECRET_LLM_API_KEY=your_secretllm_api_key_here
     ```

## Usage

### Running a Security Audit

To analyze a file for security and quality issues:

```sh
python codeguard.py <file_path>
```

### Examples

#### General Code Review

```sh
python codeguard.py myscript.py
```

#### Solidity Security Analysis

```sh
python codeguard.py contract.sol
```

## How It Works

1. **Reads the Code**: Loads the provided file.
2. **Runs Solidity Analysis (if applicable)**: If the file is a Solidity contract (`.sol`), Slither is executed.
3. **AI-Powered Review**: Sends the code (and Solidity analysis results if available) to SecretLLM for a security-focused review.
4. **Formats and Outputs Results**: Displays human-readable insights on vulnerabilities, code quality, and best practices.

## Contributing

1. Fork the repository.
2. Create a new branch (`feature-xyz`).
3. Commit your changes.
4. Push to your branch and submit a PR.

## License

This project is licensed under the MIT License.

## Support

For issues or feature requests, please open an issue on GitHub.
