import { Button, Card } from "antd"
import {ReloadOutlined } from '@ant-design/icons'

// Redux and Custom Hooks
import { useAppDispatch, useAppSelector } from "../../redux/hooks/hooks";
import { setReloadCount } from "../../redux/slices/leapProfileIdSlice";

//Assets
import { noJobData } from "../../assets";

export type EmptyJobHandlerProps = {
  title: string;
  description: string;
}

export default function NoJobsAvailable({title, description}: EmptyJobHandlerProps) {
  const {reloadCount} = useAppSelector(state => state.leapProfileId)
  const dispatch = useAppDispatch()

  const handleReloadCount = () => {
    dispatch(setReloadCount(reloadCount + 1))
    window.location.reload()
  }

  return (
          <Card title={<></>}>
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
                { reloadCount <3 && <Button onClick={handleReloadCount} 
                    className="mt-32 white-bg light-dark-color"
                    style={{
                      border: "1px solid #D9D9D9",
                    }}
                    icon={<ReloadOutlined/>}>
                    Reload
                  </Button>
                  } 
                  </div>
              </div>
           </div>
          </Card>
  )
}
