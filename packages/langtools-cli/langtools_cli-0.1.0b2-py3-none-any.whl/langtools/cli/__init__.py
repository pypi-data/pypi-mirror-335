"""
CLI Package
----------
Command-line interface implementation for LangTools CLI.

Available Commands:
- package upload: Pack and upload Python files to feeds
- job submit: Submit Python jobs to Ray clusters
"""
name = 'cli'
from langtools.cli.cli import main