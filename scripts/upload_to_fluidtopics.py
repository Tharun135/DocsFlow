#!/usr/bin/env python3
"""
Fluid Topics Upload Script for DocsFlow Pipeline

This script handles the automated upload of documentation packages to Fluid Topics.
Features:
- Documentation packaging and compression
- API authentication and upload
- Error handling and retry logic
- Deployment status reporting
"""

import os
import sys
import zipfile
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib

class FluidTopicsUploader:
    def __init__(self):
        self.base_url = os.getenv("FLUID_URL", "").rstrip('/')
        self.username = os.getenv("FLUID_USER", "")
        self.password = os.getenv("FLUID_PASS", "")
        self.docs_dir = Path("docs")
        self.build_dir = Path("site")
        self.package_name = "docs_package.zip"
        
        # Validate configuration
        if not all([self.base_url, self.username, self.password]):
            raise ValueError("Missing required environment variables: FLUID_URL, FLUID_USER, FLUID_PASS")
    
    def create_package(self) -> bool:
        """Create a zip package of the documentation."""
        print("📦 Creating documentation package...")
        
        source_dir = self.build_dir if self.build_dir.exists() else self.docs_dir
        
        if not source_dir.exists():
            print(f"❌ Source directory {source_dir} does not exist!")
            return False
        
        try:
            with zipfile.ZipFile(self.package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                files_added = 0
                
                for root, dirs, files in os.walk(source_dir):
                    # Skip hidden directories and files
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.startswith('.'):
                            continue
                            
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(source_dir)
                        
                        zipf.write(file_path, arcname)
                        files_added += 1
                        
                print(f"✅ Package created successfully with {files_added} files")
                
                # Calculate package checksum
                checksum = self.calculate_checksum(self.package_name)
                print(f"📊 Package checksum: {checksum}")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to create package: {e}")
            return False
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of the package."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def upload_package(self) -> bool:
        """Upload the documentation package to Fluid Topics."""
        print("🚀 Uploading documentation package...")
        
        if not Path(self.package_name).exists():
            print(f"❌ Package file {self.package_name} not found!")
            return False
        
        upload_url = f"{self.base_url}/api/documents/upload"
        
        try:
            with open(self.package_name, 'rb') as f:
                files = {
                    'file': (self.package_name, f, 'application/zip')
                }
                
                data = {
                    'collection': 'docsflow-docs',
                    'version': self.get_version_info(),
                    'auto_publish': 'true'
                }
                
                print(f"📡 Uploading to: {upload_url}")
                
                response = requests.post(
                    upload_url,
                    auth=(self.username, self.password),
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Upload successful!")
                    print(f"📊 Upload ID: {result.get('upload_id', 'N/A')}")
                    print(f"📊 Status: {result.get('status', 'N/A')}")
                    
                    # Monitor processing status
                    if 'upload_id' in result:
                        return self.monitor_processing(result['upload_id'])
                    
                    return True
                    
                elif response.status_code == 401:
                    print("❌ Authentication failed - check credentials")
                    return False
                    
                elif response.status_code == 413:
                    print("❌ Package too large - consider splitting or compressing further")
                    return False
                    
                else:
                    print(f"❌ Upload failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except requests.exceptions.Timeout:
            print("❌ Upload timed out - package may be too large or network is slow")
            return False
            
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - check network and Fluid Topics URL")
            return False
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def get_version_info(self) -> str:
        """Get version information for the upload."""
        # Try to get git commit info
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                commit = result.stdout.strip()
                timestamp = int(time.time())
                return f"git-{commit}-{timestamp}"
        except:
            pass
        
        # Fallback to timestamp
        return f"build-{int(time.time())}"
    
    def monitor_processing(self, upload_id: str) -> bool:
        """Monitor the processing status of an upload."""
        print("⏳ Monitoring processing status...")
        
        status_url = f"{self.base_url}/api/documents/upload/{upload_id}/status"
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = requests.get(
                    status_url,
                    auth=(self.username, self.password),
                    timeout=30
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    status = status_data.get('status', 'unknown')
                    
                    print(f"📊 Processing status: {status}")
                    
                    if status == 'completed':
                        print("✅ Processing completed successfully!")
                        if 'publication_url' in status_data:
                            print(f"🌐 Published at: {status_data['publication_url']}")
                        return True
                        
                    elif status == 'failed':
                        print("❌ Processing failed!")
                        if 'error' in status_data:
                            print(f"Error: {status_data['error']}")
                        return False
                        
                    elif status in ['processing', 'queued', 'uploading']:
                        # Still processing, wait and retry
                        time.sleep(10)
                        attempt += 1
                        continue
                        
                    else:
                        print(f"⚠️  Unknown status: {status}")
                        time.sleep(10)
                        attempt += 1
                        continue
                        
                else:
                    print(f"⚠️  Status check failed: {response.status_code}")
                    time.sleep(10)
                    attempt += 1
                    continue
                    
            except Exception as e:
                print(f"⚠️  Status check error: {e}")
                time.sleep(10)
                attempt += 1
                continue
        
        print("⚠️  Processing status monitoring timed out")
        return False
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if Path(self.package_name).exists():
                os.remove(self.package_name)
                print(f"🧹 Cleaned up {self.package_name}")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def deploy(self) -> bool:
        """Main deployment function."""
        print("🚀 Starting DocsFlow deployment to Fluid Topics")
        print("="*60)
        
        try:
            # Step 1: Create package
            if not self.create_package():
                return False
            
            # Step 2: Upload package
            success = self.upload_package()
            
            # Step 3: Cleanup
            self.cleanup()
            
            if success:
                print("\n🎉 Deployment completed successfully!")
                print("📊 Documentation is now available in Fluid Topics")
            else:
                print("\n❌ Deployment failed!")
                
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️  Deployment interrupted by user")
            self.cleanup()
            return False
            
        except Exception as e:
            print(f"\n❌ Deployment failed with error: {e}")
            self.cleanup()
            return False

def main():
    """Main entry point for the upload script."""
    try:
        uploader = FluidTopicsUploader()
        success = uploader.deploy()
        
        if success:
            print("\n✅ All operations completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed - check the errors above")
            sys.exit(1)
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Required environment variables:")
        print("   FLUID_URL  - Your Fluid Topics portal URL")
        print("   FLUID_USER - Your Fluid Topics username")
        print("   FLUID_PASS - Your Fluid Topics password")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()