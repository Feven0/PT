import { useState, useEffect } from 'react';
import Api from '../Services/Services';
import "../styles/AudioRecorder/audiorecorder.css";
import { Button } from 'antd'; 
import { LoadingSpinner } from './index'
import useProcessingWebSocket from '../hooks/useProcessingWebSocket';

const AudioUpload = () => {
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [audioURL, setAudioURL] = useState<string | null>(null);
    const [loading, setLoad] = useState(false);
    const [jobProfileId, setJobProfileId] = useState<string>('1894');

    // Initialize WebSocket connection
    const { 
        isConnected, 
        startListening, 
        stopListening, 
        getJobStatus, 
        isJobInProgress, 
        isJobCompleted, 
        isJobFailed,
        getJobProgress 
    } = useProcessingWebSocket('http://localhost:9990');

    // Get job profile ID from localStorage
    // useEffect(() => {
    //     const storedJobId = localStorage.getItem('JobId');
    //     if (storedJobId) {
    //         setJobProfileId(storedJobId);
    //         console.log('🎯 Job Profile ID loaded:', storedJobId);
    //     }
    // }, []);

    // const [transcription, sendDataToParent] = useState<any>([])

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file && file.type === 'audio/mpeg') {
            setAudioFile(file);
            setAudioURL(URL.createObjectURL(file)); 
        } else {
            alert("Please upload an MP3 file.");
        }
    };

    const uploadAudio = async () => {
        setLoad(true)
        if (!audioFile) {
            alert("No audio file selected");
            return;
        }

        if (!jobProfileId) {
            alert("Job Profile ID not found. Please navigate to a job first.");
            setLoad(false);
            return;
        }

        // Start listening to processing updates for this job
        console.log('🚀 Starting to listen for job:', jobProfileId);
        startListening(jobProfileId);

        const formData = new FormData();
        formData.append('file', audioFile, audioFile.name);
        
        // Add the target data as JSON string (as expected by the endpoint)
        const targetData = {
            job_profile_id: jobProfileId,
            all_user_id: 1959,
            challenge_id: null
        };
        formData.append('target', JSON.stringify(targetData));
        formData.append('external', 'true');
        formData.append('run_stage', 'dev');

        try {
            const response = await Api.externalAudioUpload(formData);  
            console.log("Audio upload response:", response?.data);
            setLoad(false);

        } catch (error) {
            console.error('Error uploading audio:', error);
            setLoad(false);
        }
    };

    // Get current job status for display
    const currentJobStatus = getJobStatus(jobProfileId);
    const progress = getJobProgress(jobProfileId);

    return (
        <>
            <div className="audio-uploader-container" style={{backgroundColor: "#f46b31", width:'10px'}}>
                {/* WebSocket Status */}
                <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
                    <h4>🔌 WebSocket Status</h4>
                    <p>Connection: {isConnected ? '✅ Connected' : '❌ Disconnected'}</p>
                    <p>Job ID: {jobProfileId || 'Not set'}</p>
                    {currentJobStatus && (
                        <div>
                            <p>Status: {currentJobStatus.status}</p>
                            <p>Step: {currentJobStatus.step}</p>
                            <p>Message: {currentJobStatus.message}</p>
                            {progress > 0 && <p>Progress: {progress}%</p>}
                        </div>
                    )}
                </div>

                <div>
                    <input 
                        type="file"
                        accept="audio/mpeg"  // Only accept MP3 files
                        onChange={handleFileChange}
                    />
                </div>

                {audioURL && (
                    <audio controls>
                        <source src={audioURL} type="audio/mpeg" />  {/* Play the selected file */}
                    </audio>
                )}

                {audioFile && (
                    <div className="audio-controls">
                        <Button onClick={uploadAudio} className="submit-button">
                            Upload & Evaluate
                        </Button>
                        {loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                    </div>
                )}

                {/* Debug Controls */}
                <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e6f7ff', borderRadius: '5px' }}>
                    <h4>🔧 Debug Controls</h4>
                    <Button 
                        onClick={() => startListening(jobProfileId)} 
                        disabled={!jobProfileId || !isConnected}
                        style={{ marginRight: '10px' }}
                    >
                        Start Listening
                    </Button>
                    <Button 
                        onClick={() => stopListening(jobProfileId)} 
                        disabled={!jobProfileId || !isConnected}
                    >
                        Stop Listening
                    </Button>
                </div>
            </div>

        </>
    );
};

export default AudioUpload;
