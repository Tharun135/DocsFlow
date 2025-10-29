#!/usr/bin/env python3
"""
YAML Validation Script for DocsFlow Pipeline

This script validates YAML files for:
- Syntax correctness
- Schema validation
- Required fields presence
- Data type validation
"""

import os
import sys
import yaml
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional

class YAMLValidator:
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.errors = []
        self.warnings = []
        self.required_configs = {
            'mkdocs.yml': self.validate_mkdocs_config,
            '.github/workflows/*.yml': self.validate_github_workflow,
            'docker-compose.yml': self.validate_docker_compose
        }
        
    def validate_all_files(self) -> bool:
        """Validate all YAML files in the project."""
        print("🔍 Starting YAML validation process...")
        
        yaml_files = self.find_yaml_files()
        if not yaml_files:
            print("❌ No YAML files found!")
            return False
            
        print(f"📄 Found {len(yaml_files)} YAML files to validate")
        
        success = True
        for file_path in yaml_files:
            if not self.validate_file(file_path):
                success = False
                
        self.print_summary()
        return success
        
    def find_yaml_files(self) -> List[Path]:
        """Find all YAML files in the project."""
        patterns = ['**/*.yml', '**/*.yaml']
        yaml_files = []
        
        for pattern in patterns:
            yaml_files.extend(self.config_dir.glob(pattern))
            
        return list(set(yaml_files))  # Remove duplicates
        
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single YAML file."""
        print(f"📝 Validating: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.add_error(file_path, f"Failed to read file: {e}")
            return False
            
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            self.add_error(file_path, f"Invalid YAML syntax: {e}")
            return False
            
        if data is None:
            self.add_warning(file_path, "Empty YAML file")
            return True
            
        # Run specific validation based on file type
        return self.run_specific_validation(file_path, data)
        
    def run_specific_validation(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Run file-type specific validation."""
        file_name = file_path.name
        success = True
        
        if file_name == 'mkdocs.yml':
            success = self.validate_mkdocs_config(file_path, data)
        elif file_path.match('.github/workflows/*.yml'):
            success = self.validate_github_workflow(file_path, data)
        elif file_name == 'docker-compose.yml':
            success = self.validate_docker_compose(file_path, data)
        else:
            # Generic validation
            success = self.validate_generic_yaml(file_path, data)
            
        return success
        
    def validate_mkdocs_config(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Validate MkDocs configuration."""
        success = True
        required_fields = ['site_name', 'docs_dir']
        
        for field in required_fields:
            if field not in data:
                self.add_error(file_path, f"Missing required field: {field}")
                success = False
                
        # Validate site_name
        if 'site_name' in data:
            if not isinstance(data['site_name'], str) or not data['site_name'].strip():
                self.add_error(file_path, "site_name must be a non-empty string")
                success = False
                
        # Validate docs_dir
        if 'docs_dir' in data:
            docs_path = self.config_dir / data['docs_dir']
            if not docs_path.exists():
                self.add_error(file_path, f"docs_dir '{data['docs_dir']}' does not exist")
                success = False
                
        # Check for navigation structure
        if 'nav' in data:
            if not self.validate_navigation(file_path, data['nav']):
                success = False
                
        # Validate theme
        if 'theme' in data:
            if isinstance(data['theme'], dict):
                if 'name' not in data['theme']:
                    self.add_warning(file_path, "Theme configuration missing 'name' field")
            elif not isinstance(data['theme'], str):
                self.add_error(file_path, "Theme must be a string or dictionary")
                success = False
                
        return success
        
    def validate_navigation(self, file_path: Path, nav: List[Any]) -> bool:
        """Validate MkDocs navigation structure."""
        success = True
        
        for item in nav:
            if isinstance(item, dict):
                for title, path in item.items():
                    if isinstance(path, str) and path.endswith('.md'):
                        # Check if the referenced file exists
                        doc_path = self.config_dir / 'docs' / path
                        if not doc_path.exists():
                            self.add_error(file_path, f"Navigation references non-existent file: {path}")
                            success = False
                            
        return success
        
    def validate_github_workflow(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Validate GitHub Actions workflow."""
        success = True
        required_fields = ['name', 'on', 'jobs']
        
        for field in required_fields:
            if field not in data:
                self.add_error(file_path, f"Missing required field: {field}")
                success = False
                
        # Validate jobs structure
        if 'jobs' in data:
            if not isinstance(data['jobs'], dict):
                self.add_error(file_path, "jobs must be a dictionary")
                success = False
            else:
                for job_name, job_config in data['jobs'].items():
                    if not isinstance(job_config, dict):
                        self.add_error(file_path, f"Job '{job_name}' must be a dictionary")
                        success = False
                        continue
                        
                    if 'runs-on' not in job_config:
                        self.add_error(file_path, f"Job '{job_name}' missing 'runs-on' field")
                        success = False
                        
                    if 'steps' not in job_config:
                        self.add_error(file_path, f"Job '{job_name}' missing 'steps' field")
                        success = False
                        
        return success
        
    def validate_docker_compose(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Validate Docker Compose configuration."""
        success = True
        
        # Check for version (optional but recommended)
        if 'version' not in data:
            self.add_warning(file_path, "Consider specifying a version field")
            
        # Check for services
        if 'services' not in data:
            self.add_error(file_path, "Missing required 'services' field")
            return False
            
        if not isinstance(data['services'], dict):
            self.add_error(file_path, "services must be a dictionary")
            return False
            
        # Validate each service
        for service_name, service_config in data['services'].items():
            if not isinstance(service_config, dict):
                self.add_error(file_path, f"Service '{service_name}' must be a dictionary")
                success = False
                continue
                
            # Check for image or build
            if 'image' not in service_config and 'build' not in service_config:
                self.add_error(file_path, f"Service '{service_name}' must have either 'image' or 'build'")
                success = False
                
        return success
        
    def validate_generic_yaml(self, file_path: Path, data: Dict[Any, Any]) -> bool:
        """Generic YAML validation."""
        # For now, just check that it's valid YAML (already done)
        # Could add more generic checks here
        return True
        
    def add_error(self, file_path: Path, message: str):
        """Add an error to the results."""
        self.errors.append(f"❌ {file_path}: {message}")
        
    def add_warning(self, file_path: Path, message: str):
        """Add a warning to the results."""
        self.warnings.append(f"⚠️  {file_path}: {message}")
        
    def print_summary(self):
        """Print a summary of the validation results."""
        print("\n" + "="*60)
        print("📊 YAML VALIDATION SUMMARY")
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
            print("✅ All YAML files are valid!")
        elif not self.errors:
            print(f"✅ No errors found, but {len(self.warnings)} warnings to review")
        else:
            print(f"❌ Found {len(self.errors)} errors and {len(self.warnings)} warnings")

def main():
    """Main entry point for the validation script."""
    validator = YAMLValidator()
    success = validator.validate_all_files()
    
    if not success:
        print("\n💡 Tip: Fix the errors above and run the validator again")
        sys.exit(1)
    else:
        print("\n🎉 YAML validation completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()