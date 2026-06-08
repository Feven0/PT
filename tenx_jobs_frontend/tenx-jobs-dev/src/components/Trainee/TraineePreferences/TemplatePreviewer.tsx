import { Row, Col } from 'antd';
import { pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

type File = {
  name: string;
  value: string; 
};

type DataProps = {
  file: File[];
};

export default function TemplatePreviewer ({ file }: DataProps) {
  const isPdf = (url: string) => /\.pdf$/.test(url);

  if (!file.length || !file[0]?.value || !isPdf(file[0].value)) {
    return <div>No PDF file available.</div>;
  }

  return (
    <Row justify="center" className="mt-16 asset-container">
      <Col span={20} >
        <iframe
          title="Local PDF Preview"
          src={file[0].value}
          style={{ width: '100%', height: '600px' }} 
        />
      </Col>
    </Row>
  );
}

