#!/usr/bin/env python3
"""
Test Google Cloud Speech-to-Text streaming with existing gdrive.py authentication
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api.utils.gdrive import google_api
    print("✅ Successfully imported gdrive module")
except ImportError as e:
    print(f"❌ Failed to import gdrive module: {e}")
    sys.exit(1)

def test_speech_to_text_setup():
    """Test if we can set up Speech-to-Text with existing credentials"""
    print("\n🔍 Testing Google Cloud Speech-to-Text setup...")
    
    try:
        # Try to import the Speech-to-Text client
        from google.cloud import speech
        print("✅ Google Cloud Speech-to-Text client available")
        
        # Test with existing authentication
        api = google_api(verbose=1)
        
        # Check if we can create a Speech client with existing credentials
        try:
            speech_client = speech.SpeechClient(credentials=api.creds)
            print("✅ Speech-to-Text client created successfully")
            
            # Test basic configuration
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            )
            print("✅ Speech recognition config created")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Speech client: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Google Cloud Speech-to-Text not installed: {e}")
        print("💡 Install with: pip install google-cloud-speech")
        return False

def test_streaming_config():
    """Test streaming recognition configuration"""
    print("\n🔍 Testing streaming configuration...")
    
    try:
        from google.cloud import speech
        
        # Create streaming config as per documentation
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )
        
        print("✅ Streaming recognition config created")
        print(f"   - Encoding: LINEAR16")
        print(f"   - Sample Rate: 16000 Hz")
        print(f"   - Language: en-US")
        print(f"   - Interim Results: True")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create streaming config: {e}")
        return False

def check_credentials():
    """Check if credentials have the right scopes for Speech-to-Text"""
    print("\n🔍 Checking credential scopes...")
    
    try:
        api = google_api(verbose=1)
        
        # Check current scopes
        current_scopes = api.SCOPES
        print(f"Current scopes: {len(current_scopes)}")
        
        # Check if cloud-platform scope is present
        cloud_platform_scope = "https://www.googleapis.com/auth/cloud-platform"
        if cloud_platform_scope in current_scopes:
            print("✅ Cloud Platform scope found")
        else:
            print("⚠️  Cloud Platform scope not found")
            print("💡 Add this scope for Speech-to-Text access:")
            print(f"   {cloud_platform_scope}")
        
        return cloud_platform_scope in current_scopes
        
    except Exception as e:
        print(f"❌ Error checking scopes: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Google Cloud Speech-to-Text Integration")
    print("=" * 60)
    
    # Test basic setup
    speech_available = test_speech_to_text_setup()
    
    if speech_available:
        # Test streaming configuration
        streaming_ok = test_streaming_config()
        
        # Check credentials
        scopes_ok = check_credentials()
        
        print("\n" + "=" * 60)
        print("📋 Summary:")
        print(f"✅ Speech-to-Text Client: {'Available' if speech_available else 'Not Available'}")
        print(f"✅ Streaming Config: {'OK' if streaming_ok else 'Failed'}")
        print(f"✅ Credentials Scopes: {'OK' if scopes_ok else 'Needs Update'}")
        
        if speech_available and streaming_ok and scopes_ok:
            print("\n🎉 Ready for Google Cloud Speech-to-Text streaming!")
            print("💡 You can now implement streaming STT using the existing authentication")
        else:
            print("\n⚠️  Some setup required:")
            if not speech_available:
                print("   - Install: pip install google-cloud-speech")
            if not scopes_ok:
                print("   - Add cloud-platform scope to gdrive.py")
    else:
        print("\n❌ Speech-to-Text not available")
        print("💡 Install with: pip install google-cloud-speech")

if __name__ == "__main__":
    main()

