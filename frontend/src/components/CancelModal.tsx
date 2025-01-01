import { useState } from 'react';
import { Modal, Button } from 'antd'; 
interface Data {
    visible: any, 
    handleClose: any, 
    handleConfirm: any
}

const CancelModal: React.FC<Data> = ({ visible, handleClose, handleConfirm }) => {
    const [showOptions, setShowOptions] = useState(false);

    const handleYesClick = () => {
        setShowOptions(true);
    };

    return (
        <Modal
            title={!showOptions ? 'Cancel Interview' : 'Choose an Option'}
            visible={visible}
            onCancel={handleClose}
            footer={null} 
        >
            {!showOptions ? (
                <p>Are you sure you want to cancel the interview?</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <Button type="primary" onClick={() => handleConfirm('pause')}>
                        Yes, pause the interview
                    </Button>
                    <Button type="primary" onClick={() => handleConfirm('stopEvaluate')}>
                        Yes, stop and evaluate performance
                    </Button>
                    <Button type="primary" onClick={() => handleConfirm('stopDelete')}>
                        Yes, stop and delete the interview
                    </Button>
                </div>
            )}

            {!showOptions && (
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'flex-end', 
                    marginTop: '20px', 
                    gap: '1rem'                    
                }}>
                    <Button onClick={handleYesClick} style={{
                        color: "#ffffff", 
                        fontWeight:'bolder' 
                    }}>
                        Yes, I am sure
                    </Button>
                    <Button onClick={handleClose} style={{ 
                        marginRight: '10px', 
                        color: "#ffffff", 
                        fontWeight:'bolder'
                    }}>
                        No, continue the interview
                    </Button>
                </div>
            )}
        </Modal>
    );
};

export default CancelModal;
