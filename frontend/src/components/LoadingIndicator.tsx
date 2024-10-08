import React from 'react';
import { Slab } from 'react-loading-indicators';

interface Message {
    message: string; 
}

const LoadingIndicator: React.FC<Message> = ({ message }) => {
    const containerStyle: React.CSSProperties = {
        display: 'flex',
        justifyContent: 'center',
        flexDirection: 'column',
        alignItems: 'center',
        height: '70vh',
        fontFamily: 'Arial, sans-serif',
        color: '#d1cccb',
    };

    const loadingBoxStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        padding: '20px',
        borderRadius: '10px',
    };

    const loadingTextStyle: React.CSSProperties = {
        fontSize: '18px',
        color: '#333',
        fontWeight: '500',
        marginTop: '10px',
    };

    const Loading = () => {
        return (
            <div style={containerStyle}>
                <h1 style={loadingTextStyle}>{message}</h1>
                <div style={loadingBoxStyle}>
                    <Slab color="#ee582b" size="medium" text="" textColor="#333" />
                </div>
            </div>
        );
    };

    return (
        <div>
            <Loading />
        </div>
    );
};

export default LoadingIndicator;