import {useState, useEffect} from 'react'
import '../../styles/chatbox.css'
import { MyInterviewChat } from '../index'
import useMiddleSocket from '../../hooks/useMiddleSocket';

const MyInterview = ({chat}) => {
  const { handleInterview, interview, loading,  latestInterviewResponse } = useMiddleSocket();
  const [open, setOpen] = useState('none');
  const handleReadyClick = (component: any) => {
    setOpen(component);
  };

  return (
    <div style={{ width: '100vh' }} className="relative ">
     {open === 'none' &&
      <div className='flex flex-col text-center text-3xl font-roboto'>
          <p className='text-gray-600'>Want to get ready for the job?</p>
          <small className='text-gray-400 text-lg'>how about having an interview?</small>

          <div className='flex justify-center mt-4'>
              <button 
                onClick={() => handleReadyClick('ready')} 
                className='bg-red-600 text-white p-2 text-xl rounded-full px-10'>
                  Sure
              </button>
          </div>
      </div>}

      <div className='flex justify-center items-center'>
            {open === 'ready' &&<MyInterviewChat chat={chat}/>}
      </div>
    </div>
  )
}

export default MyInterview