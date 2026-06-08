import { Col, Tooltip } from 'antd';
import { StarFilled, HeartFilled} from '@ant-design/icons'; 
import { Stats } from "../../redux/slices/userStatsSlice";

import { leap } from "../../assets";

export type TStats = {
  stats: Stats
  source?: string
};

export default function TraineeStats({ stats, source }: TStats) {
  const tooltip = `Number of credits used today out of ${stats?.max_credit}. You have ${stats?.max_credit} daily credits to generate CVs for jobs with an 90%+ match and super like.`
  return (
    <Col xs={24} lg={source && source==='jobs' ? 16: 20} className="mt-16">
      <div className="d-flex-center br-4 p-8">
        <div className="flex-end gap-16">
            <>
              <Tooltip title={tooltip}>
              <div className="d-flex-center gap-8 p-4 pl-8 pr-8 br-4">
                <img src={leap} alt="matchIcon" style={{
                  opacity: 0.8
                }} width={18} />
                <span className="job-header-texts opacity-7">Leaped</span>
                  <span className="job-header-sub-texts">{stats?.credit_used ? stats?.credit_used : 0}/{stats?.max_credit ? stats?.max_credit : 15}</span>
              </div>
              </Tooltip>
              {" •"}
            </>
          <Tooltip title="Shows the number of jobs that you have Superliked.">
          <div className="d-flex-center gap-8 p-4 pl-8 pr-8 br-4">
            <HeartFilled  style={{
                  opacity: 0.8
                }}/>
            <span className="black-color job-header-texts opacity-7">Super Liked</span>
            <div className="d-flex-center black-color job-header-sub-texts">{stats?.superlike ? stats?.superlike : 0}</div>
          </div>
          </Tooltip>
          {" •"}
          <Tooltip title="Shows the number of jobs that you have Liked.">
          <div className="d-flex-center gap-8 p-4 pl-8 pr-8 br-4">
            <StarFilled className="font-16" style={{
                  opacity: 0.8
                }} />
            <span className="black-color job-header-texts opacity-7">Liked</span>
            <div className="d-flex-center black-color job-header-sub-texts">{stats?.like ? stats?.like : 0}</div>
          </div>
          </Tooltip>
        </div>
      </div>
    </Col>
  );
}
