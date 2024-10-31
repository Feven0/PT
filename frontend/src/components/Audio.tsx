import { useState, useRef, useEffect } from 'react';
import { Typography, Card, message, Spin, Collapse } from 'antd';
import { OpenAI } from 'openai';
import WaveSurfer from 'wavesurfer.js';
import { AudioChatRecord, OverallFeedbackModal } from './index';
import useMiddleSocket from '../hooks/useMiddleSocket';
import fade from '../assets/fade-circles.svg';
import '../styles/AudioRecorder/audiorecorder.css'
const { Panel } = Collapse;

const { Title } = Typography;
const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;

const Audio = () => {
        const { handleAudioInterview, loading, audiointerview, audiohistory, seconds, minutes, pause, reset, setLoading } = useMiddleSocket();
        // const {userId, jobId} = useParams()
        // const userId = 16
        // const jobId = 1045
        const latest = JSON.parse(localStorage.getItem("userSession"));
        const [audioUrl, setAudioUrl] = useState(null);
        const [dataFromAudio, setDataFromAudio] = useState<any>(false);
        const [input, setInput] = useState<any>("");
        const [show, setShow] = useState<any>(true);
        const [counter, setCounter] = useState<any>(1);
        const [buffer, setBuffer] = useState('');

        const wavesurferRef = useRef(null);
        const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

 
        // console.log("audioooo caroline", buffer)
        // console.log("audiohistory", audiohistory)

        let previous_question = "";
        let timerValue: any;

        // Initialize WaveSurfer
    useEffect(() => {
        wavesurferRef.current = WaveSurfer.create({
            container: '#waveform',
            audioContext: new (window.AudioContext || window.webkitAudioContext)(),
            waveColor: '#6c63ff',
            progressColor: '#ff6f61',
            height: 128,
            responsive: true,
        });

        return () => {
            wavesurferRef.current.destroy();
        };
    }, []);

    // Handle audio URL changes
    useEffect(() => {
        if (audioUrl) {
            wavesurferRef.current.load(audioUrl);
            wavesurferRef.current.on('ready', () => {
                wavesurferRef.current.play();
            });
            wavesurferRef.current.on('finish', () => {
                setAudioUrl(null); // Reset audio URL after playback
            });
        }
    }, [audioUrl]);

    // Function to synthesize audio from text
    const synthesizeAudio = async () => {
        const text = 'I have work at the station near the line stree around lebu. The station was dirty but wide enough to handle too many passangers'
        if (!text) return; 
        try {
            setLoading(true); 
            
            const mp3 = await openai.audio.speech.create({
                model: "tts-1-hd",
                voice: "nova",
                input: text,
            });

            const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
            const url = URL.createObjectURL(audioBlob);
            
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
            }
            setAudioUrl(url); 
            setLoading(false);
        } catch (error) {
            console.error("Error generating audio:", error);
            setLoading(false); 
        }
    };

    useEffect(() => {
        const processChunks = async () => {
            let tempBuffer = ''; 
            
            for (const chunk of audiohistory) {
                console.log("audiochunk", chunk); 
                tempBuffer += chunk;

                if (chunk.endsWith(' ') || chunk.endsWith('.') || chunk.endsWith('?') || chunk.endsWith('!')) {
                    //await synthesizeAudio(tempBuffer.trim()); 
                    tempBuffer = ''; 
                }
            }
        };

        if (audiohistory.length > 0) {
            processChunks(); 
        }
    }, [audiohistory]); 


    const handleWaveformClick = (e: any) => {
        const waveformWidth = e.currentTarget.clientWidth;
        const clickPosition = e.clientX - e.currentTarget.getBoundingClientRect().left;
        const seekTo = clickPosition / waveformWidth;

        if (wavesurferRef.current) {
            wavesurferRef.current.seekTo(seekTo);
            wavesurferRef.current.play();
        }
    };
    const handleDataFromAudio = (audioTranscript: any) => {
        setInput(audioTranscript);
        console.log("transcription org.", audioTranscript)
        if(audioTranscript !== undefined){
            submitAudio(audioTranscript)
        }
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

    const startInterview = async() => {
        // const filteredJob = jobs.filter(match => match.job_profile_id === parseInt(jobId as any));
        // const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latest
        // const data = {
        //     jobId: jobId,
        //     userId: userId,
        //     name: filteredUser[0]?.name,
        //     cvJson: filteredUser[0],
        //     jbJson: filteredJob[0]
        // };
        // const response = await Api.sessionCreate(data);
        // localStorage.setItem("userSession", JSON.stringify(response?.data))
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        pause();
        handleAudioInterview({ 
            input: input, 
            interview: audiohistory, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
        setShow(false)
    }  

    const submitAudio = async(audioTranscript: any) => {
        // const filteredJob = jobs.filter(match => match.job_profile_id === parseInt(jobId as any));
        // const filteredUser = users.filter(match => match?.user_profile_id === parseInt(userId as any));
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latest
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        handleAudioInterview({ 
            input: audioTranscript, 
            interview: audiohistory, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
    }



    return (
        <>
        <div onClick={synthesizeAudio}>Let's Test</div>
        <div className="audio-history-container">
            {audiohistory.map((msg, index) => (
                <p key={index} className="audio-message">{msg}</p> 
            ))}
        </div>

        <div style={{display: 'flex', gap: '15rem', margin: '0rem 5rem 0rem 10rem'}}>
            <div style={{ width: '600px' }}>
                <Card title="Audio Interview" bordered={true} >
                    <div style={{ 
                        fontSize: '20px', 
                        display: 'flex', 
                        justifyContent:'space-between',
                        // textAlign: 'end'
                        }}>
                        
                        {show && (<div>
                            <button style={{fontSize:'1rem',backgroundColor: '#f34e38', border: 'none', padding:'0.7rem', borderRadius: '0.6rem', cursor: 'pointer', width: '8rem'}} onClick={startInterview}>
                                start
                            </button>
                        </div>)}
                        <div>{String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}</div>                    
                    </div>
                    
                    {(loading || dataFromAudio) && <Spin indicator={<img src={fade} alt="" className='h-10' />} />}

                    <div 
                        id="waveform" 
                        style={{ width: '100%', height: '128px', marginTop: '20px' }} 
                        onClick={handleWaveformClick}
                    ></div>

                    <div>
                    <AudioChatRecord sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} pause={pause}/>
                    </div>
                </Card>
            </div>
            
            <div style={{display:'flex', flexDirection: 'column'}}>
                {(audiointerview !== undefined && !loading && audiointerview[0]?.content?.realtime_evaluation !== "null") &&(
                    <div style={{width: '28rem', bottom: '0', marginBottom: '0'}}>
                        <div style={{
                        textAlign: 'justify', 
                        width: '30rem',
                        padding: '1.5rem',
                        borderRadius: '1rem',
                        color: '#333',
                        backgroundColor: '#f9f9f9', 
                        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', 
                    }}>
                        <Collapse defaultActiveKey={['1']} style={{ marginTop: '1rem' }}>
                            <Panel 
                                header="Feedback" 
                                key="1" 
                                style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }} 
                            >
                                <div className='message-text' style={{ padding: '1rem', color: '#6b6666', lineHeight: '1.5rem' }}>{audiointerview[0]?.content?.realtime_evaluation?.overall?.feedback}</div>
                            </Panel>
                            <Panel 
                                header="Other Metrics" 
                                key="2" 
                                style={{ backgroundColor: '#f3f5f7', border: 'none', borderRadius: '1rem' }}
                            >
                                <div style={{ padding: '1rem' }}>
                                    {audiointerview[0]?.content?.realtime_evaluation?.communication_skills?.map((skill, index) => (
                                        <div key={index} style={{ marginBottom: '0.5rem' }}>
                                            <strong style={{ fontSize: '1.1rem' }}>
                                                {skill?.skill}: 
                                            </strong>
                                            <span style={{ marginLeft: '0.5rem', color: '#555' }}>{skill?.level}</span>
                                        </div>
                                    ))}
                                </div>
                            </Panel>
                        </Collapse>
                    </div>
                    </div>
                )}

                {(audiointerview !== undefined && !loading && audiointerview[0]?.content?.interview_evaluation !== "null") &&(
                    <div style={{marginTop: '1.8rem'}}>
                        <OverallFeedbackModal
                            metricsData={audiointerview[0]?.content?.interview_evaluation_metrics}
                            evaluationData={audiointerview[0]?.content?.interview_evaluation} 
                        />
                    </div>
                )}
            </div>
        </div>
            
        </>
    );
};

export default Audio;