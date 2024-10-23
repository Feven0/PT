import { useState, useRef, useEffect, useContext } from 'react';
import { Card, message, Spin, Collapse } from 'antd';
import { OpenAI } from 'openai';
import WaveSurfer from 'wavesurfer.js';
import { AudioChatRecord, OverallFeedbackModal } from './index';
import useMiddleSocket from '../hooks/useMiddleSocket';
import { ProviderContext } from '../context/context';
import fade from '../assets/fade-circles.svg';

const { Panel } = Collapse;

const apiKey = `${import.meta.env.VITE_REACT_APP_OPENAI_KEY}`;

interface CustomWaveSurferOptions {
    container: string;
    audioContext?: AudioContext; 
    waveColor?: string;
    progressColor?: string;
    height?: number;
    responsive?: boolean;
}

const Audio = () => {
        const { handleAudioInterview, loading, audiointerview, seconds, minutes, pause, reset, setLoading } = useMiddleSocket();
        const { latestsession } = useContext<any>(ProviderContext);
        const [audioUrl, setAudioUrl] = useState<any>(null);
        const [dataFromAudio, setDataFromAudio] = useState<any>(false);
        const [input, setInput] = useState<any>("");
        const [show, setShow] = useState<any>(true);
        const [counter, setCounter] = useState<any>(1);
        const wavesurferRef = useRef<WaveSurfer | null>(null);
        const openai = new OpenAI({ apiKey, dangerouslyAllowBrowser: true });

        // const audiointerview = [{
        //     "user_type": "assistant",
        //     "content_type": "question_feedback",
        //     "complete": false,
        //     "content": {
        //         "time_taken": "null",
        //         "response": "null",
        //         "realtime_evaluation": {
        //             "overall": {
        //                 "relevance": "weak",
        //                 "feedback": "Your response suggested a basic understanding of time management through the use of scheduling tools. However, it lacked depth and specific strategies that demonstrate how you effectively manage your workload, especially when juggling multiple projects. Providing examples or elaborating on how these tools help you prioritize tasks would strengthen your answer."
        //             },
        //             "answer_relevancy": [
        //                 {
        //                     "level": "50",
        //                     "reason": "The mention of scheduling tools is relevant, but the response does not provide sufficient detail or context to fully address the question."
        //                 }
        //             ],
        //             "communication_skills": [
        //                 {
        //                     "skill": "clarity",
        //                     "level": "Good",
        //                     "reason": "Your response was coherent, but it could benefit from more elaboration to enhance understanding."
        //                 },
        //                 {
        //                     "skill": "engagement",
        //                     "level": "Poor",
        //                     "reason": "The response lacked enthusiasm and did not engage the interviewer effectively, making it seem less compelling."
        //                 }
        //             ]
        //         },
        //         "interview_evaluation": {
        //             "evaluation": "Your performance in the interview indicates a foundational understanding of machine learning and software engineering concepts, but there are areas that require improvement. Specifically, your responses lacked depth and concrete examples, which are crucial for demonstrating your experience and capabilities. To be a better fit for the role, focus on providing specific instances of your work and the outcomes achieved, especially in collaborative settings.",
        //             "recommendation": [
        //                 {
        //                     "title": "Effective Communication Skills",
        //                     "resource": "The Complete Communication Skills Masterclass for Life",
        //                     "type": "Online Course",
        //                     "link": "www.udemy.com"
        //                 },
        //                 {
        //                     "title": "Project Management Fundamentals",
        //                     "resource": "Project Management Professional (PMP) Certification Training",
        //                     "type": "Online Course",
        //                     "link": "www.coursera.org"
        //                 },
        //                 {
        //                     "title": "Deep Learning Specialization",
        //                     "resource": "Deep Learning Specialization by Andrew Ng",
        //                     "type": "Online Course",
        //                     "link": "www.coursera.org"
        //                 }
        //             ],
        //             "competency": [
        //                 {
        //                     "name": "Machine Learning",
        //                     "sfia_level": "3"
        //                 },
        //                 {
        //                     "name": "Communication Skills",
        //                     "sfia_level": "2"
        //                 },
        //                 {
        //                     "name": "Project Management",
        //                     "sfia_level": "2"
        //                 }
        //             ],
        //             "overall_performance": 50,
        //             "message": "Good"
        //         },
        //         "interview_evaluation_metrics": {
        //             "performance": [
        //                 {
        //                     "name": "confidence_level",
        //                     "level": "Poor",
        //                     "reason": "You appeared unsure and lacked confidence during your response, which affected the clarity of your communication."
        //                 }
        //             ],
        //             "areas_of_improvement": [
        //                 {
        //                     "skill": "Time Management",
        //                     "description": "You need to provide specific examples of how you manage your time and workload effectively. Instead of general statements about collaboration, focus on concrete instances where you successfully handled multiple projects and the strategies you employed."
        //                 }
        //             ],
        //             "strength": [
        //                 {
        //                     "skill": "Collaboration",
        //                     "description": "You mentioned collaboration with developers, indicating an understanding of teamwork. However, you need to enhance this by providing detailed examples of successful collaborations and their outcomes."
        //                 }
        //             ],
        //             "time_management": {
        //                 "fail": 0,
        //                 "pass": 0
        //             },
        //             "relevancy": [
        //                 {
        //                     "index": 1,
        //                     "level": "50",
        //                     "reason": "The mention of scheduling tools is relevant, but the response does not provide sufficient detail or context to fully address the question."
        //                 }
        //             ],
        //             "message": "Good",
        //             "rating": 2
        //         }
        //     }
        // }]

        console.log("audioooo", audiointerview)

        let previous_question = "";
        let timerValue: any;

        useEffect(() => {
            synthesizeAudio(audiointerview)
        }, [audiointerview])

       const synthesizeAudio = async (data: any) => {
        try {
            if(data !== undefined){
                setLoading(true)
                const feedcheck = data[0]?.content?.realtime_evaluation
                const response = data[0]?.content?.response
                const feedback = data[0]?.content?.realtime_evaluation?.overall?.feedback;
                const question = data[0]?.content?.response?.question;
                const endMessage = data[0]?.content?.response?.end_message;
                const time_limit = data[0]?.content?.response?.time_limit;
                let textToRead = "";

                if(feedcheck === "null" && response !== "null") {
                    textToRead = `Let start the interview: Now, ${question} ${endMessage}`;
                }
                else if(response !== "null" && feedcheck !== "null") {
                    textToRead = `${feedback}. Now, ${question}, and you must provide an answer with in ${time_limit} minutes ${endMessage}`;
                } else {
                    const overall  = data[0]?.content?.interview_evaluation?.evaluation
                    textToRead = `${feedback}. We are done with the interview, Here is your overall performance evaluation ${overall}`
                }

                const mp3 = await openai.audio.speech.create({
                    model: "tts-1-hd",
                    voice: "nova",
                    input: textToRead,
                });

                const audioBlob = new Blob([await mp3.arrayBuffer()], { type: 'audio/mpeg' });
                const url = URL.createObjectURL(audioBlob);

                if (audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                }
                setAudioUrl(url);
                setLoading(false);
            }
        } catch (error) {
            console.error("Error generating audio:", error);
            message.error("Failed to generate audio. Please try again.");
        }
    };
    
    useEffect(() => {
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        wavesurferRef.current = WaveSurfer.create({
            container: '#waveform',
            audioContext: audioContext, 
            waveColor: '#6c63ff',
            progressColor: '#ff6f61',
            height: 128,
            responsive: true,
        }as CustomWaveSurferOptions);

        if (audioUrl) {
            wavesurferRef.current.load(audioUrl);
            wavesurferRef.current.on('ready', () => {
                wavesurferRef.current?.play();
            });
            wavesurferRef.current.on('finish', () => {
                reset(); 
            });
        }

        return () => {
            wavesurferRef.current?.destroy();
        };
    }, [audioUrl]); 

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
        if(audioTranscript !== undefined){
            submitAudio(audioTranscript)
        }
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

    const startInterview = async() => {
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latestsession

        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        pause();
        handleAudioInterview({ 
            input: input, 
            interview: audiointerview, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
        setShow(false)
    }  

    const submitAudio = async(audioTranscript: any) => {
        if(audiointerview !== undefined){
            previous_question = audiointerview[0]?.content?.response?.question
        }
        const user_session = latestsession
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        handleAudioInterview({ 
            input: audioTranscript, 
            interview: audiointerview, 
            user_session: user_session,
            counter: counter,
            timerValue: timerValue,
            previous_question: previous_question
        });
        setCounter(counter < 9 ? counter + 1 : 1);
    }

   
    return (
        <>
        <div style={{display: 'flex', gap: '15rem', margin: '0rem 5rem 0rem 10rem'}}>
            <div style={{ width: '600px' }}>
                <Card title="Audio Chat" bordered={true} >
                    <div style={{ 
                        fontSize: '20px', 
                        display: 'flex', 
                        justifyContent:'space-between',
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
                {(audiointerview !== undefined && audiointerview[0]?.content?.realtime_evaluation !== "null") &&(
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
                                    {audiointerview[0]?.content?.realtime_evaluation?.communication_skills?.map((skill: any, index: any) => (
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

                {(audiointerview !== undefined && audiointerview[0]?.content?.interview_evaluation !== "null") &&(
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