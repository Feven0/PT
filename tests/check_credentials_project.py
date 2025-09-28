#!/usr/bin/env python3
"""
Check what project ID is in the current Google credentials
"""

import os
import sys
import json
sys.path.append('/home/rehmet/tenx_ipersona')

try:
    from api.utils.gdrive import google_api
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def check_credentials_project():
    """Check what project ID is in the current credentials"""
    try:
        # Initialize Google API
        api_client = google_api()
        print(f"✅ Google API client initialized")
        
        # Check the credentials file
        if hasattr(api_client, 'fauth') and os.path.exists(api_client.fauth):
            print(f"📁 Credentials file: {api_client.fauth}")
            
            with open(api_client.fauth, 'r') as f:
                creds_data = json.load(f)
            
            project_id = creds_data.get('project_id', 'NOT_FOUND')
            print(f"📋 Project ID in credentials: {project_id}")
            
            # Check other relevant fields
            client_email = creds_data.get('client_email', 'NOT_FOUND')
            print(f"📧 Client email: {client_email}")
            
            # Check if it's a service account
            cred_type = creds_data.get('type', 'NOT_FOUND')
            print(f"🔑 Credential type: {cred_type}")
            
            return project_id
        else:
            print("❌ Credentials file not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Google Credentials Project ID Checker")
    print("=" * 50)
    
    project_id = check_credentials_project()
    
    print("\n" + "=" * 50)
    if project_id:
        if project_id == "admin-projects-310515":
            print("✅ Credentials are for the correct project!")
        else:
            print(f"❌ Credentials are for project: {project_id}")
            print("💡 You need credentials for project: admin-projects-310515")
            print("💡 Check your SSM key 'googleservice/tenxsaas' in AWS Parameter Store")
    else:
        print("❌ Could not determine project ID from credentials")
