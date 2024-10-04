import React, { useState, useRef } from 'react';
import { InboxOutlined } from '@ant-design/icons';
import { Upload, message, Button, UploadProps } from 'antd';
import '../styles/UploadCV/upload.css'
import Api from '../Services/Services';

const { Dragger } = Upload;

const UploadCV: React.FC = () => {
  const [file, setFile] = useState(null);
  const [iscv, setcvUpload] = useState(null);
  const [iscvsize, setcvSize] = useState(null);
  const [change, setChange] = useState(false);
  const [view, setView] = useState(false);
  const fileInputRef = useRef(null);

  const handleCVFileUpload = (info) => {
    const uploadedFile = info.file;
    setFile(uploadedFile);
    setcvUpload(uploadedFile.name);
    const size = formatFileSize(uploadedFile.size);
    setcvSize(size);
    setChange(true);
  };

  const handleClick = () => {
    setView(true);
    sendFile();
  };

  const sendFile = async () => {
    const userId = 'a82d3efe-0289-4acf-a93b-fcc768355e5b';
    const email = "fin@gmail.com";
    const formData = new FormData();

    if (file) {
      formData.append('file', file);
      formData.append('userId', userId);
      formData.append('email', email);
    }

    try {
      await Api.uploadpdf(formData);
      message.success('File uploaded successfully!');
      window.location.assign("/jobs");
    } catch (error) {
      message.error('Failed to upload file.');
      setView(false);
    }
  };

  const formatFileSize = (size) => {
    if (size < 1024) return `${size} B`;
    else if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
    else return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  };

  const props: UploadProps = {
    name: 'file',
    multiple: true,
    beforeUpload: (file) => {
      return false; 
    },
    onChange(info) {
      const { status } = info.file;
      if (status !== 'uploading') {
        console.log(info.file, info.fileList);
        handleCVFileUpload(info);
      }
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
    onDrop(e) {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };
 

  return (
    <div className="upload-container">
        <Dragger {...props}>
            <p className="ant-upload-drag-icon">
                <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to this area to upload</p>
            <p className="ant-upload-hint">
                Support for a single upload. Only PDF or DOCX files are accepted.
            </p>
        </Dragger>
        {change && (
            <div className="button-container">
                <Button type="primary" onClick={handleClick}>
                    Upload CV
                </Button>
            </div>
        )}
    </div>
    );
};

export default UploadCV;