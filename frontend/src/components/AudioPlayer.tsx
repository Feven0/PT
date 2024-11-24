import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';

interface Data {
    audiointerview: any
}

const AudioPlayer: React.FC<Data> = ({ audiointerview }) => {
    const wavesurferRef = useRef<any>(null);
    const audioQueue = useRef<any>([]);  
    const isPlayingRef = useRef<any>(false);
    const previousLengthRef = useRef<any>(0); 
    const [isFirstLoad, setIsFirstLoad] = useState<any>(true);  

    const [loading, setLoading] = useState(false);

    const handleWaveformClick = (e: any) => {
        const waveformWidth = e.currentTarget.clientWidth;
        const clickPosition = e.clientX - e.currentTarget.getBoundingClientRect().left;
        const seekTo = clickPosition / waveformWidth;

        if (wavesurferRef.current) {
            wavesurferRef.current.seekTo(seekTo);
            wavesurferRef.current.play();
        }
    };

    useEffect(() => {
        wavesurferRef.current = WaveSurfer.create({
            container: '#waveform',
            waveColor: 'violet',
            progressColor: 'purple',
        });

        wavesurferRef.current.on('finish', () => {
            if (audioQueue.current.length > 0) {
                playNextAudio();
            }
        });

        return () => {
            if (wavesurferRef.current) {
                wavesurferRef.current.destroy();
                wavesurferRef.current = null;
            }
        };
    }, []);

    const playNextAudio = async () => {
        if (audioQueue.current.length > 0 && !isPlayingRef.current) {
            const nextUrl = audioQueue.current.shift(); 
            isPlayingRef.current = true;

            if (wavesurferRef.current) {
                wavesurferRef.current.load(nextUrl);  

                wavesurferRef.current.once('ready', () => {
                    wavesurferRef.current.play();
                });

                wavesurferRef.current.once('finish', () => {
                    isPlayingRef.current = false;  
                    // if (audioQueue.current.length > 0) {
                    //     playNextAudio();  // Continue to the next audio in the queue
                    // }
                });
            } else {
                console.error("WaveSurfer instance is not initialized.");
            }
        }
    };

    const synthesizeAudio = async (newChunks: any) => {
        try {
            setLoading(true);

            if (newChunks.length > 0) {
                const concatenatedBlob = await concatenateChunks(newChunks);  
                const url = URL.createObjectURL(concatenatedBlob);
                audioQueue.current.push(url);  

                if (!isPlayingRef.current) {
                    playNextAudio();
                }
            } else {
                console.error('No audio interview chunks available');
            }

            setLoading(false);
        } catch (error) {
            console.error('Error processing audio:', error);
            setLoading(false);
        }
    };

    const concatenateChunks = async (chunks: any) => {
        const arrays = await Promise.all(chunks.map(async (chunkUrl: any) => {
            const response = await fetch(chunkUrl);
            const arrayBuffer = await response.arrayBuffer();
            return new Uint8Array(arrayBuffer);
        }));

        const totalLength = arrays.reduce((sum, arr) => sum + arr.length, 0);
        const concatenated = new Uint8Array(totalLength);

        let offset = 0;
        arrays.forEach(arr => {
            concatenated.set(arr, offset);
            offset += arr.length;
        });

        return new Blob([concatenated], { type: 'audio/mpeg' });
    };

    const processNewChunks = async () => {
        if (isFirstLoad) {
            const newChunks = audiointerview;  
            if (newChunks.length > 0) {
                await synthesizeAudio(newChunks);
                previousLengthRef.current = audiointerview.length;  
                setIsFirstLoad(false);  
            }
        } else {
            const newChunks = audiointerview.slice(previousLengthRef.current);  
            if (newChunks.length > 0) {
                await synthesizeAudio(newChunks);
                previousLengthRef.current = audiointerview.length;  
            }
        }
    };

    useEffect(() => {
        if (audiointerview.length > previousLengthRef.current) {
            processNewChunks(); 
        }
    }, [audiointerview]);

    return (
        <div>
            <div 
                id="waveform"
                onClick={handleWaveformClick}
            ></div>
            {loading && <p>Loading...</p>}
        </div>
    );
};

export default AudioPlayer;
