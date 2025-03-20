#!/usr/bin/env python3
"""
Juno Code Linter

This tool checks Juno code for potential issues and style violations.
"""

import argparse
import os
import sys
import re

def lint_file(file_path, strict=False):
    """
    Lint a Juno file.
    
    Args:
        file_path (str): Path to the Juno file
        strict (bool): If True, enforce stricter rules
        
    Returns:
        list: List of issues found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lint the content
        issues = lint_content(content, file_path, strict)
        
        # Print the issues
        if issues:
            print(f"Found {len(issues)} issue(s) in {file_path}:")
            for issue in issues:
                print(f"  Line {issue['line']}: {issue['message']}")
        else:
            print(f"No issues found in {file_path}")
        
        return issues
    
    except Exception as e:
        print(f"Error linting {file_path}: {e}", file=sys.stderr)
        return [{'line': 0, 'message': f"Error linting file: {e}"}]

def lint_content(content, file_path, strict=False):
    """
    Lint Juno code.
    
    Args:
        content (str): The Juno code to lint
        file_path (str): Path to the file (for reporting)
        strict (bool): If True, enforce stricter rules
        
    Returns:
        list: List of issues found
    """
    issues = []
    lines = content.split('\n')
    
    # Check for basic issues
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check for trailing whitespace
        if line.rstrip() != line:
            issues.append({
                'line': line_num,
                'message': "Trailing whitespace"
            })
        
        # Check for tabs
        if '\t' in line:
            issues.append({
                'line': line_num,
                'message': "Tab character found (use spaces instead)"
            })
        
        # Check for lines that are too long
        if len(line) > 100:
            issues.append({
                'line': line_num,
                'message': f"Line too long ({len(line)} > 100 characters)"
            })
        
        # Check for missing semicolons
        if line.strip() and not line.strip().startswith('//') and not line.strip().endswith('{') and not line.strip().endswith('}') and not line.strip().endswith(';'):
            issues.append({
                'line': line_num,
                'message': "Missing semicolon at end of line"
            })
        
        # Check for inconsistent spacing around operators
        for op in ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=']:
            if op in line and (op + ' ' not in line and ' ' + op not in line):
                issues.append({
                    'line': line_num,
                    'message': f"Inconsistent spacing around operator '{op}'"
                })
    
    # Check for more complex issues
    if strict:
        # Check for unused variables (simplified)
        var_decl_pattern = re.compile(r'(let|var)\s+(\w+)')
        var_use_pattern = re.compile(r'\b(\w+)\b')
        
        declared_vars = []
        for i, line in enumerate(lines):
            # Find variable declarations
            for match in var_decl_pattern.finditer(line):
                var_name = match.group(2)
                declared_vars.append({
                    'name': var_name,
                    'line': i + 1,
                    'used': False
                })
        
        # Check for variable usage
        for i, line in enumerate(lines):
            for var in declared_vars:
                # Skip the line where the variable is declared
                if i + 1 == var['line']:
                    continue
                
                # Check if the variable is used
                for match in var_use_pattern.finditer(line):
                    if match.group(1) == var['name']:
                        var['used'] = True
                        break
        
        # Report unused variables
        for var in declared_vars:
            if not var['used']:
                issues.append({
                    'line': var['line'],
                    'message': f"Unused variable '{var['name']}'"
                })
    
    return issues

def main():
    """Main entry point for the linter."""
    parser = argparse.ArgumentParser(description="Juno Code Linter")
    parser.add_argument('files', nargs='+', help='Files to lint')
    parser.add_argument('--strict', action='store_true', help="Enforce stricter rules")
    
    args = parser.parse_args()
    
    issue_count = 0
    for file_path in args.files:
        if os.path.isfile(file_path) and file_path.endswith('.juno'):
            issues = lint_file(file_path, args.strict)
            issue_count += len(issues)
        else:
            print(f"Skipping {file_path} (not a .juno file)")
    
    print(f"Found {issue_count} issue(s) in total")
    
    # Return non-zero exit code if issues were found
    sys.exit(1 if issue_count > 0 else 0)

if __name__ == "__main__":
    main()