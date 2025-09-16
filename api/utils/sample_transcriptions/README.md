# Testing Mode Usage Examples

## How to Use Testing Mode

The testing mode allows you to test the AI-powered content validation without calling the Whisper API, saving costs while testing.

### Basic Usage

```python
from api.utils.audio_utils import AudioUtils

audio_utils = AudioUtils()

# Test with a valid interview sample
result = await audio_utils.process_upload_external_audio(
    filename="test_audio.mp3",
    content_type="audio/mpeg", 
    audio_path="/tmp/test.mp3",
    job_profile_id="test_job_123",
    challenge_id=None,
    template_id=None,
    all_user_id="test_user_123",
    external=True,
    run_stage="dev",
    test_mode=True,  # Enable testing mode
    test_sample_file="valid_interview.txt"  # Use this sample file
)
```

### Available Sample Files

1. **valid_interview.txt** - Complete interview with Q&A (should PASS)
2. **answers_only.txt** - Only candidate answers (should FAIL)
3. **questions_only.txt** - Only interviewer questions (should FAIL)
4. **casual_conversation.txt** - Random conversation (should FAIL)
5. **gibberish.txt** - Nonsensical text (should FAIL)
6. **too_short.txt** - Very short content (should FAIL)

### Testing Different Scenarios

```python
# Test valid interview
result = await audio_utils.process_upload_external_audio(
    # ... other params ...
    test_mode=True,
    test_sample_file="valid_interview.txt"
)

# Test answers without questions
result = await audio_utils.process_upload_external_audio(
    # ... other params ...
    test_mode=True,
    test_sample_file="answers_only.txt"
)

# Test casual conversation
result = await audio_utils.process_upload_external_audio(
    # ... other params ...
    test_mode=True,
    test_sample_file="casual_conversation.txt"
)
```

### Expected Results

- **PASS**: "Testing completed successfully for sample: [filename]"
- **FAIL**: "Invalid interview content: [specific reason]"

### Running the Test Script

```bash
cd /home/rehmet/tenx_ipersona
python api/utils/test_content_validation.py
```

This will run all test cases and show which ones pass/fail validation.
