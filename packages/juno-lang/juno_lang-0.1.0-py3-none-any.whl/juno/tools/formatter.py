#!/usr/bin/env python3
"""
Juno Code Formatter

This tool formats Juno code according to the Juno style guide.
"""

import argparse
import os
import sys

def format_file(file_path, dry_run=False):
    """
    Format a Juno file.
    
    Args:
        file_path (str): Path to the Juno file
        dry_run (bool): If True, don't modify the file, just print the formatted code
        
    Returns:
        bool: True if the file was formatted, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Format the content
        formatted_content = format_content(content)
        
        if dry_run:
            print(formatted_content)
            return True
        
        # Check if the content changed
        if content == formatted_content:
            print(f"No changes needed for {file_path}")
            return False
        
        # Write the formatted content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        print(f"Formatted {file_path}")
        return True
    
    except Exception as e:
        print(f"Error formatting {file_path}: {e}", file=sys.stderr)
        return False

def format_content(content):
    """
    Format Juno code.
    
    Args:
        content (str): The Juno code to format
        
    Returns:
        str: The formatted Juno code
    """
    # This is a simple implementation that just adds consistent spacing
    # A real formatter would parse the code and apply more sophisticated formatting
    
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip()
        
        # Add space after commas
        line = line.replace(',', ', ')
        
        # Add space around operators
        for op in ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=']:
            line = line.replace(op, f' {op} ')
        
        # Fix multiple spaces
        while '  ' in line:
            line = line.replace('  ', ' ')
        
        # Fix spaces around parentheses and braces
        for pair in [('( ', '('), (' )', ')'), ('{ ', '{'), (' }', '}')]:
            line = line.replace(pair[0], pair[1])
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def main():
    """Main entry point for the formatter."""
    parser = argparse.ArgumentParser(description="Juno Code Formatter")
    parser.add_argument('files', nargs='+', help='Files to format')
    parser.add_argument('--dry-run', action='store_true', help="Don't modify files, just print the formatted code")
    
    args = parser.parse_args()
    
    formatted_count = 0
    for file_path in args.files:
        if os.path.isfile(file_path) and file_path.endswith('.juno'):
            if format_file(file_path, args.dry_run):
                formatted_count += 1
        else:
            print(f"Skipping {file_path} (not a .juno file)")
    
    print(f"Formatted {formatted_count} file(s)")

if __name__ == "__main__":
    main()