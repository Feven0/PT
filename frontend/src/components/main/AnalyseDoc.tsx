import { useState, useContext, useEffect } from 'react';
import { Button, Typography, Card } from 'antd';
import Api from '../../Services/Services';
import { AnalyseDetail, AnalyseChat } from './index';
import { useParams } from 'react-router-dom';
import { ProviderContext } from '../../context/context';
import { WechatWorkOutlined } from '@ant-design/icons';
import jobs from '../../assets/mock-data/job_profiles.json';
import users from '../../assets/mock-data/user_profiles.json';
import '../../styles/AnalyseChat/chat.css'

const { Text, Title } = Typography;

const AnalyseDoc = () => {
  const { latestsession, latestanalysischat, latestUserData ,latestanalysis, setJobId } = useContext(ProviderContext)
  const { userId, jobId } = useParams()
  const [open, setOpen] = useState(true);
  const [show, setShow] = useState(false);
  const [analysis, setAnalysis] = useState([]);
  
  const filteredJobMatch = jobs.filter(match => match.job_profile_id === parseInt(jobId as any));
  const filteredUserMatch = users.filter(match => match.user_profile_id === parseInt(userId as any));

  useEffect(() => {
    setJobId(jobId)
  })

  const handleAnalyse = async () => {
    const data = {
      sessionId: latestsession?.sessionId || '2ad1d065-c879-4efa-a86b-eabbdc19c146',
      jbId: jobId,
      // cvPath: latestsession?.cvPath,
      cvPath: filteredUserMatch[0],
      jbPath: filteredJobMatch[0]
    }
    
    const response = await Api.analyseDoc(data);
    console.log("analysis", response.data);
    setAnalysis(response.data);
    setOpen(false)
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      {open && (
        <div style={{ textAlign: 'center', width: '30rem' }} >
          <Text style={{ fontSize: '24px', color: 'gray' }}>
            Want to see how fit you are for the role?
          </Text>
          <div style={{ marginTop: '16px' }}>
            <Button 
              type="primary" 
              onClick={handleAnalyse} 
              style={{ backgroundColor: '#ff4d4f', borderColor: '#ff4d4f' }}
            >
              Sure
            </Button>
          </div>
        </div>
      )}

      <div 
      // style={{ marginTop: '-60px' }}
      >
        {latestanalysis !== undefined && 
        <div >
            <AnalyseDetail realtimeanalysis={analysis} dblatestanalysis={latestanalysis} />
        </div>
        }
      </div>

      <div className="chat-container" style={{ position: 'absolute', right: '20px', bottom: '0px' }}>
        <div className="chat-relative">
          {show && (
            <AnalyseChat 
            latestanalysischat={latestanalysischat} 
            latestUserData={latestUserData} 
            profile = {filteredUserMatch[0]}
            job= {filteredJobMatch[0]} 
            />
          )}
          <div className="chat-icon" onClick={() => setShow(!show)} style={{ position: 'absolute', right: '0px' }}>
            <WechatWorkOutlined className='text-white' size={30} />
          </div>
        </div>
      </div>

    </div>
  );
};

export default AnalyseDoc;