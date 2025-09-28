#!/usr/bin/env python3
"""
Test Google Cloud STT integration with gdrive.py authentication
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_gdrive_stt_integration():
    """Test the integration between gdrive.py and Google Cloud STT"""
    print("🚀 Testing Google Cloud STT + gdrive.py Integration")
    print("=" * 60)
    
    try:
        # Test 1: Import modules
        print("\n🔍 Test 1: Import modules...")
        from api.utils.gdrive import google_api
        from google.cloud import speech_v1 as speech
        print("✅ All modules imported successfully")
        
        # Test 2: Initialize gdrive authentication
        print("\n🔍 Test 2: Initialize gdrive authentication...")
        gdrive_auth = google_api(verbose=1)
        print("✅ gdrive.py authentication initialized")
        
        # Test 3: Check scopes
        print("\n🔍 Test 3: Check authentication scopes...")
        scopes = gdrive_auth.SCOPES
        cloud_platform_scope = "https://www.googleapis.com/auth/cloud-platform"
        
        if cloud_platform_scope in scopes:
            print("✅ Cloud Platform scope found in gdrive.py")
        else:
            print("❌ Cloud Platform scope missing")
            return False
        
        # Test 4: Create Speech client with gdrive credentials
        print("\n🔍 Test 4: Create Speech client with gdrive credentials...")
        try:
            speech_client = speech.SpeechClient(credentials=gdrive_auth.creds)
            print("✅ Speech client created with gdrive credentials")
        except Exception as e:
            print(f"❌ Failed to create Speech client: {e}")
            return False
        
        # Test 5: Test streaming configuration
        print("\n🔍 Test 5: Test streaming configuration...")
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )
        print("✅ Streaming configuration created successfully")
        
        # Test 6: Test the GoogleStreamingSession class
        print("\n🔍 Test 6: Test GoogleStreamingSession class...")
        try:
            # Import the socket module to test the class
            sys.path.insert(0, str(Path(__file__).parent.parent / "api" / "pages" / "ipersona" / "socket"))
            from ipersona_socket import GoogleStreamingSession
            
            # Create a test session
            session = GoogleStreamingSession(sid="test_session")
            print("✅ GoogleStreamingSession created successfully")
            print(f"   - Language: {session.language_code}")
            print(f"   - Sample Rate: {session.sample_rate_hz}")
            print(f"   - Interim Results: {session.enable_interim_results}")
            
        except Exception as e:
            print(f"❌ Failed to create GoogleStreamingSession: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Google Cloud STT integration is ready!")
        print("\n📋 Integration Summary:")
        print("✅ gdrive.py authentication working")
        print("✅ Cloud Platform scope added")
        print("✅ Speech client using gdrive credentials")
        print("✅ GoogleStreamingSession class functional")
        print("\n💡 You can now use Google Cloud STT streaming in your application!")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_socket_integration():
    """Test the socket integration"""
    print("\n🔍 Testing socket integration...")
    
    try:
        # Test if the socket module can be imported
        sys.path.insert(0, str(Path(__file__).parent.parent / "api" / "pages" / "ipersona" / "socket"))
        from ipersona_socket import audio_transcribe_google
        print("✅ Socket event handler imported successfully")
        
        # Test if the GoogleStreamingSession is accessible
        from ipersona_socket import GoogleStreamingSession
        print("✅ GoogleStreamingSession accessible from socket module")
        
        return True
        
    except Exception as e:
        print(f"❌ Socket integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Google Cloud STT + gdrive.py Integration Test Suite")
    print("=" * 70)
    
    # Run integration tests
    integration_ok = test_gdrive_stt_integration()
    
    if integration_ok:
        # Test socket integration
        socket_ok = test_socket_integration()
        
        print("\n" + "=" * 70)
        print("📊 Final Results:")
        print(f"✅ Core Integration: {'PASS' if integration_ok else 'FAIL'}")
        print(f"✅ Socket Integration: {'PASS' if socket_ok else 'FAIL'}")
        
        if integration_ok and socket_ok:
            print("\n🎉 SUCCESS: Google Cloud STT is fully integrated and ready to use!")
            print("\n🚀 Next Steps:")
            print("   1. Start your socket server")
            print("   2. Connect from frontend")
            print("   3. Send 'audio transcribe google' events")
            print("   4. Enjoy real-time speech-to-text!")
        else:
            print("\n⚠️  Some issues detected. Check the errors above.")
    else:
        print("\n❌ Core integration failed. Please check the errors above.")

if __name__ == "__main__":
    main()

