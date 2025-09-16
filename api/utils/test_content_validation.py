#!/usr/bin/env python3
"""
Test Script for AI-Powered Content Validation

This script demonstrates how to test the content validation logic
using sample transcription files instead of calling the Whisper API.

Usage:
    python test_content_validation.py
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append('/home/rehmet/tenx_ipersona')

from api.utils.audio_utils import AudioUtils

async def test_content_validation():
    """Test the content validation with different sample files"""
    
    audio_utils = AudioUtils()
    
    # Test cases with expected outcomes
    test_cases = [
        {
            "file": "valid_interview.txt",
            "expected": "PASS",
            "description": "Valid interview with Q&A pattern"
        },
        {
            "file": "answers_only.txt", 
            "expected": "FAIL",
            "description": "Only answers without questions"
        },
        {
            "file": "questions_only.txt",
            "expected": "FAIL", 
            "description": "Only questions without answers"
        },
        {
            "file": "casual_conversation.txt",
            "expected": "FAIL",
            "description": "Casual conversation, not interview"
        },
        {
            "file": "gibberish.txt",
            "expected": "FAIL",
            "description": "Gibberish/Latin text"
        },
        {
            "file": "too_short.txt",
            "expected": "FAIL",
            "description": "Content too short"
        }
    ]
    
    print("🧪 Starting Content Validation Tests")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"📁 File: {test_case['file']}")
        print(f"🎯 Expected: {test_case['expected']}")
        print("-" * 40)
        
        try:
            result = await audio_utils.process_upload_external_audio(
                filename=f"test_{test_case['file']}",
                content_type="audio/mpeg",
                audio_path="/tmp/test.mp3",
                job_profile_id=f"test_job_{i}",
                challenge_id=None,
                template_id=None,
                all_user_id="test_user_123",
                external=True,
                run_stage="dev",
                test_mode=True,
                test_sample_file=test_case['file']
            )
            
            if "Invalid interview content" in result:
                actual_result = "FAIL"
                print(f"❌ Result: FAIL - {result}")
            elif "Testing completed successfully" in result:
                actual_result = "PASS"
                print(f"✅ Result: PASS - {result}")
            else:
                actual_result = "UNKNOWN"
                print(f"⚠️ Result: UNKNOWN - {result}")
            
            # Check if result matches expectation
            if actual_result == test_case['expected']:
                print(f"✅ Test {i} PASSED - Result matches expectation")
            else:
                print(f"❌ Test {i} FAILED - Expected {test_case['expected']}, got {actual_result}")
                
        except Exception as e:
            print(f"💥 Test {i} ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_content_validation())