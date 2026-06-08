import { Button, Col, Divider, Row } from "antd";
import { pdfjs } from 'react-pdf';

import EmptyJobHandler from "../../commonComponents/EmptyJobHandler";
import '../../../styles/slidingCard.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

export type File = {
  name: string;
  value: string;
  embed: boolean;
};

type DataProps = {
  file: File[];
};

export default function Assets({ file }: DataProps) {
  const isPdf = (url: string) => /\.pdf$/.test(url);
  const isImage = (url: string) => /\.(jpg|jpeg|png|gif|bmp)$/.test(url);
  const isGoogleDoc = (url: string) => /docs\.google\.com\/document/.test(url);
  const isGoogleDriveFile = (url: string) => /https:\/\/drive\.google\.com\/file\/d\/[a-zA-Z0-9_-]+\/view/.test(url);

  const getFileId = (url: string) => {
    const match = url.match(/[-\w]{25,}/);
    return match ? match[0] : '';
  };

  const displayPdf = (url: string) => {
    return (
      <iframe
        title="PDF Preview"
        src={`https://drive.google.com/file/d/${getFileId(url)}/preview`}
        className="assignmentRender-pdf"
      />
    );
  };

  const displayImage = (url: string) => {
    return (
      <img
        src={url}
        alt="Image Preview"
        className="assignmentRender-file"
        onError={(e) => console.error(`Error loading image: ${url}`, e)}
      />
    );
  };

  const renderFile = (name: string, value: string) => {
    if (name === "Application Link") {
      return <a href={value} target="_blank" rel="noopener noreferrer"><span style={{fontSize:"1rem"}}>{name}</span></a>;
    } else if (name === "Google Drive Folder Link") {
      return (
        <div className="flex-end">
          <Button className="white-bg dark-orange-color"><a href={value} target="_blank" rel="noopener noreferrer">Open Google Drive Folder</a></Button>
        </div>
      );
    } else if (isPdf(value)) {
      return displayPdf(value);
    } else if (isImage(value)) {
      return displayImage(value);
    } else if (isGoogleDoc(value)) {
      return displayPdf(value);
    } else if (isGoogleDriveFile(value)) {
      return displayPdf(value);
    } else {
      return <div>Unsupported file type or link.</div>;
    }
  };

  if (file?.every(item => !item.value)) {
    return <EmptyJobHandler title="No Assets Available" description="There are no assets for this job, please go back to job and react to jobs!" />;
  }

  return (
    <Row gutter={16} justify="center" className="mt-16 asset-container">
    {file?.map((item, index) => (
      <Col key={index} span={18} className="iframe-container">
        <div>
          {item.name !== "Application Link" && item.name !== "Google Drive Folder Link" && (
            <div className="d-flex-between mt-8">
              <h4>{item.name}</h4>
              <span><a href={item.value} target="_blank" rel="noopener noreferrer">Download</a></span>
            </div>
          )}
          {renderFile(item.name, item.value)}
        </div>
        {index < file.length - 1 && <Divider />}
      </Col>
    ))}
  </Row>
  );
}
