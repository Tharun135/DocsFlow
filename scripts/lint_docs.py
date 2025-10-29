#!/usr/bin/env python3
"""
Documentation Linting Script for DocsFlow Pipeline

This script validates Markdown files for:
- Syntax errors
- Style consistency
- Link validation
- Heading structure
- Code block formatting
"""

import os
import sys
import re
import glob
from pathlib import Path
from typing import List, Dict, Any

class DocumentLinter:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.errors = []
        self.warnings = []
        
    def lint_all_files(self) -> bool:
        """Lint all Markdown files in the docs directory."""
        print("🔍 Starting documentation lint process...")
        
        md_files = list(self.docs_dir.glob("**/*.md"))
        if not md_files:
            print("❌ No Markdown files found in docs directory!")
            return False
            
        print(f"📄 Found {len(md_files)} Markdown files to validate")
        
        success = True
        for file_path in md_files:
            if not self.lint_file(file_path):
                success = False
                
        self.print_summary()
        return success
        
    def lint_file(self, file_path: Path) -> bool:
        """Lint a single Markdown file."""
        print(f"📝 Linting: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.add_error(file_path, f"Failed to read file: {e}")
            return False
            
        file_success = True
        
        # Run all validation checks
        if not self.check_heading_structure(file_path, content):
            file_success = False
        if not self.check_code_blocks(file_path, content):
            file_success = False
        if not self.check_links(file_path, content):
            file_success = False
        if not self.check_line_endings(file_path, content):
            file_success = False
        if not self.check_list_formatting(file_path, content):
            file_success = False
            
        return file_success
        
    def check_heading_structure(self, file_path: Path, content: str) -> bool:
        """Check heading hierarchy and structure."""
        lines = content.split('\n')
        headings = []
        success = True
        
        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('#').strip()
                headings.append((level, heading_text, i))
                
        # Check for single H1
        h1_count = sum(1 for level, _, _ in headings if level == 1)
        if h1_count != 1:
            self.add_error(file_path, f"Found {h1_count} H1 headings, should have exactly 1")
            success = False
            
        # Check heading hierarchy
        for i, (level, text, line_num) in enumerate(headings[1:], 1):
            prev_level = headings[i-1][0]
            if level > prev_level + 1:
                self.add_warning(file_path, f"Line {line_num}: Heading level jumps from H{prev_level} to H{level}")
                
        return success
        
    def check_code_blocks(self, file_path: Path, content: str) -> bool:
        """Check code block formatting."""
        lines = content.split('\n')
        success = True
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            if line.startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    language = line[3:].strip()
                    if not language and line == '```':
                        self.add_warning(file_path, f"Line {i}: Code block missing language specification")
                    in_code_block = True
                else:
                    # Ending a code block
                    in_code_block = False
                    
        if in_code_block:
            self.add_error(file_path, "Unclosed code block found")
            success = False
            
        return success
        
    def check_links(self, file_path: Path, content: str) -> bool:
        """Check link formatting and validity."""
        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        success = True
        
        for link_text, url in links:
            # Check for descriptive link text
            if link_text.lower() in ['click here', 'here', 'link', 'read more']:
                self.add_warning(file_path, f"Non-descriptive link text: '{link_text}'")
                
            # Check for relative file links
            if url.endswith('.md') and not url.startswith('http'):
                target_path = self.docs_dir / url
                if not target_path.exists():
                    self.add_error(file_path, f"Broken internal link: {url}")
                    success = False
                    
        return success
        
    def check_line_endings(self, file_path: Path, content: str) -> bool:
        """Check for proper line endings."""
        if not content.endswith('\n'):
            self.add_error(file_path, "File should end with a newline")
            return False
        return True
        
    def check_list_formatting(self, file_path: Path, content: str) -> bool:
        """Check list formatting consistency."""
        lines = content.split('\n')
        success = True
        
        for i, line in enumerate(lines, 1):
            # Check for consistent bullet points
            if re.match(r'^\s*\*\s', line):
                self.add_warning(file_path, f"Line {i}: Use hyphens (-) instead of asterisks (*) for bullets")
                
        return success
        
    def add_error(self, file_path: Path, message: str):
        """Add an error to the results."""
        self.errors.append(f"❌ {file_path}: {message}")
        
    def add_warning(self, file_path: Path, message: str):
        """Add a warning to the results."""
        self.warnings.append(f"⚠️  {file_path}: {message}")
        
    def print_summary(self):
        """Print a summary of the linting results."""
        print("\n" + "="*60)
        print("📊 LINTING SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ All documentation files passed linting!")
        elif not self.errors:
            print(f"✅ No errors found, but {len(self.warnings)} warnings to review")
        else:
            print(f"❌ Found {len(self.errors)} errors and {len(self.warnings)} warnings")
            
def main():
    """Main entry point for the linting script."""
    linter = DocumentLinter()
    success = linter.lint_all_files()
    
    if not success:
        print("\n💡 Tip: Fix the errors above and run the linter again")
        sys.exit(1)
    else:
        print("\n🎉 Documentation linting completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()