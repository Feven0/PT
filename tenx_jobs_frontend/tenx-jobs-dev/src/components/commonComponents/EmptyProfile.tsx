import { Button, Card, Col, Modal } from "antd"
import {UploadOutlined } from '@ant-design/icons'
import { useState } from "react";

//Assets
import AddJSONProfile from "../Trainee/Profile/AddJSONProfile";

import { noJobData } from "../../assets";

export type EmptyJobHandlerProps = {
  title: string;
  description: string;
}

export default function EmptyProfile({title, description}: EmptyJobHandlerProps) {
  const [showUploadProfileModal, setShowUploadProfileModal] = useState(false)

  const showModal = () => setShowUploadProfileModal(true)
  const closeModal = () => setShowUploadProfileModal(false)

  return (<>
      <Col span={24} className="no-jobs-available" style={{
        paddingLeft: "0",
        paddingRight: "0"
      }}>
          <Card className="mt-8" title={<></>}>
           <div className="no-job-handler gap-16 content-center">
              <div className="d-flex-center empty-job-inner-container" style={{flexDirection:"column"}}>
                <img src={noJobData} alt ="no-data" className="no-job-img"/>
                <span className="no-job-header mt-32">
                 {title}
                </span>
                  <p className="mt-4 text-center">
                    {description}
                    </p>
                  <div className="flex-center content-center">
                  <Button 
                    onClick={showModal}
                    className="mt-32 white-color dark-orange-bg"
                    style={{
                      border: "1px solid #D9D9D9",
                    }}
                    icon={<UploadOutlined/>}>
                    Upload Profile
                  </Button>
                  
                  </div>
              </div>
           </div>
          </Card>
      </Col>
     <Modal
        title="Upload Profile"
        open={showUploadProfileModal}
        onCancel={closeModal}
        footer={null}
        width={1000}>
          <AddJSONProfile setUploadProfileModal = {setShowUploadProfileModal} />

        </Modal>
        </>
  )
}
