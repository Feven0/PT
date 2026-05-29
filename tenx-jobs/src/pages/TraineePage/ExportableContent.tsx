import { Button, Col, Divider, Row } from "antd";
import { useRef } from "react";
import { DownloadOutlined } from "@ant-design/icons";
import { MailOutlined, PhoneOutlined, MediumOutlined, ArrowLeftOutlined, LinkedinOutlined, EnvironmentOutlined, WhatsAppOutlined, SkypeOutlined } from "@ant-design/icons";
import ReactToPrint from 'react-to-print';
import { FaGithub } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { FaLink } from "react-icons/fa";
import moment from "moment";
import { FaTelegramPlane } from "react-icons/fa";

import { useAppSelector } from "../../redux/hooks/hooks";
import EmptyJobHandler from "../../components/commonComponents/EmptyJobHandler";

import { calculateDuration } from "../../utils/dateCalculator";
import { capitalizeFirstChar } from "../../utils/commonUtils";
import { T_TraineeLocation } from "../../types/profileResponse";
import '../../styles/slidingCard.css'

export default function ExportableContent() {
  const componentRef = useRef<HTMLDivElement>(null)
  const { awards, basics, competencies, education, languages, projects, volunteer, work_experience } = useAppSelector((state) => state.traineeProfileResponse.user_profile)

  const navigate = useNavigate()

  const sortedEducation = education?.attributes
    ? [...education.attributes].sort((a, b) => {
      return new Date(b.end_date).getTime() - new Date(a.start_date).getTime();
    })
    : [];

  const isLocationValid = (location: T_TraineeLocation) => {
    return Object.values(location).every(
      (value) => typeof value === 'string' && value.trim() !== ''
    );
  };

  const location = basics?.attributes[0]?.location;
  const getIconByName = (name: string) => {
    switch (name.toLowerCase()) {
      case 'main':
        return <PhoneOutlined />;
      case 'whatsapp':
        return <WhatsAppOutlined />;
      case 'telegram':
        return <FaTelegramPlane />;
      case 'skype':
        return <SkypeOutlined />;
      default:
        return <PhoneOutlined />;
    }
  };

  return (
    !(awards && basics && competencies && education && languages && projects && volunteer && work_experience) ?
      <Row gutter={16} justify="center" style={{ marginTop: "3rem" }}>
        <Col xs={24} lg={20} xxl={16} className="mobile-skills-header">
          <EmptyJobHandler title="No file to export" description="You currently don't have a profile to export" />
        </Col>
      </Row> :
      <Row gutter={16} justify="center" style={{ marginTop: "3rem" }}>
        <Col xs={24} lg={20} xxl={16} className="mobile-skills-header printable-mobile-skills-header">
          <div className="flex-between" style={{
            borderBottom: "1px solid #f0f0f0",
            alignItems: "center",
            padding: "0 1rem"
          }}>
            <div className="flex-center gap-8">
              <ArrowLeftOutlined className="font-20" onClick={() =>
                navigate('/trainee/trainee-profile')
              } />
              <h2>Profile Preview</h2>
            </div>
            <ReactToPrint
              trigger={() => <DownloadOutlined className="font-24 edit-outlined-icon dark-orange-color" />}
              content={() => componentRef.current}
              documentTitle={"Profile"}
            />
          </div>
          <div ref={componentRef}>
            <div className="flex gap-32 p-16 print-document-component">
              <div className="print-document-first-content">
                <Row gutter={[16, 32]}>
                  <Col span={24}>
                    <div className="flex-center gap-8" style={{ padding: "0.5rem 0" }}>
                      <div className="flex" style={{ flexDirection: "column" }}>
                        <span className="user-name-text">{basics?.attributes[0]?.full_name}</span>
                        <p className="user-name-sub-text">{basics?.attributes[0]?.role}</p>
                      </div>
                    </div>
                    <div>
                      {basics?.attributes[0]?.email && (
                        <span className="flex gap-8">
                          <MailOutlined /> <p>{basics?.attributes[0]?.email}</p>
                        </span>
                      )}
                      {basics?.attributes[0]?.phone.length > 0 && (
                        <div className="mt-8">
                          {basics.attributes[0].phone.map((phoneEntry, index) => (
                            <span key={index} className="flex-center gap-8">
                              {getIconByName(phoneEntry.name)}
                              <p>{phoneEntry.value}</p>
                            </span>
                          ))}
                        </div>
                      )}
                      {basics?.attributes[0]?.media &&
                        basics?.attributes[0]?.media.map((me) => {
                          let icon;
                          switch (me.name.toLowerCase()) {
                            case 'linkedin':
                              icon = <LinkedinOutlined />;
                              break;
                            case 'github':
                              icon = <FaGithub />;
                              break;
                            case 'medium':
                              icon = <MediumOutlined />;
                              break;
                            default:
                              icon = <FaLink />;
                          }

                          return (
                            <span className="flex gap-8 mt-8" key={me.link}>
                              {icon}
                              <a href={me.link} target="_blank" rel="noopener noreferrer">
                                {me.name}
                              </a>
                            </span>
                          );
                        })}
                      {location && isLocationValid(location) && (
                        <span className="flex gap-8 mt-8">
                          <EnvironmentOutlined /><p>{location.address}</p>
                        </span>
                      )}
                    </div>
                  </Col>
                  {sortedEducation?.length > 0 && <Col span={24}style={{borderTop:"1px solid whitesmoke"}}>
                    <h3 className="mb-8 mt-8">Education</h3>
                    {education ?
                      sortedEducation?.map((edu, index) => (
                        <div className="flex gap-16" key={index} style={{
                          marginBottom: `${index !== sortedEducation.length - 1 ? '1rem' : '0'}`
                        }}>
                          <div className="full-width">
                            <div className="d-flex-between">
                              <h4>{edu.institution_name}</h4>
                            </div>
                            <div>
                              <p>{edu.study_area}</p>
                              <p>{edu.study_type}</p>
                              <div className="flex-center gap-8">
                                {edu.country && <span>{edu.country}</span>}
                              </div>
                              {edu.score && <span>Score - {edu.score}</span>}
                            </div>
                            {moment(edu.start_date, 'YYYY-MM-DD', true).isValid() &&
                              (!edu.end_date || moment(edu.end_date, 'YYYY-MM-DD', true).isValid()) && (
                                <div className="flex-center gap-8">
                                  {moment(edu.start_date).format('DD MMM YYYY')} - {edu.end_date ? moment(edu.end_date).format('DD MMM YYYY') : 'Present'}
                                </div>
                              )}
                            <br /><span className="mt-16">
                              {
                                edu.institution_url && <a href={edu.institution_url} target="_blank" rel="noreferrer">
                                  <Button icon={<FaLink />} className="white-bg dark-orange-color mt-8">{edu.institution_url}</Button>
                                </a>
                              }
                            </span>
                            {/* <p>{edu?.remark} </p> */}
                          </div>
                        </div>
                      )) : null
                    }
                  </Col>}
                  <Col span={24} style={{borderTop:"1px solid whitesmoke"}}>
                    {awards?.attributes?.length > 0 && <h3 className="mb-8 mt-8">Awards</h3>}
                    {awards?.attributes?.length > 0 ? (
                      awards?.attributes?.map((awa, index) => (
                        <div className="flex gap-16" key={index} style={{
                          marginBottom: `${index !== awards?.attributes.length - 1 ? '1rem' : '0'}`
                        }}>
                          <div className="full-width">
                            <div className="d-flex-between">
                              <h4>{capitalizeFirstChar(awa.title)}</h4>
                            </div>
                            <div>
                              <p>{awa.awarder}</p>
                              {moment(awa.date, 'YYYY-MM-DD', true).isValid() && (
                                <div className="flex-center gap-8">
                                  {moment(awa.date).format('DD MMM YYYY')}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : null}
                  </Col>
                  <Col span={24} style={{borderTop:"1px solid whitesmoke"}}>
                    {languages?.attributes?.length > 0 && (
                      <>
                        <h3 className="mb-8 mt-8">Languages</h3>
                      </>
                    )}
                    {
                      languages && languages?.attributes?.length > 0 ? (
                        languages?.attributes?.map((lang, index) => (
                          <div className="flex gap-16" key={index} style={{
                            marginBottom: `${index !== languages?.attributes.length - 1 ? '1rem' : '0'}`
                          }}>
                            <div className="full-width">
                              <div className="d-flex-between">
                                <h4>{capitalizeFirstChar(lang.language)}</h4>
                              </div>
                              <div>
                                <p>{lang.fluency}</p>
                              </div>
                            </div>
                          </div>

                        ))
                      ) : null
                    }
                  </Col>
                </Row>
              </div>
              <div className="print-document-second-content">
                <p>{basics?.attributes[0]?.personal_statement}</p>
                <Divider style={{ margin: "1rem 0" }} />
                <h3 className="mb-16">Competencies</h3>
                <Row gutter={8} className="flex" style={{ rowGap: "8px" }}>
                  {competencies?.attributes?.map((skill, index) => (
                    <Col span={6} key={index}>
                      <span>{skill.display}</span>
                    </Col>
                  ))}
                </Row>
                {work_experience?.attributes?.length > 0 && (
                  <>
                    <Divider style={{ margin: "1rem 0" }} />
                    <h3 className="mb-16">Work Experience</h3>
                  </>
                )}
                {
                  work_experience ?
                    work_experience?.attributes?.map((exp, index) => (
                      <div className="flex gap-16" key={index}
                        style={{
                          marginBottom: `${index !== work_experience.attributes.length - 1 ? '1rem' : '0'}`
                        }}
                      >
                        <div className="full-width">
                          <div className="d-flex-between">
                            <h4 className="mb-8">{capitalizeFirstChar(exp.role)}</h4>
                          </div>
                          <div>
                            <p>{exp.company}</p>
                            <p>{exp.location}</p>
                            {moment(exp.start_date, 'YYYY-MM-DD', true).isValid() &&
                              (!exp.end_date || moment(exp.end_date, 'YYYY-MM-DD', true).isValid()) && (
                                <div className="flex-center gap-8">
                                  {moment(exp.start_date).format('DD MMM YYYY')} - {exp.end_date ? moment(exp.end_date).format('DD MMM YYYY') : 'Present'}
                                  <p>{" • "} {calculateDuration(exp.start_date, exp.end_date)}</p>
                                </div>
                              )}
                          </div>
                          <p>{exp.summary}</p>
                        </div>
                      </div>
                    )) : null
                }
                {projects?.attributes?.length > 0 && (
                  <>
                    <Divider style={{ margin: "1rem 0" }} />
                    <h3 className="mb-16 mt-16">Projects</h3>
                  </>
                )}
                {projects ?
                  projects?.attributes?.map((attr, attrIndex) => {
                    return (
                      <div className="flex gap-16" key={attrIndex}
                      style={{
                        marginBottom: `${attrIndex !== projects.attributes.length - 1 ? '1rem' : '0'}`
                      }}>
                      <div className="full-width">
                        <div className="d-flex-between">
                          <h4 className="mb-8" style={{ opacity: 0.8 }}>{attr.title}</h4>
                        </div>
                        {attr.start_date && attr.start_date !== 'None' && attr.end_date && attr.end_date !== 'None' && (
                          <div className="flex gap-8">
                            {moment(attr.start_date, 'YYYY-MM-DD', true).isValid() &&
                              (!attr.end_date || moment(attr.end_date, 'YYYY-MM-DD', true).isValid()) && (
                                <div className="flex-center gap-8">
                                  {moment(attr.start_date).format('DD MMM YYYY')} - {attr.end_date ? moment(attr.end_date).format('DD MMM YYYY') : 'Present'}
                                  <p>{" • "} {calculateDuration(attr.start_date, attr.end_date)}</p>
                                </div>
                              )}
                          </div>
                        )}
                        <p>{attr.summary}</p>
                        { (attr.url!=='None')  && <p>
                          <a href={attr.url} target="_blank" rel="noopener noreferrer">
                            {attr.url}
                          </a>
                        </p>
                        }
                      </div>
                    </div>
                    )
                    
                }) : null
                }
                {volunteer?.attributes?.length > 0 && (
                  <>
                    <Divider style={{ margin: "1rem 0" }} />
                    <h3 className="mt-16 mb-8">Volunteer Works</h3>
                  </>
                )}
                {
                  volunteer ? (
                    volunteer?.attributes?.map((vol, index) => (
                      <div className="flex gap-16" key={index} style={
                        {
                          marginBottom: `${index !== volunteer.attributes.length - 1 ? '1rem' : '0'}`
                        }
                      }>
                        <div className="full-width">
                          <div className="d-flex-between">
                            <h4>{capitalizeFirstChar(vol.position)}</h4>
                          </div>
                          <div>
                            <p>{vol.organization}</p>
                            {moment(vol.start_date, 'YYYY-MM-DD', true).isValid() &&
                              (!vol.end_date || moment(vol.end_date, 'YYYY-MM-DD', true).isValid()) && (
                                <div className="flex-center gap-8">
                                  {moment(vol.start_date).format('DD MMM YYYY')} - {vol.end_date ? moment(vol.end_date).format('DD MMM YYYY') : 'Present'}
                                  <p>{" • "} {calculateDuration(vol.start_date, vol.end_date)}</p>
                                </div>
                              )}
                          </div>
                          <p>{vol?.summary}</p>
                        </div>
                      </div>
                    ))
                  ) : null
                }
              </div>
            </div>
          </div>
        </Col>
      </Row>
  )
}
