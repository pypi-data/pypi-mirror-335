"""inprompt: CLI to output files as Markdown code blocks for LLM prompts.

Example usage:
    inprompt path/to/file.py '**/*.py' | pbcopy
"""

import glob

from absl import app
from loguru import logger


def print_usage() -> None:
    """Log usage info."""
    logger.info("Usage: inprompt <files or patterns> [<files or patterns> ...]")
    logger.info("Example: inprompt my_script.py '**/*.py' | pbcopy")


def match_file_patterns(patterns: list[str]) -> list[str]:
    """Glob patterns and return sorted, unique matches.

    Args:
        patterns (list[str]): Glob patterns.

    Returns:
        list[str]: De-duplicated, sorted filenames.
    """
    filenames = []
    for pattern in patterns:
        matched_files = sorted(glob.glob(pattern))
        if not matched_files:
            logger.warning("No files matched pattern: {}", pattern)
        filenames.extend(matched_files)
    return list(dict.fromkeys(filenames))


def read_and_format_source_code(filename: str) -> str:
    """Return file contents as a Markdown code fence.

    Args:
        filename (str): Path to the file.

    Returns:
        str: Markdown code fence string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return f"{filename}\n```\n{content}\n```"
    except FileNotFoundError:
        logger.error("File not found: {}", filename)
        raise


def main(argv: list[str]) -> int:
    """CLI entry point.

    Args:
        argv (list[str]): Command-line arguments.

    Returns:
        int: Exit code.
    """
    if len(argv) < 2:
        logger.error("No files or file patterns specified.")
        print_usage()
        return 2

    file_patterns = argv[1:]
    filenames = match_file_patterns(file_patterns)

    if not filenames:
        logger.error("No matching files found.")
        return 3

    formatted_contents = [read_and_format_source_code(fname) for fname in filenames]
    print("\n\n".join(formatted_contents))

    logger.info("Formatted and outputted {} files.", len(filenames))
    return 0


def run():
    """Console script entry point."""
    app.run(main)


if __name__ == "__main__":
    run()
