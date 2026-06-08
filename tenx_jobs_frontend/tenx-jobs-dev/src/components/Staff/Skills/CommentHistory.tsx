import { useMemo } from 'react'
import { Col, Row, Typography } from 'antd';
import dayjs from 'dayjs';

type CommentHistoryProps = any

const { Paragraph } = Typography
export default function CommentHistory({ user_role, role, content, timestamp }: CommentHistoryProps) {
    const time = useMemo(() => dayjs(timestamp).format('h:mm A'), [timestamp]);
    const containerStyle = {
        padding: "0.5rem"
    };

    const spaceStyle = {
        padding: "0.6rem 0.8rem",
        borderRadius: "0.5rem 0 0.5rem 0.5rem",
        backgroundColor: user_role === role ? "#FFFFFF" : "#0000000F",
        border: user_role === role ? "1px solid #0000000F" : "1px solid #0000000A",
        color: "#000000E0",
        alignItems: "baseline",
        boxShadow: "0px 0.2px 5px 0px rgba(0, 0, 0, 0.08)"
    };


    return (
        <Row style={containerStyle}>
            <Col span={24}>
                <div className={`gap-8 ${user_role === role ? 'flex flex-end' : ''}`}>
                    <div
                        className="flex"
                        style={spaceStyle}
                    >
                        <>
                            <Paragraph
                                style={{ margin: 0 }}
                            >
                                {content}
                            </Paragraph>
                            <div style={{ marginLeft: "0.5rem", width: "5vw" }}>
                                <sub style={{ fontSize: "0.5rem" }}>
                                    {time}
                                </sub>
                            </div>
                        </>
                    </div>
                </div>
            </Col>
        </Row>
    )
}
