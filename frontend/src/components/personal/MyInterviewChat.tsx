import { useState, useEffect, useContext } from 'react';
import fade from '../../assets/fade-circles.svg' 
import useMiddleSocket from '../../hooks/useMiddleSocket';
import '../../styles/chatbox.css'
import hr from '../../assets/hr.jpg'
import profile from '../../assets/profile.png'
import { IoMdVideocam } from "react-icons/io";
import ReactMarkdown from 'react-markdown';
import { AudioRecorder } from '..';
import { ProviderContext } from '../../context/context';
import { useParams } from 'react-router-dom';
import Api from '../../Services/Services';

const InterviewChat = ({chat}) => {
    const { handleInterview, interview, loading,  latestInterviewResponse } = useMiddleSocket();
    const {latestanalysis, latestinterviewchat, latestUserData, session, setStart} = useContext(ProviderContext)
    const [counter, setCounter] =useState(0)
    const [input, setInput] = useState("")
    const [dataFromAudio, setDataFromAudio] = useState(false);
    const [initialChatInterview, setInitialChatInterview] = useState<any>(latestinterviewchat);
    const [view, setShow] = useState(false)
    const {jbId, sessionId} = useParams()

    useEffect(() => {
      setStart(false)
    })

    const filterBySessionId = (sessionId) => {
      return session.filter(item => item.sessionId === sessionId);
    };
      
    const filterBySessionIdAndJobId = async() => {
      const datas = {sessionId: sessionId, jbId: jbId}
      const response = await Api.fetchSessionJob(datas)
      // console.log("responding...", response.data.latest_user_data)
      const value = response.data.latest_user_data
      return value
    };

    const onSendMessage = async() => {
      const filteredData = filterBySessionId(sessionId);
      const cv_path = filteredData[0].cvPath
      const latestUserInfo = await filterBySessionIdAndJobId()

      handleInterview({ input, interview, cv_path, latestUserInfo, counter })
      setInput('');
      if (counter < 5) {
        setCounter(counter + 1);
      } else {
        setCounter(0);
      } 
    };
  
    const handler = (event: any) => {
        if (event.keyCode === 13) {  
          onSendMessage()
        }
    };

    const handleDataFromAudio = (audioTranscript: any) => {
        setInput((prevInput) => prevInput + ' ' + audioTranscript);
        // console.log("audio", audioTranscript)
    };

    function handleDataAudio(data: bool) {
      setDataFromAudio(data);
    }

   
    console.log("interview", interview)

    const MarkdownContent = ({ content }: { content: string }) => {
      const formattedContent = content.replace(/---/g, ' ');
      return (
        <div className="markdown-content text-justify p-2 px-6 font-lato leading-loose">
          <ReactMarkdown>{formattedContent}</ReactMarkdown>
        </div>
      );
    };

  return (
    <>
      <div className='w-[50rem]'>
            <div className='shadow-xl p-3 border mb-1 rounded overflow-auto h-[32rem] mt-12'>
               <div className='flex justify-center mb-10'>
                  <button 
                    onClick={() => setShow(!view)}
                    className='text-gray-50 font-bold font-roboto mb-2 fixed bg-red-400 rounded-full px-3'>
                      {!view? 'Previous' : 'Hide'}
                  </button>
                </div>

                {view && (<div>
                  {chat?.map((message: any, index: any) => (
                      <div key={index}>
                        {message.role == "candidate" && (
                          <div className='mt-1 mb-5'>
                              <div className="my-2 flex gap-1">
                                  <img src={profile} alt="" className='h-10 w-10 rounded-full' />
                                  <p className="text-justify text-gray-700 font-roboto">{message?.response}</p>
                                </div>
                          </div>
                        )}

                        {message.role == "assistant" && (
                          <div className="">
                              <div className="bg-white p-3 rounded max-w-fit flex gap-1">
                                  <img src={hr} alt="" className='h-10 w-10 rounded-full' />
                                  <div className={`text-gray-500 ${index === 0 ? 'bg-red-50' : ''}`}>
                                    <MarkdownContent content={message?.response}/>
                                  </div>
                              </div>
                          </div>
                        )}                   
                      </div>
                  ))}
                </div>)}

                  {interview?.map((message: any, index: any) => (
                      <div key={index}>
                        {message.role == "candidate" && (
                          <div className='mt-1 mb-5'>
                              <div className="my-2 flex gap-1">
                                  <img src={profile} alt="" className='h-10 w-10 rounded-full' />
                                  <p className="text-justify text-gray-700 font-roboto">{message?.response}</p>
                                </div>
                          </div>
                        )}

                        {message.role == "assistant" && (
                          <div className="">
                              <div className="bg-white p-3 rounded max-w-fit flex gap-1">
                                  <img src={hr} alt="" className='h-10 w-10 rounded-full' />
                                  <div className={`text-gray-500 ${index === 0 ? 'bg-red-50' : ''}`}>
                                    <MarkdownContent content={message?.response}/>
                                  </div>
                              </div>
                          </div>
                        )}                   
                      </div>
                  ))}
                  {loading? <img src={fade} alt="" className='h-10' />:null} 
            </div>

            
            <div className='border rounded-lg'>        
                <textarea            
                    className="w-[100%] focus:outline-none focus:ring-0 focus:border-transparent text-sm py-2 rounded-lg p-1"    
                    value={input}
                    placeholder="Put your answer here"
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => handler(e)}
                />
                <div className='flex justify-between gap-1 p-2'>
                  <div className='flex gap-1'>
                    <IoMdVideocam size={30} className='text-[gray]'/>
                    <AudioRecorder sendDataParent={handleDataAudio} sendDataToParent={handleDataFromAudio} />
                    {dataFromAudio? <img src={fade} alt="" className='h-10' />:null} 
                  </div>
                </div>
            </div>
      </div>
    </>
  )
}

export default InterviewChat