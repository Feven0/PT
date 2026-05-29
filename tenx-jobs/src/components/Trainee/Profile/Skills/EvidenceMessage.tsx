import { useMutation } from '@apollo/client';
import { SendOutlined , LoadingOutlined} from '@ant-design/icons';
import { Button, Card, Col, Input, Row, Typography, message } from 'antd'
import React, { useCallback, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../../../../redux/hooks/hooks'
import CommentHistory from './CommentHistory'
import { T_EvidenceMessage } from '../../../../types/profileResponse';
import { CREATE_NOTIFICATION } from '../../../../graphql/mutations/createNotification';
import useFetchUserProfile from '../../../../hooks/useFetchUserProfile';
import { appendMessageToEvidence } from "../../../../redux/slices/staffCompetencySlice";
import ServerError from "../../../commonComponents/ServerError";
import useAxiosRequest from "../../../../hooks/useAxiosRequest";
import { getRunStage } from "../../../../utils/getRunStage";
import '../../../../styles/message.css'
import { setE } from "../../../../redux/slices/traineeProfileResponseSlice";
import { updateMessage } from "../../../../redux/slices/evidenceMssagesSlice";

const { Title } = Typography

const run_stage = getRunStage();

export default function EvidenceMessage() {
    const [value, setValue] = useState('');
    const { allUserId, user_profile_id, user_role, trainee_id } = useAppSelector(state => state.leapProfileId)
    const batch = parseInt(useAppSelector((state) => state.user?.batchID));
    const {evidence} = useAppSelector(state => state.traineeCompetencyEvidence)
    const { competencies: skills } = useAppSelector((state) => state.traineeProfileResponse.user_profile)
    const {selectedSkillsUUID} = useAppSelector((state) => state.selectedSkillsUUID)
    const selectedSkills = skills.attributes.filter((skill) => skill.uuid === selectedSkillsUUID)
    const evidenceIndex = selectedSkills[0]?.evidence.findIndex((_ev, index) => index === Number(evidence?.key));
  
    const dispatch = useAppDispatch();
    const [createNotification] = useMutation(CREATE_NOTIFICATION);
    const  { fetchUserProfile } = useFetchUserProfile()
    const { makeRequest, loading, error } = useAxiosRequest();

    const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newContent = e.target.value;
        setValue(newContent); 
    }, [user_role]);
    

    const handleSubmit = async () => {
        if (!value.trim()) {
            message.error("empty");
            return;
        }
        else {
            const evidenceIndex = selectedSkills[0]?.evidence.findIndex((_ev, index) => index === Number(evidence?.key));
            
            const record = { ...evidence }; 
            console.log("this is record", record);
            if(!record) return;
            const timestamp = new Date().toISOString();
            const role = user_role;
            const content = value;
            const newMessage = { timestamp, role, content };

            if (Object.prototype.hasOwnProperty.call(record, 'message') && record.message) {
                record.message = [...record.message];
                record.message.push(newMessage);
                setValue("");

            } else {
                record.message = [newMessage];
                setValue("");
            }
            const updatedEvidence = selectedSkills[0]?.evidence?.map((evidence, index) => {
                if (index.toString() === record.key) {  
                    const updatedData = { ...record };
                    delete updatedData.key;
                    return {
                        ...evidence,
                        ...updatedData,
                    };
                }
                return evidence;
            });
    
            const data = {
                user_role: user_role,
                run_stage: run_stage,
                all_user_id: allUserId,
                user_profile_id: user_profile_id,
                user_profile: [
                    {
                        code: "competencies",
                        uuid: selectedSkills[0]?.uuid,
                        data: {
                            abilities: selectedSkills[0]?.abilities,
                            attitude: selectedSkills[0]?.attitude,
                            description: selectedSkills[0]?.description,
                            display: selectedSkills[0]?.display,
                            evidence: updatedEvidence,
                            knowledge: selectedSkills[0]?.knowledge,
                            name: selectedSkills[0]?.name,
                            others: selectedSkills[0]?.others,
                            rationale: selectedSkills[0]?.rationale,
                            sfia_level: selectedSkills[0]?.sfia_level,
                            sfia_estimation_method: selectedSkills[0]?.sfia_estimation_method,
                            experience_level: selectedSkills[0]?.experience_level,
                            skills: selectedSkills[0]?.skills,
                        }
                    }
                ],
                status: "approved",
            }
            const details = {
                traineeId: trainee_id,
                notificationMessageTeam: `Updated evidence! `,
                notificationMessageTrainee: `Updated evidence!`,
                where: "Competencies",
                traineeLink: `/trainee/trainee-profile`,
                staffLink: `/staff/trainee_details/${allUserId}/${trainee_id}/${user_profile_id}`,
            }
            if (evidenceIndex) {
                dispatch(appendMessageToEvidence({ index: evidenceIndex, newMessage  }));
            }
            dispatch(updateMessage(newMessage))
            dispatch(setE({
                uuid: selectedSkillsUUID,
                evidenceIndex: evidenceIndex,
                message: newMessage
            }));

            await makeRequest({
              url: '/sjob/put-user-profile',
              method: 'POST',
              data: data,
              onSuccess: async () => {
                await createNotification({
                  variables: {
                    sender: allUserId,
                    group: 1,
                    detail: details,
                    origin: 'leap',
                    batch: batch,
                  },
                  onCompleted: (data) => {
                    if (data?.createNotification?.data.id) {
                      message.success('Notification created successfully');
                    } 
                  },
                });
                // window.location.reload();
                message.success('Comment added successfully');
                setValue("");
                fetchUserProfile();
              },
              onError: () => {},
            })
        }
    }

    if (error) return <ServerError />

    return (
        <Col xs={24} lg={22}>
            <Card className='comment-card-container' title={
                <div className="flex-between" style={{ padding: "0 1rem" }}>
                    <Title level={4} style={{ margin: "0" }}>Comments</Title>
                </div>
            }>
                <Col span={24}>
                {selectedSkills[0]?.evidence[evidenceIndex]?.message?.map((msg: T_EvidenceMessage, index: number) => (
                    <CommentHistory
                        key={index}
                        user_role={user_role}
                        role={msg.role}
                        content={msg.content}
                        timestamp={msg.timestamp}
                    />
                ))}
                </Col>
                <Col span={24}>
                    <Row className='d-flex-between'>
                        <Col span={24} className='flex gap-4' style={{ padding: "0.5rem" }}>
                            <div className="reply-input">
                                <Input.TextArea
                                    autoSize={{ minRows: 2, maxRows: 6 }}
                                    value={value}
                                    onChange={handleChange}
                                    className='comment-inputs'
                                    placeholder="Write here"
                                />
                                <div className="flex flex-end gap-4" >
                                    <Button
                                        disabled={!value.trim()}
                                        icon={loading ? <LoadingOutlined /> : <SendOutlined />}
                                        style={{ border: "none", color: "#FF4405" }} className="asset-form-action-buttons"
                                        onClick={handleSubmit}
                                        loading={false}
                                    />
                                </div>
                            </div>
                        </Col>
                    </Row>
                </Col>
            </Card>
        </Col>

    )
}

