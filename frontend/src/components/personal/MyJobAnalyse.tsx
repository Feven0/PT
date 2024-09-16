import {useState} from 'react'
import {MyJobAnalysisDetail, MyAnalyseChat} from './index'
import '../../styles/AnalyseDetail/analysedetail.css'
import { WechatWorkOutlined } from '@ant-design/icons';
import { Button, Typography, Card } from 'antd';

const { Text, Title } = Typography;

const MyJobAnalyse = ({data, chatanalysis}) => {
  const [open, setOpen] = useState('none');
  const [show, setShow] = useState(false)
  const handleReadyClick = (component: any) => {
    setOpen(component);
  };

  return (
    <div>
       {open === 'none' &&
        <div className="analyse-box" style={{ textAlign: 'center', width: '30rem' }} >
          <Text style={{ fontSize: '24px', color: 'gray' }}>
            Want to see how fit you are for the role?
          </Text>
          <div style={{ marginTop: '16px' }}>
            <Button 
              type="primary" 
              onClick={() => handleReadyClick('analyse')} 
              style={{ backgroundColor: '#ff4d4f', borderColor: '#ff4d4f' }}
            >
              Sure
            </Button>
          </div>
        </div>
      }

      <div className=''>
          {open === 'analyse' && data !== undefined  && (<MyJobAnalysisDetail analysis={data}/>)}
      </div>

      {open === 'analyse' && data !== undefined  && (
        <div className="chat-container" style={{ position: 'absolute', right: '20px', bottom: '50px' }}>
          <div className="chat-relative">
            {show && (
              <MyAnalyseChat chat={chatanalysis} />
            )}
            <div className="chat-icon" onClick={() => setShow(!show)} style={{ position: 'absolute', right: '0px' }}>
              <WechatWorkOutlined className='text-white' size={30} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MyJobAnalyse