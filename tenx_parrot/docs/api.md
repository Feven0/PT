# iPersona Backend API Documentation

## Overview

The iPersona Backend provides several APIs for real-time communication and interview analysis:

1. REST API for traditional HTTP requests
2. WebSocket API for real-time bidirectional communication
3. WebRTC API for high-quality audio streaming

## Base URLs

- REST API: `http://localhost:9900/api/v1`
- WebSocket: `ws://localhost:9900/ws`
- WebRTC: `http://localhost:9900/webrtc`

## Authentication

All APIs require authentication using a Bearer token:

```http
Authorization: Bearer your_token_here
```

## REST API

### Interview Analysis

#### Analyze Interview

```http
POST /interviews/analyze
Content-Type: application/json
Authorization: Bearer your_token_here

{
    "interview_id": "string",
    "transcript": "string",
    "metrics": {
        "duration": "number",
        "question_count": "number"
    }
}
```

Response:
```json
{
    "id": "string",
    "analysis": {
        "technical_competency": {
            "score": "number",
            "observations": "string",
            "strengths": ["string"],
            "improvements": ["string"]
        },
        "communication": {
            "score": "number",
            "observations": "string",
            "strengths": ["string"],
            "improvements": ["string"]
        },
        "problem_solving": {
            "score": "number",
            "observations": "string",
            "strengths": ["string"],
            "improvements": ["string"]
        },
        "cultural_fit": {
            "score": "number",
            "observations": "string",
            "strengths": ["string"],
            "improvements": ["string"]
        },
        "overall": {
            "score": "number",
            "recommendation": "string"
        }
    },
    "metrics": {
        "duration": "number",
        "question_count": "number",
        "response_time_avg": "number",
        "technical_accuracy": "number",
        "communication_clarity": "number"
    },
    "created_at": "string"
}
```

#### Get Interview Analysis

```http
GET /interviews/{interview_id}/analysis
Authorization: Bearer your_token_here
```

Response: Same as analyze interview response

## WebSocket API

### Chat Connection

Connect URL: `ws://localhost:9900/ws/chat/{client_id}`

Headers:
```http
Authorization: Bearer your_token_here
```

### Message Types

#### 1. Text Chat

Send:
```json
{
    "type": "chat",
    "content": "string",
    "conversation_id": "string (optional)"
}
```

Receive:
```json
{
    "type": "chat",
    "content": "string",
    "timestamp": "string"
}
```

#### 2. Interview Analysis

Send:
```json
{
    "type": "interview",
    "interview_id": "string",
    "transcript": "string"
}
```

Receive:
```json
{
    "type": "interview_analysis",
    "content": {
        // Same as REST API analysis response
    }
}
```

#### 3. Audio Transcription

Send:
```json
{
    "type": "audio",
    "content": "base64_audio_data"
}
```

Receive:
```json
{
    "type": "transcription",
    "content": "string",
    "is_final": "boolean"
}
```

### Error Messages

Receive:
```json
{
    "type": "error",
    "content": "string"
}
```

## WebRTC API

### Create Connection

```http
POST /webrtc/offer
Content-Type: application/json
Authorization: Bearer your_token_here

{
    "client_id": "string",
    "offer": {
        "sdp": "string",
        "type": "string"
    }
}
```

Response:
```json
{
    "sdp": "string",
    "type": "string"
}
```

### Close Connection

```http
DELETE /webrtc/{client_id}
Authorization: Bearer your_token_here
```

Response:
```json
{
    "status": "success"
}
```

## Client Integration

### Python Example (Complete)

```python
import asyncio
import websockets
import json
import aiohttp
import base64
import pyaudio
import wave
import numpy as np

class iPersonaClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.client_id = None
        self.websocket = None
        self.rtc_connection = None
        
    async def connect(self):
        """Connect to WebSocket."""
        self.client_id = "client_" + str(uuid.uuid4())
        uri = f"{self.base_url}/ws/chat/{self.client_id}"
        self.websocket = await websockets.connect(uri, extra_headers=self.headers)
        
    async def send_message(self, message):
        """Send chat message."""
        if not self.websocket:
            await self.connect()
            
        await self.websocket.send(json.dumps({
            "type": "chat",
            "content": message
        }))
        
        response = await self.websocket.recv()
        return json.loads(response)
        
    async def analyze_interview(self, transcript):
        """Analyze interview transcript."""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.base_url}/interviews/analyze",
                json={
                    "transcript": transcript
                }
            ) as response:
                return await response.json()
                
    async def start_audio_stream(self):
        """Start audio streaming using WebRTC."""
        if not self.client_id:
            await self.connect()
            
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        # Create WebRTC connection
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Send offer
            offer = {
                "client_id": self.client_id,
                "offer": {
                    "sdp": "...",  # Your SDP here
                    "type": "offer"
                }
            }
            
            async with session.post(
                f"{self.base_url}/webrtc/offer",
                json=offer
            ) as response:
                answer = await response.json()
                
                # Start streaming
                try:
                    while True:
                        data = stream.read(1024)
                        # Send audio data through WebSocket
                        await self.websocket.send(json.dumps({
                            "type": "audio",
                            "content": base64.b64encode(data).decode()
                        }))
                        
                        # Receive transcription
                        response = await self.websocket.recv()
                        print(json.loads(response))
                        
                except KeyboardInterrupt:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()

# Usage example
async def main():
    client = iPersonaClient(
        base_url="http://localhost:9900",
        token="your_token_here"
    )
    
    # Text chat
    response = await client.send_message("Hello!")
    print(response)
    
    # Interview analysis
    analysis = await client.analyze_interview(
        "Tell me about your experience with Python..."
    )
    print(analysis)
    
    # Audio streaming
    await client.start_audio_stream()

# Run in Jupyter
await main()
```

### React Example (Complete)

```typescript
// iPersonaClient.ts
interface iPersonaConfig {
    baseUrl: string;
    token: string;
}

class iPersonaClient {
    private baseUrl: string;
    private token: string;
    private ws: WebSocket | null = null;
    private rtcConnection: RTCPeerConnection | null = null;
    private clientId: string;
    
    constructor(config: iPersonaConfig) {
        this.baseUrl = config.baseUrl;
        this.token = config.token;
        this.clientId = `client_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    private get headers() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async connect(onMessage: (data: any) => void) {
        this.ws = new WebSocket(
            `${this.baseUrl.replace('http', 'ws')}/ws/chat/${this.clientId}`
        );
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onMessage(data);
        };
        
        return new Promise((resolve, reject) => {
            if (this.ws) {
                this.ws.onopen = () => resolve(true);
                this.ws.onerror = (error) => reject(error);
            }
        });
    }
    
    async sendMessage(content: string) {
        if (!this.ws) {
            throw new Error('WebSocket not connected');
        }
        
        this.ws.send(JSON.stringify({
            type: 'chat',
            content
        }));
    }
    
    async analyzeInterview(transcript: string) {
        const response = await fetch(
            `${this.baseUrl}/interviews/analyze`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ transcript })
            }
        );
        return response.json();
    }
    
    async startAudioStream(onTranscription: (text: string) => void) {
        // Create RTCPeerConnection
        this.rtcConnection = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        });
        
        // Get user media
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });
        
        // Add tracks
        stream.getTracks().forEach(track => {
            if (this.rtcConnection) {
                this.rtcConnection.addTrack(track, stream);
            }
        });
        
        // Create and set local description
        const offer = await this.rtcConnection.createOffer();
        await this.rtcConnection.setLocalDescription(offer);
        
        // Send offer to server
        const response = await fetch(
            `${this.baseUrl}/webrtc/offer`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({
                    client_id: this.clientId,
                    offer: {
                        sdp: this.rtcConnection.localDescription?.sdp,
                        type: this.rtcConnection.localDescription?.type
                    }
                })
            }
        );
        
        // Set remote description
        const answer = await response.json();
        await this.rtcConnection.setRemoteDescription(answer);
    }
    
    async disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        
        if (this.rtcConnection) {
            this.rtcConnection.close();
        }
        
        if (this.clientId) {
            await fetch(
                `${this.baseUrl}/webrtc/${this.clientId}`,
                {
                    method: 'DELETE',
                    headers: this.headers
                }
            );
        }
    }
}

// Usage in React component
import React, { useEffect, useState } from 'react';

const InterviewComponent: React.FC = () => {
    const [client, setClient] = useState<iPersonaClient | null>(null);
    const [messages, setMessages] = useState<string[]>([]);
    
    useEffect(() => {
        const initClient = async () => {
            const ipersonaClient = new iPersonaClient({
                baseUrl: 'http://localhost:9900',
                token: 'your_token_here'
            });
            
            await ipersonaClient.connect((data) => {
                if (data.type === 'chat') {
                    setMessages(prev => [...prev, data.content]);
                }
            });
            
            setClient(ipersonaClient);
        };
        
        initClient();
        
        return () => {
            if (client) {
                client.disconnect();
            }
        };
    }, []);
    
    const handleSendMessage = async (message: string) => {
        if (client) {
            await client.sendMessage(message);
        }
    };
    
    const handleStartAudio = async () => {
        if (client) {
            await client.startAudioStream((transcription) => {
                console.log('Transcription:', transcription);
            });
        }
    };
    
    return (
        <div>
            <div>
                {messages.map((msg, i) => (
                    <div key={i}>{msg}</div>
                ))}
            </div>
            <button onClick={() => handleSendMessage('Hello!')}>
                Send Message
            </button>
            <button onClick={handleStartAudio}>
                Start Audio
            </button>
        </div>
    );
};

export default InterviewComponent;
```

## Error Handling

All APIs use standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

WebSocket error messages include:
```json
{
    "type": "error",
    "content": "Error description"
}
```

## Rate Limiting

- REST API: 100 requests per minute
- WebSocket: 10 messages per second
- WebRTC: No explicit limits, but bandwidth limitations apply

## Best Practices

1. **Connection Management**:
   - Always properly close WebSocket and WebRTC connections
   - Implement reconnection logic for WebSocket
   - Handle WebRTC ICE connection failures

2. **Audio Streaming**:
   - Use appropriate audio format (16-bit PCM, 16kHz sample rate)
   - Implement audio level monitoring
   - Handle network interruptions gracefully

3. **Error Handling**:
   - Implement proper error handling for all API calls
   - Log errors appropriately
   - Provide user-friendly error messages

4. **Performance**:
   - Use streaming responses when available
   - Implement proper cleanup of resources
   - Monitor memory usage with audio/video streams 