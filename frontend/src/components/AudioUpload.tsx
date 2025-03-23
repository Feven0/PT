import { useState } from 'react';
import Api from '../Services/Services';
import "../styles/AudioRecorder/audiorecorder.css";
import { Button } from 'antd'; 
import { LoadingSpinner } from './index'

const AudioUpload = () => {
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [audioURL, setAudioURL] = useState<string | null>(null);
    const [loading, setLoad] = useState(false);

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

        const formData = new FormData();
        formData.append('file', audioFile, audioFile.name);  

        try {
            const response = await Api.externalAudioUpload(formData);  
            console.log("transcription")
            console.log(response?.data?.chat)
           
            const data = {
                transcribe_chat: response?.data?.chat,
                job_profile_id: 46,
                all_user_id: 1959,
                template: false,
                generate: false,
                external: true,
                challenge: false
            };
            const resp = await Api.sessionExternalCreate(data);
            console.log(resp?.data)
            setLoad(false)

        } catch (error) {
            console.error('Error uploading audio:', error);
        }
    };

    return (
        <>
            <div className="audio-uploader-container" style={{backgroundColor: "#f46b31", width:'10px'}}>
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
            </div>

        </>
    );
};

export default AudioUpload;
