import { useState, useEffect } from 'react';
import { Card, Input, Button, Spin } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import {
    ChatAudioRecorder, 
    OverallFeedbackModal, 
    LoadingSpinner, 
    Messages,
    CancelModal
} from './index'
import Api from '../Services/Services';
import "../styles/InterviewChat/interviewchat.css"

const InterviewChat = () => {
    const { 
        handleInterview, 
        seconds, 
        minutes, 
        reset, 
        pause, 
        interview, 
        setChatInterview, 
        startfetching, 
        setStartFetch,
        startchat, 
        setChat } = useMiddleSocket();
    const [input, setInput] = useState<any>("");
    const [dataFromAudio, setDataFromAudio] = useState<any>(false);
    const [loadin, setLoad] = useState<any>(false);
    const [sessions, setSession] = useState<any>([]);
    const latest = JSON.parse(localStorage.getItem("userSession") || 'null');       
    console.log("latest_session_info", interview) 
    const [loadingSessionId, setLoadingSessionId] = useState(null);
    const [isHovered, setIsHovered] = useState(false);
    let timerValue: any;
    const charLimit = 1200; 
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [loading, setLoading] = useState(false);
    const [questions, setQuestions] = useState<any>([]); 
    const handleClose = () => setShowCancelModal(false);
    const handleShow = () => setShowCancelModal(true);


    const buttonStyle = {
        color: '#ffffff',
        fontWeight: 'bolder',
        fontSize: '1rem',
        backgroundColor: isHovered ? '#888888' : '#a5a2a2', 
        border: 'none', 
        padding: '8px 20px', 
        cursor: 'pointer', 
        transition: 'background-color 0.3s',
        borderRadius: '5px 0 5px 0'
    };

    const ExecuteInterview = () => {
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;    
        const inputToSend = questions.length > 0 ? questions : input;    
        handleInterview({ 
            input: inputToSend, 
            user_session,
            timerValue,
            job_profile_id: 232,
            all_user_id: 1920
        });    
        setInput('');
        setQuestions([]); 
        setChat(true); 
    };
    
    const handler = () => {
        ExecuteInterview();
        pause();
    };

    const startSession = async() => {
        setLoad(true)
        const data = {
            job_profile_id: 232,
            all_user_id: 1920
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleInterview({ 
                input, 
                user_session: response?.data,
                timerValue,
                job_profile_id: 232,
                all_user_id: 1920
            });
            setInput('');
            setChat(true) 
        }
        setChatInterview([])
        setLoad(false)
    }

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput((prevInput: any) => prevInput + ' ' + audioTranscript);
    };

    function handleDataAudio(data: any) {
        setDataFromAudio(data);
    }

    const handleChange = (e: any) => {
        const newInput = e.target.value;  
        if (newInput.length <= charLimit) {
            setInput(newInput);
        }
    };

    const fetchChatHistory = async (session: any) => {
        const sessionId = session?.id
        setLoadingSessionId(sessionId)
        setChat(false) 
        setChatInterview([])
            const data = {
                sessionId: sessionId
            }
            const response = await Api.fetchChatHistory(data)
            const fetched_session = await Api.fetchSingleSession(data)
            localStorage.setItem("userSession", JSON.stringify(fetched_session?.data))

            // console.log("fetching data...", response?.data)
            // console.log("fetching data observers...", fetched_session?.data)

        setChatInterview(response?.data?.total)
        setLoadingSessionId(null);
        if(fetched_session?.data?.attributes?.status == 'Completed'){
            setChat(false)
            reset() 
        }
        else if(fetched_session?.data?.attributes?.status == 'Incomplete') {
           setChat(true) 
        }        
    }

    const closeSession = async() => {
        const user_session = {
        "id": "513",
        "attributes": {
            "slug": "all_user_id: 1959",
            "status": "Incomplete",
            "attributes": {
                "persona": "Act as an experienced HR analyst with expertise in evaluating job descriptions and user profiles. \n\nThe documents are:\n    - Job description: {'role': 'Python Intern (AI-Driven Recruitment Automation)', 'purpose': 'To develop and implement a solution for automating the evaluation of incoming job applications using AI and automation.', 'required_qualifications': 'R, e, c, e, n, t,  , g, r, a, d, u, a, t, e,  , i, n,  , C, o, m, p, u, t, e, r,  , S, c, i, e, n, c, e, ,,  , D, a, t, a,  , S, c, i, e, n, c, e, ,,  , A, I, ,,  , o, r,  , a,  , r, e, l, a, t, e, d,  , f, i, e, l, d, ;,  , p, r, o, f, i, c, i, e, n, t,  , i, n,  , P, y, t, h, o, n,  , w, i, t, h,  , e, x, p, e, r, i, e, n, c, e,  , i, n,  , l, i, b, r, a, r, i, e, s,  , l, i, k, e,  , N, u, m, P, y,  , a, n, d,  , P, a, n, d, a, s, ;,  , c, o, m, f, o, r, t, a, b, l, e,  , w, i, t, h,  , A, P, I, s, .', 'duties_responsibilities': \"A, n, a, l, y, z, e,  , t, h, e,  , c, u, r, r, e, n, t,  , m, a, n, u, a, l,  , s, h, o, r, t, l, i, s, t, i, n, g,  , p, r, o, c, e, s, s, ,,  , i, n, t, e, g, r, a, t, e,  , M, a, n, a, t, a, l, ', s,  , A, P, I,  , w, i, t, h,  , a,  , L, a, r, g, e,  , L, a, n, g, u, a, g, e,  , M, o, d, e, l,  , (, L, L, M, ), ,,  , d, e, v, e, l, o, p,  , a,  , c, o, d, e, b, a, s, e,  , u, s, i, n, g,  , G, i, t, H, u, b, ,,  , d, o, c, u, m, e, n, t,  , p, r, o, c, e, s, s, e, s, ,,  , a, n, d,  , p, r, e, s, e, n, t,  , t, e, c, h, n, i, c, a, l,  , a, p, p, r, o, a, c, h, e, s, .\", 'attributes.apply_link': '', 'competencies': [{'name': 'Programming Languages', 'skills': ['Python'], 'summary': 'Entry level competency in Python programming is required.'}, {'name': 'Data Engineering', 'skills': ['data handling', 'data analysis'], 'summary': 'Basic level of competency in data engineering practices is necessary.'}, {'name': 'Professional Communication', 'skills': ['oral communication', 'written communication'], 'summary': 'Entry level competency in professional communication is necessary.'}, {'name': 'API Integration', 'skills': ['API usage', 'integration'], 'summary': 'Basic competency in API usage and integration is required.'}]}\n    - User Profile: {'basics.attributes': [], 'projects.attributes': [], 'education.attributes': [], 'work_experience.attributes': []}\n\nEmployment Type: Look for individuals with a strong academic foundation, a passion for the industry, and a desire to learn and grow. Assess their relevant skills, their career aspirations, and their willingness to take on new challenges and contribute to real-world projects.\nIndustry: Prioritize candidates with strong technical skills, a passion for innovation, and the ability to adapt to rapidly changing technologies. Evaluate their problem-solving abilities, their experience with relevant tools and technologies, and their capacity for continuous learning.\nRole Level: Prioritize candidates who are eager to learn, possess a strong work ethic, and are excited to contribute to the team. Focus on their transferable skills, their willingness to take on new challenges, and their potential for growth within the company.\nDepartment / Title: Prioritize candidates who possess strong problem-solving abilities, a deep understanding of engineering principles, and a passion for developing innovative solutions. Assess their technical expertise, their experience with relevant tools and technologies, and their ability to work collaboratively on complex projects.\nWork Environment: Look for individuals who thrive in a collaborative environment, enjoy interacting with colleagues in person, and value the benefits of working from a central location. Assess their communication style, their ability to work effectively as part of a team, and their comfort level with a structured work setting.\nCompany Size: Prioritize candidates who are adaptable, comfortable wearing multiple hats, and thrive in a fast-paced environment with a high degree of autonomy. Assess their ability to take initiative, their comfort level with ambiguity, and their willingness to contribute across different areas of the business.\nCompany Culture: Seek out candidates who are creative thinkers, embrace new challenges, and are passionate about pushing boundaries and developing innovative solutions.  Assess their ability to think outside the box, their willingness to challenge the status quo, and their comfort level with taking risks.\nTeam Structure and Performance Metrics: Prioritize candidates who are independent, proactive, and comfortable taking initiative.  Assess their ability to work autonomously with minimal supervision, their problem-solving skills, and their willingness to contribute ideas and take ownership of their work.\nEducation: Look for candidates who possess a strong foundation in relevant industry concepts and can apply their academic knowledge to practical situations. Evaluate their coursework, internships, and projects for evidence of critical thinking, problem-solving, and potential for future career growth.\n\n\n\nUse non-gender-specific pronouns like 'you' and 'your' instead of gender-specific pronouns or names. \n\nVERY IMPORTANT: Append 'TERMINATE' to every response you provide to the user."
            },
            "createdAt": "2025-01-14T08:07:56.820Z",
            "i_persona_observer": {
                "data": null
            },
            "tinder_job_profile": {
                "data": {
                    "id": "1693"
                }
            },
            "tinder_user_profile": {
                "data": {
                    "id": "197"
                }
            },
            "updatedAt": "2025-01-14T08:07:56.820Z"
        }
    }
       
        const obj = {
            user_session: user_session,
            job_profile_id: 1693,
            all_user_id: 1959
        }
        const param = {data: obj}
        const response = await Api.CloseSession(param)
        console.log("response-close", response?.data)
    }

    const deleteSession = async() => {
        const user_session = latest;
        const data = {sessionId: user_session?.id}
        const response = await Api.DeleteSession(data)
        console.log("response-delete", response?.data)
    }

    const fetchSession = async() =>{
        const data = {
            job_profile_id: 232,
            all_user_id: 1920
        }
        const response = await Api.fetchSession(data)
        // console.log("sessions", response?.data)
        setSession(response?.data)
        setStartFetch(false);
    }

    useEffect(() => {
        if (startfetching) {
            fetchSession();
        }
    }, [startfetching == true]);
        
    const handleConfirm = async (action: any) => {
        setLoading(true);
        try {
            if (action === 'pause') {
                // Logic to pause the interview
                window.location.reload();
                console.log("Interview paused.");
            } else if (action === 'stopEvaluate') {
                // Logic to stop and evaluate
                await closeSession()
                console.log("Interview stopped and evaluated.");
                window.location.reload();
            } else if (action === 'stopDelete') {
                // Logic to stop and delete
                await deleteSession()
                console.log("Interview stopped and deleted.");
                window.location.reload();
            }
        } catch (error) {
            console.error("Error during session action:", error);
        } finally {
            setLoading(false);
            handleClose();
        }
    };

    // const handleKeyPress = (e: any) => {
    //     if (e.key === 'Enter' && !e.shiftKey && input.trim() !== '' && interview?.length === 21) {
    //         setQuestions([...questions, input.trim()]);
    //         setInput(''); 
    //         e.preventDefault(); 
    //     }
    // };

    return (
        <>
            <div className="interview-chat-container">
                <div style={{marginTop: '2rem'}}>                
                    <div>
                        <Button 
                            style={{ 
                                margin:'1rem', 
                                textAlign:'center',  
                                color:'#ffffff', 
                                fontWeight: 'bolder', 
                                fontSize: '0.81rem'
                            }}
                            onClick={startSession}
                            >
                                start new session
                                <span>
                                  {loadin && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                </span>
                        </Button>
                        
                        <div
                            style={{ 
                                display: 'flex',
                                flexDirection: 'column', 
                                width:'24rem',  
                                maxHeight: '500px',  
                                overflowY: 'scroll',   
                                padding: '0.5rem',
                                scrollbarWidth: 'none',  
                                msOverflowStyle: 'none', 
                                WebkitOverflowScrolling: 'touch',  
                                cursor: 'pointer'
                            }}
                        >
                        {/* Display userjob sessions */}
                        {(Array.isArray(sessions) && sessions.length > 0) && (
                            <div>
                                {sessions.map((session: any, index: any) => (
                                    session?.attributes?.status !== 'Deleted' && (  // Condition to check before rendering
                                        <div 
                                            key={session.id} 
                                            className="session" 
                                            style={{ 
                                                display: 'flex', 
                                                justifyContent: 'space-between', 
                                                alignItems: 'center', 
                                                backgroundColor: '#ffffff', 
                                                borderRadius: '10px', 
                                                marginBottom: '10px',
                                                padding: '10px' 
                                            }}>
                                            <div onClick={() => fetchChatHistory(session)}>
                                                {new Date(session?.attributes?.createdAt).toLocaleDateString('en-US', {
                                                    month: 'short',
                                                    day: 'numeric',
                                                })}
                                                {' at '}
                                                {new Date(session?.attributes?.createdAt).toLocaleTimeString('en-US', {
                                                    hour: '2-digit',
                                                    minute: '2-digit',
                                                    hour12: true,
                                                })}
                                            </div>
                                            {session?.attributes?.i_persona_observer?.data !== null && (
                                                <span>
                                                    {(() => {
                                                        const item = session.attributes.i_persona_observer.data;
                                                        return (
                                                            <OverallFeedbackModal
                                                                key={index}
                                                                metricsData={item?.attributes?.attributes?.interview_evaluation_metrics}
                                                                evaluationData={item?.attributes?.attributes?.interview_evaluation} 
                                                            />
                                                        );
                                                    })()}
                                                </span>
                                            )}
                                            <span 
                                                onClick={() => fetchChatHistory(session)}
                                                style={{ 
                                                    color: session?.attributes?.status === 'Incomplete' ? 'rgba(255, 0, 0, 0.63)' : 'rgba(0, 232, 0, 0.603)' }}>
                                                {session?.attributes?.status}
                                            </span>
                                            {loadingSessionId === session.id && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                        </div>
                                    )
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
            
            {/* Interview Chats */}
            <Card className="chat-box" style={{ height: '36rem', width: '50rem', overflowY: 'auto' }}>
                <Messages interview={interview}/>
            </Card>
            
            {/* Input area */}
            <div className='chat-timer-box' style={{}}>
                {(startchat) && (
                    <div>
                        {/* cancel section */}
                        <div>
                            <Card>
                                <Button 
                                    style={{ 
                                        margin: '1rem', 
                                        textAlign: 'center',  
                                        color: '#ffffff', 
                                        fontWeight: 'bolder', 
                                        fontSize: '0.81rem' 
                                    }}
                                    onClick={handleShow}
                                >
                                    Cancel
                                    <span>
                                        {loading && <LoadingSpinner style={{ marginLeft: '5px' }} />}
                                    </span>
                                </Button>
                            </Card>

                            {/* Modal for confirmation */}
                            <CancelModal 
                                visible={showCancelModal} 
                                handleClose={handleClose} 
                                handleConfirm={handleConfirm}
                            />
                        </div>
                       
                        {/* Input area */}
                        <div>
                            <div style={{ fontSize: '50px', textAlign: 'center' }}>
                                {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
                            </div>
                    
                            <div className='input-container' style={{width: '25rem'}}>
                                <Input.TextArea
                                    value={input}
                                    placeholder="Put your answer here"
                                    onChange={handleChange}
                                    // onKeyPress={handleKeyPress}
                                    rows={2}
                                    className="input-area"
                                />
                                <div style={{ margin: '5px', color: '#d1cccb' }}>
                                    <span>{`you must follow character limit:
                                        ${input.length}/${charLimit}`}
                                    </span>
                                </div>

                                {interview?.length === 21 && (
                                    <div>
                                        <ul>
                                            {questions.map((question: any, index: any) => (
                                                <li key={index}>{question}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                
                                <div className='actions'>
                                    <div className='actions-audio'>
                                        <ChatAudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
                                        {dataFromAudio && <Spin indicator={<img src={fade} alt="" className='actions-load' />} />}
                                    </div>
                                    <div style={{marginTop: '0.97rem'}}>
                                        <button 
                                        onClick={handler}
                                        style={buttonStyle}
                                        onMouseEnter={() => setIsHovered(true)}
                                        onMouseLeave={() => setIsHovered(false)}
                                        className='actions-btn'>
                                            submit
                                        </button>
                                    </div>
                                </div>
                            </div>                            
                        </div>
                    </div>
                )}
            </div>

          </div>
        </>
    );
};

export default InterviewChat;