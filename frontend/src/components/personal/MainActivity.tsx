import { useEffect, useState, useContext } from 'react';
import {Job, MyInterview, MyAnalyseChat, MyJobAnalyse} from "../index"
import { IoChatbubbleEllipses } from "react-icons/io5";
import { Link, useParams } from 'react-router-dom';
import Api from '../../Services/Services';
import { ProviderContext } from '../../context/context';

const MainActivity = () => {
    const { latestanalysis, userData, latestUserData } = useContext(ProviderContext);
    const [refresh, setRefresh] = useState(0);
    const [activeComponent, setActiveComponent] = useState('A');
    const [show, setShow] = useState(false)
    const [chatanalysis, setChatAnalysis] = useState([])
    const [chatinterview, setChatInterview] = useState([])
    const [analysis, setAnalysis] = useState([])

    let { jbId, sessionId } = useParams();

    const dataFetch = async() => {
        const data = {
            sessionId: sessionId,
            jbId: jbId            
        }
        // console.log("get h", analysis !== undefined)
        const response = await Api.fetchSessionJob(data)
        // console.log("get hold", response.data.latest_analysis)
        setChatAnalysis(response.data.latest_analysischat)
        setChatInterview(response.data.latest_interviewchat)
        setAnalysis(response.data.latest_analysis)
    }

    useEffect(() => {
        dataFetch()
        const intervalId = setInterval(() => {
        setRefresh((prev) => prev + 1); 
        }, 10000);
        return () => clearInterval(intervalId);
    }, [refresh, jbId, sessionId]); 

    const handleMenuClick = (component: any) => {
        setActiveComponent(component);
    };

  return (
    <div className='mx-12'>
        <div className='flex '>
            <nav className='bg-[red] w-44 py-3 rounded gap-3 mx-20 mt-10 max-h-52 flex flex-col'>
                <button onClick={() => handleMenuClick('A')} 
            className={`mx-1 p-2 flex justify-start  ${activeComponent === 'A' ? 'bg-white' : ''} text-gray-900  rounded px-1`}>
                    Job
                </button>

                <button onClick={() => handleMenuClick('B')} 
                className={`mx-1 p-2 flex justify-start ${activeComponent === 'B' ? 'bg-white' : ''} text-gray-900 rounded px-1`}>
                    Analysis
                </button>

                <button onClick={() => handleMenuClick('C')} 
                className={`mx-1 p-2 flex justify-start  ${activeComponent === 'C' ? 'bg-white' : ''} text-gray-900 rounded px-1`}>
                    Interview
                </button>

                <Link to="/profile_detail">
                    <button className='mx-1 p-2 flex justify-start text-gray-900 rounded px-1'>
                        Back
                    </button>
                </Link>

            </nav>

            <div className='mx-20'>
                {activeComponent === 'A' && <Job />}
                {activeComponent === 'B' && <MyJobAnalyse data={analysis !== undefined && (analysis)} />}
                {activeComponent === 'C' && <MyInterview chat={chatinterview} />}
            </div>
        </div>

        <div className='absolute inline-block right-0 bottom-0 mb-14 mr-5 bg-white'>
            {activeComponent === 'B' && 
                <div className='relative h-full'> 
                    {show ? <MyAnalyseChat chat={chatanalysis}/> : null}
                
                    <div className='absolute right-0'>
                        <div 
                            className='my-2 bg-red-500 cursor-pointer rounded-full h-10 w-10 flex justify-center items-center'
                            onClick={() => setShow(!show)}
                        > 
                            <IoChatbubbleEllipses 
                                className='text-white' 
                                size={30}
                            />
                        </div> 
                    </div>
                </div>    
            }         
        </div>
    </div>
  )
}

export default MainActivity