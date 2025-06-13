import { useState, useEffect } from 'react';
import { Card, Input, Button, Spin, Modal } from 'antd';
import fade from '../assets/fade-circles.svg';
import useMiddleSocket from '../hooks/useMiddleSocket';
import {
    ChatAudioRecorder, 
    OverallFeedbackModal, 
    LoadingSpinner, 
    Messages,
    CancelModal,
    AudioUpload
} from './index'
import Api from '../Services/Services';
import "../styles/InterviewChat/interviewchat.css"

const InterviewChat = () => {
    const { 
        handleInterview, 
        handleTemplateInterview,
        handleChallengeInterview,
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
    const [mode, setMode] = useState<any>('Audio');
    const [questions, setQuestions] = useState<any>([]); 
    const handleClose = () => setShowCancelModal(false);
    const handleShow = () => setShowCancelModal(true);
    
    const [template_id, setTemplateId] = useState<number>(0);
    const [challenge_id, setChallengId] = useState<number>(0);
    const [job_profile_id, setJobProfileId] = useState<number>(46); // Keep as-is if 46 is default

   
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
        const temp_id = template_id || latest?.template_id || 0;
        const cha_id = challenge_id || latest?.challenge_id || 0;
        const job_id = job_profile_id || latest?.job_profile_id || 0;

        const isTempValid = temp_id > 0;
        const isChallengeValid = cha_id > 0;
        const isJobProfileValid = job_id > 0;

        if (isTempValid && isChallengeValid) {
            console.log("🎯 Executing Template with Challenge");
            ExecutiveTemplate(temp_id, job_id, cha_id);
        } 
        else if (isTempValid && isJobProfileValid) {
            console.log("📄 Executing Template with Job Profile");
            ExecutiveTemplate(temp_id, job_id, cha_id);
        }
        else if (!isTempValid && isChallengeValid) {
            console.log("🔥 Executing Challenge");
            ExecutiveChallenge(cha_id);
        } 
        else if (!isTempValid && !isChallengeValid && isJobProfileValid) {
            console.log("🛠️ Generating Interview with Job Profile");
            ExecuteGenerateInterview();
        } 
        else {
            console.warn("⚠️ Invalid configuration: No valid identifiers provided");
        }
    };


    
    const ExecuteGenerateInterview = () => {
        console.log('ExecuteGenerateInterview')
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;    
        const inputToSend = questions.length > 0 ? questions : input;    
        handleInterview({ 
            input: inputToSend, 
            user_session,
            template_id: null,
            timerValue,
            challenge_id: 0,
            job_profile_id: 46,
            all_user_id: 1959
        });    
        setInput('');
        setQuestions([]); 
        setChat(true); 
    };

    const ExecutiveTemplate = async (temp_id: any, job_id: any, cha_id: any) => {
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;    
        console.log("*)9-0TYIGHVYONHUPIONUMKJNUONUIH", user_session)
        handleTemplateInterview({ 
            input, 
            user_session: user_session,
            template_id: temp_id,
            challenge_id: cha_id,
            job_profile_id: job_id,
            timerValue,
            all_user_id: 1959
        });
        setInput('');
        setChat(true); 
    }

    const ExecutiveChallenge = async (id: any) => {
        timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        const user_session = latest;    
        handleChallengeInterview({ 
            input, 
            user_session: user_session,
            challenge_id: id,
            timerValue,
            job_profile_id: 0,
            all_user_id: 1959
        });
        setInput('');
        setChat(true); 
    }
    
    const handler = () => {
        ExecuteInterview();
        pause();
    };

    const startSession = async() => {
        setLoad(true)
        console.log("i wish we had these")
        const data = {
            run_stage: 'dev',
            mode: mode,
            // job_profile_id: 9,
            // all_user_id: 55,
            job_profile_id: 46,
            all_user_id: 1959,
            template: false,
            generate: true,
            external: false,
            challenge: false,
            template_id: 0, 
            challenge_id: 0
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleInterview({ 
                input, 
                user_session: response?.data,
                template_id: null,
                timerValue,
                job_profile_id: 46,
                all_user_id: 1959
            });
            setInput('');
            setChat(true) 
        }
        setChatInterview([])
        setLoad(false)
        setShowModal(false);
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
            // const response = await Api.fetchChatHistory(data)
            const response = await Api.fetchSingleSession(data)
            localStorage.setItem("userSession", JSON.stringify(response?.data))
            setTemplateId(response?.data?.template_id) 
            setChallengId(response?.data?.challenge_id)
            // console.log("fetching data...", response?.data)
            console.log("fetching data observers...", response?.data?.template_id)

        setChatInterview(response?.data?.chat)
        setLoadingSessionId(null);
        if(response?.data?.status == 'Completed'){
            setChat(false)
            reset() 
        }
        else if(response?.data?.status == 'Incomplete') {
           setChat(true) 
        }        
    }

    const closeSession = async() => {
        const user_session = latest
       
        const obj = {
            user_session: user_session,
            job_profile_id: 46,
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
            "run_stage": "dev",
            "all_user_id": 1959,
            "job_profile_id": 46,
            "template_id": 0,
            "challenge_id": 0,
            "cursor": {
                        "page": 1, 
                        "pageSize": 20,
                        "page_count": 1,
                        "page_size": 20,
                        "query": {},
                        "total": 58
                    }
            }
        
        const response = await Api.fetchSession(data)
        console.log("sessions", response?.data)
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

    const [showModal, setShowModal] = useState(false); // Modal for the two options
    const [showTemplateModal, setShowTemplateModal] = useState(false); // Modal for templates
    const [showChallengeModal, setShowChallengeModal] = useState(false); 
    const [templates, setTemplates] = useState([]);
    const [challenges, setChallenges] = useState([]);


    const GetTemplates = async() => {
        const data = {
            run_stage: 'dev',
            job_profile_id: 46,
            challenge_id: 0,
            prompt_id: 0,
            type: '',
            cursor: {
                "page": 1, 
                "pageSize": 20,
                "page_count": 1,
                "page_size": 20,
                "query": {},
                "total": 58
            },
            filter: {},
            limit: 10,
            since: 7,
            information_level: 'minimal',
            return_skip: false
        };
        const response = await Api.GetTemplates(data)
        console.log("await....", response?.data)
        setTemplates(response?.data)
    }

    const GetChallenges = async() => {
        const response = await Api.GetChallenges()
        console.log("await...charilie.", response?.data)
        setChallenges(response?.data?.challenges)
    }

    const chooseTemplate = async (id: any) => {
        setLoad(true)
        const data = {
            job_profile_id: 46,
            all_user_id: 1959,
            template: true,
            generate: false,
            external: false,
            challenge: false,
            template_id: 55, 
            challenge_id: 0
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleTemplateInterview({ 
                input, 
                user_session: response?.data,
                template_id: template_id,
                challenge_id: challenge_id,
                job_profile_id: job_profile_id,
                timerValue,
                all_user_id: 1959
            });
        }
        setChatInterview([])
        setShowModal(false);
        setChat(true); 
        setLoad(false)
    }

    const chooseChallenge = async(id: any) => {
        setLoad(true)
        const data = {
            job_profile_id: 0,
            all_user_id: 1959,
            template: false,
            generate: false,
            external: false,
            challenge: true,
            template_id: 0, 
            challenge_id: id
        };
        const response = await Api.sessionCreate(data);
        localStorage.setItem("userSession", JSON.stringify(response?.data))
        if(response?.data){  
            timerValue = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            handleChallengeInterview({ 
                input, 
                user_session: response?.data,
                challenge_id: id,
                timerValue,
                job_profile_id: 0,
                all_user_id: 1959
            });
        }
        setChatInterview([])
        setShowModal(false);
        setChat(true); 
        setLoad(false)
    }

    const openTemplateModal = () => {
        setShowTemplateModal(true);
    };

    const openChallengeModal = () => {
        setShowChallengeModal(true);
    };


    const handleTemplateSelection = (templateId: any) => {
        chooseTemplate(templateId);
        setShowTemplateModal(false);
    };

    const handleChallengeSelection = (challengeId: any) => {
        chooseChallenge(challengeId)
        setShowChallengeModal(false)
    }

    useEffect(() =>{
        GetTemplates()
        GetChallenges()
    },[])

    return (
        <>
            <div className="interview-chat-container">
                <div style={{marginTop: '2rem'}}>                
                    <div>

                    <div className="interview-chat-container">
                        <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <Button
                                type="primary"
                                style={{ fontWeight: 'bolder', fontSize: '0.81rem' }}
                                onClick={() => setShowModal(true)}
                            >
                                Start New Session 
                                <span>{loading && <Spin style={{ marginLeft: '5px' }} />}</span>
                            </Button>

                            <AudioUpload/>
                        </div>
                    </div>


                     {/* Modal for session options */}
                        <Modal
                            title="Choose an Option"
                            visible={showModal}
                            onCancel={() => setShowModal(false)}
                            footer={null}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-around', gap:'30px'}}>
                            {loadin && <LoadingSpinner style={{ marginLeft: '5px' }} />}

                                <Card
                                    hoverable
                                    style={{ width: 240, textAlign: 'center' }}
                                    onClick={startSession}
                                >
                                    <h3>New Session</h3>
                                </Card>
                                <Card
                                    hoverable
                                    style={{ width: 240, textAlign: 'center' }}
                                    onClick={openTemplateModal}
                                >
                                    <h3>Existing Question Templates</h3>

                                </Card>
                                <Card
                                    hoverable
                                    style={{ width: 240, textAlign: 'center' }}
                                    onClick={openChallengeModal}
                                >
                                    <h3>Challenge Document</h3>
                                </Card>
                            </div>
                        </Modal>

                        {/* Modal for choosing a template */}
                        <Modal
                            title="Select a Template"
                            visible={showTemplateModal}
                            onCancel={() => setShowTemplateModal(false)}
                            footer={null}
                        >
                           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem' }}>
                                {templates?.template?.map((template: any) =>
                                    template?.data?.map((dataItem: any) => (
                                        <Card
                                            key={dataItem?.id}
                                            hoverable
                                            onClick={() => handleTemplateSelection(dataItem.id)}
                                        >
                                            <h4>{dataItem?.name}</h4>
                                            <p>Type: {dataItem?.type}</p>
                                        </Card>
                                    ))
                                )}
                            </div>

                        </Modal>

                        {/* Modal for choosing a template */}
                        <Modal
                            title="Select a Challenge"
                            visible={showChallengeModal}
                            onCancel={() => setShowChallengeModal(false)}
                            footer={null}
                        >
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem' }}>
                            {challenges?.map((challenge: any) => (
                                <Card
                                key={challenge?.id}
                                hoverable
                                onClick={() => handleChallengeSelection(challenge.id)}
                                >
                                <h4>{challenge.attributes?.Title}</h4>
                                </Card>
                            ))}
                            </div>
                        </Modal>
                        
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
                                            {/* {session?.attributes?.i_persona_observer?.data !== null && (
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
                                            )} */}
                                            <span 
                                                onClick={() => fetchChatHistory(session)}
                                                style={{ 
                                                    color: session?.attributes?.status === 'Incomplete' ? 'rgba(255, 0, 0, 0.63)' : 'rgba(0, 1617, 0, 0.603)' }}>
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