#!/usr/bin/env python3
"""
Minimal test to debug Google Cloud STT streaming issue
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_minimal_streaming():
    """Test minimal Google Cloud STT streaming"""
    print("🔍 Testing minimal Google Cloud STT streaming...")
    
    try:
        from api.utils.gdrive import google_api
        from google.cloud import speech_v1 as speech
        
        # Initialize with gdrive credentials
        gdrive_auth = google_api(verbose=0)
        client = speech.SpeechClient(credentials=gdrive_auth.creds)
        print("✅ Speech client created")
        
        # Create config
        config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            ),
            interim_results=True,
        )
        print("✅ Config created")
        
        # Create a simple generator with dummy audio data
        def simple_audio_generator():
            # Generate some dummy PCM16 audio data (silence)
            dummy_audio = b'\x00\x00' * 1000  # 1000 samples of silence
            yield speech.StreamingRecognizeRequest(audio_content=dummy_audio)
            # Send None to signal end
            yield None
        
        print("✅ Generator created")
        
        # Test the streaming_recognize call
        print("🔍 Testing streaming_recognize call...")
        try:
            responses = client.streaming_recognize(
                config=config,
                requests=simple_audio_generator()
            )
            print("✅ streaming_recognize call successful")
            
            # Try to iterate
            print("🔍 Testing iteration...")
            count = 0
            for response in responses:
                count += 1
                print(f"✅ Got response {count}: {response}")
                if count >= 3:  # Limit to avoid infinite loop
                    break
            print(f"✅ Iteration successful, got {count} responses")
            
        except Exception as e:
            print(f"❌ streaming_recognize failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_async_generator():
    """Test if the issue is with async generators"""
    print("\n🔍 Testing async generator approach...")
    
    try:
        from api.utils.gdrive import google_api
        from google.cloud import speech_v1 as speech
        
        gdrive_auth = google_api(verbose=0)
        client = speech.SpeechClient(credentials=gdrive_auth.creds)
        
        config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
            ),
            interim_results=True,
        )
        
        # Test with a list instead of generator
        requests = [
            speech.StreamingRecognizeRequest(audio_content=b'\x00\x00' * 1000)
        ]
        
        print("🔍 Testing with list instead of generator...")
        responses = client.streaming_recognize(config=config, requests=requests)
        
        count = 0
        for response in responses:
            count += 1
            print(f"✅ Got response {count}")
            if count >= 3:
                break
        
        print(f"✅ List approach successful, got {count} responses")
        return True
        
    except Exception as e:
        print(f"❌ Async generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Google Cloud STT Streaming Debug Test")
    print("=" * 50)
    
    # Test 1: Minimal streaming
    test1_ok = test_minimal_streaming()
    
    # Test 2: List approach
    test2_ok = test_async_generator()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"✅ Minimal streaming test: {'PASS' if test1_ok else 'FAIL'}")
    print(f"✅ List approach test: {'PASS' if test2_ok else 'FAIL'}")
    
    if test1_ok and test2_ok:
        print("\n🎉 Both tests passed! The issue might be in the async implementation.")
    else:
        print("\n❌ Tests failed. There's a fundamental issue with the API call.")

if __name__ == "__main__":
    main()

