import { Card, Col, Collapse, Row } from "antd";
import { CollapseProps } from "antd/lib";

//Components
import Bio from "./Bio";
import Experience from "./Experience";
import EducationProf from "./EducationProf";
import VolunteerWork from "./VolunteerWork";
import Projects from "./Projects";
import TraineeAwards from "./TraineeAwards";
import TraineeCertificates from "./TraineeCertificates";
import TraineeLanguages from "./TraineeLanguages";
import NoFile from "../../commonComponents/NoFile";
import Achievements from "./Achievements";
import Publications from "./Publications";
import References from "./References";

import { T_TraineeAward, T_TraineeBasics, T_TraineeCertificates, T_TraineeEducation, T_TraineeLanguages, T_TraineeProjects, T_TraineeVolunteer, T_TraineeWorkExperience } from "../../../types/profileResponse";
import '../../../styles/staff.css'

type TraineeProfileDetailProps = {
  bio:T_TraineeBasics;
  projects : T_TraineeProjects
  education : T_TraineeEducation
  experience: T_TraineeWorkExperience
  volunteer: T_TraineeVolunteer
  awards : T_TraineeAward
  certificates : T_TraineeCertificates
  languages: T_TraineeLanguages
}

export default function TraineeProfileDetail({
  bio,
  projects,
  education,
  experience,
  volunteer,
  awards,
  certificates,
  languages
}: TraineeProfileDetailProps) {
 
  if(!education && !bio && !projects && !experience && !volunteer && !awards && !certificates && !languages) {
    return <NoFile/>
  }

  const items: CollapseProps['items'] = [
    {
      key: '1',
      label: 'Volunteer Work',
      children: <VolunteerWork volunteer={volunteer} />,
    },
    {
      key: '2',
      label: 'Awards',
      children: <TraineeAwards awards={awards} />,
    },
    {
      key: '3',
      label: 'Certificates',
      children: <TraineeCertificates certificates={certificates}  />,
    },
    {
      key: '4',
      label: 'Languages',
      children: <TraineeLanguages languages={languages} />,
    },
    {
      key: '5',
      label: 'Publications',
      children: <Publications/>,
    },
    {
      key: '6',
      label: 'Achievements',
      children: <Achievements/>,
    },
    {
      key: '7',
      label: 'References',
      children: <References/>,
    }
  ]

  return (
    <Row gutter={16} justify="center" className="trainee-detail-container-row">
       <Card className="full-width bio-card bio-staff-card"
        title={
          <div className="d-flex-between mr-24">
              <h3>Bio</h3>
            </div>
        }
       >
        <Bio bio={bio}/>
      </Card>
      
        {/* Experience */}
        <Col span={24}>
          <Row gutter={16}>
            <Card className="full-width trainee-details-prof-card"
              title={
                <div className="d-flex-between">
                <h3>Work Experience</h3>
              </div>
              }
            >
            <Experience userExp={experience}/>
            </Card>
          </Row>
        </Col>

        {/* Education */}
        <Col span={24}>
          <Row gutter={16}>
            <Card className="full-width trainee-details-prof-card"
              title={
                <div className="d-flex-between">
                  <h3>Education</h3>
                </div>
              }
            >
            <EducationProf userEdu={education}/>
          </Card>
          </Row>
         </Col>

          {/* Projects */}
          <Col span={24}>
            <Row gutter={16}>
              <Card className="full-width trainee-details-prof-card"
                title={
                  <div className="d-flex-between">
                    <h3>Projects</h3>
                  </div>
                }
              >
                <Projects projects={projects} />
            </Card>
            </Row>
         </Col>
         <Col span={24} className="mt-16 other-details-container other-details-title" >
            <div className="full-width white-bg br-8 p-16">
              <h3>Miscellaneous</h3>
            </div>
         </Col>
         <Col span={24} className="other-details-container">
          <Collapse  
              style={{background:"#fff"}} 
              className="other-details-collapse"
              items={items} 
              defaultActiveKey={['1']} />
        </Col>
    </Row>
  )
}

