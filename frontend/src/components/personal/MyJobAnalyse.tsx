import {useState} from 'react'
import {MyJobAnalysisDetail} from '../index'

const MyJobAnalyse = ({data}) => {
  const [open, setOpen] = useState('none');
  const handleReadyClick = (component: any) => {
    setOpen(component);
  };

  return (
    <div style={{ width: "100vh"}} className="relative">
     {open === 'none' &&
      <div className='flex flex-col text-center text-3xl font-roboto'>
          <p className='text-gray-600'>Want to see how fit you are for the role?</p>
          <div className='flex justify-center mt-4'>
              <button 
                onClick={() => handleReadyClick('analyse')} 
                className='bg-red-600 text-white p-1 text-xl rounded-full px-10'>
                  {data.length !==0 ? 'Sure': 'Nothing to show, select a cv first!!!'}
              </button>
          </div>
      </div>}

      <div className='my-20'>
            {open === 'analyse' && data !== undefined  && (<MyJobAnalysisDetail analysis={data}/>)}
      </div>
    </div>
  )
}

export default MyJobAnalyse