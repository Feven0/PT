import { Row, Table, Typography, Image, Card } from "antd";
import moment from 'moment-timezone';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { useAppSelector } from "../../redux/hooks/hooks";
import { tenAcLogo } from "../../assets"; 
const backendUrl = import.meta.env.VITE_API_BACKEND_URL;

const { Text } = Typography;

export default function PrintEmail() {
    const { printData } = useAppSelector((state) => state.tableExtension);
    const { sender, subject, body, to, cc, sentCount } = printData;

    let logo = tenAcLogo;
    if (logo) {
        logo = `${backendUrl}${logo}`;
    }
    const currentDate = moment().format('MMMM Do YYYY');

    const dataSource = [
        { key: 'sender', label: 'Sender', value: sender },
        { key: 'to', label: 'To', value: to },
        { key: 'cc', label: 'CC', value: cc ? cc : 'None'},
        { key: 'sentCount', label: 'Sent Count', value: sentCount ? sentCount : 0 },
        { key: 'failCount', label: 'Fail Count'},
    ];

    const columns = [
        { title: 'Label', dataIndex: 'label', key: 'label' },
        { title: 'Value', dataIndex: 'value', key: 'value' },
    ];

    return (
        <div style={{ padding: '24px' }}>
        <Row >
            <div style={{display: 'flex', justifyContent:'space-between', width: '100%'}}>
                <Image style={{borderRadius: "0.2rem"}} src={logo} width={30} height={30} preview={false} />
                <Text strong style={{ fontSize: '0.8rem', marginBottom: '24px' }}>{`${subject} - ${currentDate}`}</Text>
            </div>
        </Row>
            <Table
                dataSource={dataSource}
                columns={columns}
                pagination={false}
                bordered
                size="middle"
                showHeader={false}
                rowKey="key"
                style={{ marginBottom: '24px' }}
            />
            <Card title={subject}>
                <ReactMarkdown 
                    rehypePlugins={[rehypeRaw]}
                    remarkPlugins={[remarkGfm]}
                    className='assessment-instruction'>{body}</ReactMarkdown>
            </Card>
        
        </div>
    );
}
