import { useState, useContext, useEffect } from 'react';
import { Button, Typography, Card } from 'antd';
import Api from '../Services/Services';
import { AnalyseDetail, AnalyseChat } from './index';
import { useParams } from 'react-router-dom';
import { ProviderContext } from '../context/context';
import { WechatWorkOutlined } from '@ant-design/icons';
import '../styles/AnalyseChat/chat.css'

const { Text, Title } = Typography;

const AnalyseDoc = () => {
  const { latestsession, latestanalysischat, latestUserData ,latestanalysis, setJobId } = useContext(ProviderContext)
  const { id } = useParams()
  const [open, setOpen] = useState(true);
  const [show, setShow] = useState(true);
  const [analysis, setAnalysis] = useState([]);
  console.log("lady", latestanalysis)

  useEffect(() => {
    setJobId(id)
  })

  const handleAnalyse = async () => {
    const response = await Api.analyseDoc({
      sessionId: latestsession?.sessionId,
      jbId: id,
      cvPath: latestsession?.cvPath,
      jbPath: "jbPath"
    });
    console.log("analysis", response.data);
    setAnalysis(response.data);
    setOpen(false)
  };

  return (
    <div style={{ height: '80vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      {open && (
        <div style={{ textAlign: 'center' }}>
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

      <div style={{ marginTop: '-60px' }}>
        {latestanalysis !== undefined && <AnalyseDetail analysis={latestanalysis} />}
      </div>

      <div className="chat-container" style={{ position: 'absolute', right: '20px', bottom: '30px' }}>
        <div className="chat-relative">
          {show && (
            <AnalyseChat latestanalysischat={latestanalysischat} latestUserData={latestUserData} />
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