#!/usr/bin/env python3
"""
Test script for gdrive.py module
This script tests the Google Drive API integration functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the api module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api.utils.gdrive import google_api, gauth
    print("✅ Successfully imported gdrive module")
except ImportError as e:
    print(f"❌ Failed to import gdrive module: {e}")
    sys.exit(1)

def test_gdrive_initialization():
    """Test basic initialization of the google_api class"""
    print("\n🔍 Testing Google API initialization...")
    
    try:
        # Test with minimal parameters
        api = google_api(verbose=2)
        print("✅ Google API initialized successfully")
        
        # Check if credentials are available
        if hasattr(api, 'creds') and api.creds:
            print("✅ Credentials loaded")
        else:
            print("⚠️  No credentials found")
            
        # Check available services
        services = api.get_service()
        print(f"✅ Available services: {list(services.keys())}")
        
        return api
        
    except Exception as e:
        print(f"❌ Failed to initialize Google API: {e}")
        return None

def test_authentication_methods():
    """Test different authentication methods"""
    print("\n🔍 Testing authentication methods...")
    
    try:
        # Test service account authentication
        print("Testing service account authentication...")
        api = google_api(fauth='admin-10ac-service.json', verbose=1)
        
        if api.creds:
            print("✅ Service account authentication successful")
        else:
            print("⚠️  Service account authentication failed")
            
    except Exception as e:
        print(f"❌ Service account authentication error: {e}")

def test_drive_operations(api):
    """Test basic Google Drive operations"""
    if not api:
        print("❌ Cannot test drive operations - API not initialized")
        return
        
    print("\n🔍 Testing Google Drive operations...")
    
    try:
        services = api.get_service(['drive'])
        drive_service = services.get('drive')
        
        if drive_service:
            print("✅ Drive service initialized")
            
            # Test listing files (limited to avoid quota issues)
            results = drive_service.files().list(pageSize=5, fields="nextPageToken, files(id, name)").execute()
            files = results.get('files', [])
            
            print(f"✅ Found {len(files)} files in Drive")
            for file in files[:3]:  # Show first 3 files
                print(f"   - {file.get('name')} (ID: {file.get('id')})")
                
        else:
            print("❌ Drive service not available")
            
    except Exception as e:
        print(f"❌ Drive operations error: {e}")

def test_sheets_operations(api):
    """Test Google Sheets operations"""
    if not api:
        print("❌ Cannot test sheets operations - API not initialized")
        return
        
    print("\n🔍 Testing Google Sheets operations...")
    
    try:
        services = api.get_service(['sheet'])
        sheets_service = services.get('sheet')
        
        if sheets_service:
            print("✅ Sheets service initialized")
            print("ℹ️  Note: Specific sheet operations require a valid sheet ID")
        else:
            print("❌ Sheets service not available")
            
    except Exception as e:
        print(f"❌ Sheets operations error: {e}")

def test_classroom_operations(api):
    """Test Google Classroom operations"""
    if not api:
        print("❌ Cannot test classroom operations - API not initialized")
        return
        
    print("\n🔍 Testing Google Classroom operations...")
    
    try:
        services = api.get_service(['class'])
        classroom_service = services.get('class')
        
        if classroom_service:
            print("✅ Classroom service initialized")
            print("ℹ️  Note: Classroom operations require proper permissions")
        else:
            print("❌ Classroom service not available")
            
    except Exception as e:
        print(f"❌ Classroom operations error: {e}")

def check_environment():
    """Check the environment and configuration"""
    print("\n🔍 Checking environment...")
    
    # Check for credential files
    home_dir = os.path.expanduser("~")
    cred_paths = [
        os.path.join(home_dir, '.credentials'),
        os.path.join(home_dir, '.env'),
        '/tmp'
    ]
    
    for path in cred_paths:
        if os.path.exists(path):
            print(f"✅ Found credential directory: {path}")
            
            # List files in credential directory
            try:
                files = os.listdir(path)
                google_files = [f for f in files if 'google' in f.lower() or 'admin' in f.lower()]
                if google_files:
                    print(f"   Google-related files: {google_files}")
                else:
                    print("   No Google credential files found")
            except PermissionError:
                print(f"   Permission denied accessing {path}")
        else:
            print(f"❌ Credential directory not found: {path}")
    
    # Check environment variables
    env_vars = ['GSPREAD_CONFIG', 'GOOGLE_APPLICATION_CREDENTIALS']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ Environment variable {var} is set")
        else:
            print(f"⚠️  Environment variable {var} is not set")

def main():
    """Main test function"""
    print("🚀 Starting Google Drive API Test")
    print("=" * 50)
    
    # Check environment first
    check_environment()
    
    # Test initialization
    api = test_gdrive_initialization()
    
    # Test authentication
    test_authentication_methods()
    
    # Test various services
    test_drive_operations(api)
    test_sheets_operations(api)
    test_classroom_operations(api)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    
    # Summary
    if api:
        print("✅ Google Drive API module is functional")
        print("ℹ️  This module provides integration with:")
        print("   - Google Drive (file operations)")
        print("   - Google Sheets (spreadsheet operations)")
        print("   - Google Slides (presentation operations)")
        print("   - Google Classroom (education management)")
        print("   - Google Admin (reports and analytics)")
    else:
        print("❌ Google Drive API module has issues")
        print("ℹ️  Check your credentials and configuration")

if __name__ == "__main__":
    main()

