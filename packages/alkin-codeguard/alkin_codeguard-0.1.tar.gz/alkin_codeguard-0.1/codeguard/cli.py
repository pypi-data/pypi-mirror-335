import os
import subprocess

import click
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API URL and key from environment variables
SECRETLLM_API_URL = os.getenv(
    "SECRETLLM_API_URL", "https://nilai-a779.nillion.network/v1/chat/completions"
)
SECRET_LLM_API_KEY = os.getenv("SECRET_LLM_API_KEY")


def read_code_file(file_path):
    """Reads and returns the code from the given file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}")
        exit(1)


def run_solidity_analysis(file_path):
    """Runs security auditing only if the file is a Solidity (.sol) file."""
    click.echo("\n🔍 Running Solidity Security Audits...")
    slither_result = subprocess.run(
        ["slither", file_path], capture_output=True, text=True
    )
    return slither_result.stderr  # Capture stderr instead of stdout


def analyze_with_secretllm(code, is_solidity=False, analysis_results=None):
    """Sends code to SecretLLM for AI-powered analysis."""
    headers = {
        "Authorization": f"Bearer {SECRET_LLM_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Create appropriate prompt based on file type
    if is_solidity and analysis_results:
        prompt = f"""Review this Solidity code for security flaws. Focus on smart contract vulnerabilities, 
potential exploits, and best practices for secure Solidity development.

Solidity Analysis Tool Results:
{analysis_results}

Code to review:
{code}

Please provide a detailed security analysis covering:
1. Critical vulnerabilities
2. Medium/low severity issues
3. Gas optimization suggestions
4. Best practices recommendations"""
    else:
        prompt = f"""Review this code for security flaws and quality issues:

{code}

Please provide a detailed analysis covering:
1. Security vulnerabilities
2. Code quality issues
3. Performance concerns
4. Best practices recommendations"""

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a security-focused code review assistant",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": 2048,
        "stream": False,
        "nilrag": {},
    }

    try:
        response = requests.post(SECRETLLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "No response received.")
        )
    except Exception as e:
        return f"Error communicating with SecretLLM API: {str(e)}"


def format_output(content):
    """Formats the LLM output for better readability"""
    # Try to identify sections and add proper formatting
    formatted = content

    # Add section highlights
    for section in [
        "Critical vulnerabilities",
        "Medium",
        "Low",
        "Gas optimization",
        "Best practices",
        "Security vulnerabilities",
        "Code quality",
        "Performance concerns",
    ]:
        formatted = formatted.replace(f"{section}:", f"\n🚨 **{section}:**")

    # Highlight code snippets if they appear in markdown format
    if "```" in formatted:
        formatted = formatted.replace("```solidity", "```solidity\n")
        formatted = formatted.replace("```python", "```python\n")
        formatted = formatted.replace("```javascript", "```javascript\n")

    return formatted


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
def cli(file_path):
    """CLI tool to analyze and audit code for security issues."""
    click.echo(f"\n🔍 Analyzing {file_path}...\n")

    # Read the code file
    code = read_code_file(file_path)
    is_solidity = file_path.endswith(".sol")

    # For Solidity files, run Slither analysis first
    slither_result = None
    if is_solidity:
        click.echo("\n🛡️ **Running deep Solidity Security Scans**:")
        slither_result = run_solidity_analysis(file_path)

    secretllm_result = analyze_with_secretllm(code, is_solidity, slither_result)

    # Format and display the final results
    click.echo("\n📋 ** Code Review **:")
    click.echo(format_output(secretllm_result))
    click.echo("\n✅ ** Analysis Complete! **")


def main():
    cli()


if __name__ == "__main__":
    main()
