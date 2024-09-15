import { useState, useEffect, useContext } from 'react';
import fade from '../../assets/fade-circles.svg' 
import useMiddleSocket from '../../hooks/useMiddleSocket';
import { ProviderContext } from '../../context/context'
import ReactMarkdown from 'react-markdown';
import { useParams } from 'react-router-dom';
import Api from '../../Services/Services';

const MyAnalyseChat = ({chat}) => {
    const { loading, analysis, latestAnalyseResponse, handleAnalyse } = useMiddleSocket();
    const { latestanalysis, session, setStart } = useContext(ProviderContext)
    const [input, setInput] = useState("")
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
  
    const onSendMessage = async () => {
      const filteredData = filterBySessionId(sessionId);
      const cv_path = filteredData[0].cvPath
      const latestUserInfo = await filterBySessionIdAndJobId()
      // console.log("cancering...", cv_path, latestUserInfo)
      handleAnalyse({input, cv_path, latestUserInfo})
      setInput('');
    };
    const handler = (event: any) => {
        if (event.keyCode === 13) {  
          onSendMessage()
        }
    };

    const MarkdownContent = ({ content }: { content: string }) => {
      const formattedContent = content.replace(/---/g, ' ');
      return (
        <div className="markdown-content text-justify p-2 px-6 font-lato leading-loose">
          <ReactMarkdown>{formattedContent}</ReactMarkdown>
        </div>
      );
    };

  return (
    <div>
         <div className='shadow-xl p-3 border mb-1 rounded overflow-auto font-roboto h-[38rem] w-[30rem]'>
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
                          {message.role === "user" && (
                            <div className='mt-1 mb-3'>
                              <div className="">
                                <div className="text-gray-900 rounded p-2 inline-block">
                                  {message?.response}
                                </div>
                              </div>
                            </div>
                          )}
                          {message.role === "assistant" && (
                            <div className="mx-2">
                              {!Array.isArray(message?.response) ? (
                                <div className="flex gap-1">
                                  <p className="text-justify inline-block text-gray-500 bg-gray-50 p-3 font-roboto mb-3">
                                    <MarkdownContent content={message?.response} />
                                  </p>
                                </div>
                              ) : null}
                            </div>
                          )}
                        </div>
                    ))}
                </div>)}
                {analysis?.map((message: any, index: any) => (
                    <div key={index}>
                      {message.role == "user" && (
                        <div className='mt-1 mb-3'>
                            <div className="">
                                <div className="text-gray-900 rounded p-2 inline-block">
                                {message?.response}
                                </div>
                            </div>
                        </div>
                      )}
                      {message.role == "assistant" && (
                        <div className="mx-2">
                            {!Array.isArray(message?.response) ? (
                            <div className="flex gap-1">
                                <p className="text-justify inline-block text-gray-500 bg-gray-50 p-3 font-roboto mb-3">
                                <MarkdownContent content={message?.response} />
                                </p>
                            </div>
                            ):null}
                        </div>   
                      )}                 
                    </div>
                ))}
                {loading && (<img src={fade} alt="" className='h-10' />)} 
            </div>

          
            <div className='border rounded-lg w-[30rem]'>        
                <textarea          
                    className="w-[100%] focus:outline-none focus:ring-0 focus:border-transparent text-sm py-2 rounded-lg p-1"    
                    value={input}
                    placeholder="follow up question?"
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => handler(e)}
                />
            </div>
    </div>
  )
}

export default MyAnalyseChat