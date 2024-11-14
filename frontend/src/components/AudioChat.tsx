import { useState } from 'react';
import axios from 'axios';

const AudioChat = () => {
    const [content, setContent] = useState('');
    const [audioUrl, setAudioUrl] = useState('');
  

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        console.log('content:', content);
        const response = await axios.post(`http://0.0.0.0:8080/chat?content=${content}`);

        if (response) {
            console.log('was that all about:', response);

            const data = await response.data;
            const blob = await data.blob(); // Get the response as a blob
            const url = URL.createObjectURL(blob); // Create a URL for the blob
            setAudioUrl(url); // Set the audio URL for playback

        } else {
            console.error('Error fetching audio:', response);
        }
    };

    const handleChange = (e: any) => {
        const newInput = e.target.value;
        setContent(newInput); 
    };

    return (
        <div>
            {/* <form> */}
                <input
                    type="text"
                    value={content}
                    onChange={handleChange}
                    // onChange={(e) => setContent(e.target.value)}
                    placeholder="Type your message"
                />
                <button type="submit"  onClick={handleSubmit}>Send</button>
            {/* </form> */}
            {audioUrl && (
                <audio controls>
                    <source src={audioUrl} type="audio/opus" />
                    Your browser does not support the audio element.
                </audio>
            )}
        </div>
    );
};

export default AudioChat;