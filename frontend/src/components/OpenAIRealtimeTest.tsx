import React, { useRef, useState } from 'react';
import useMiddleSocket from '../hooks/useMiddleSocket';

const OpenAIRealtimeTest: React.FC = () => {
  const { setAssemblyTTS, } = useMiddleSocket();
  const socketHook = useMiddleSocket();

  const [isRecording, setIsRecording] = useState(false);
  const [streamProvider, setStreamProvider] = useState<'whisper'|'google'|'gemini'|'fw'>('whisper');
  const [uploadProvider, setUploadProvider] = useState<'fw'|'gemini'|'openai'>('fw');
  const [uploadLang, setUploadLang] = useState<string>('');
  const [activePanel, setActivePanel] = useState<'realtime'|'upload'>('realtime');
  const [activeTranscriptSource, setActiveTranscriptSource] = useState<'whisper'|'google'|'gemini'|'fw'|'upload-fw'|'upload-gemini'|'upload-openai'>('whisper');
  const [uploadResults, setUploadResults] = useState<Record<string,string>>({});
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [comparisons, setComparisons] = useState<Array<{ id: string; source: string; text: string; ts: number }>>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const latest = JSON.parse(localStorage.getItem('userSession') || 'null');

  const setupAudio = async (onProcess: (pcm: ArrayBuffer) => void) => {
    setAssemblyTTS([]);
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStreamRef.current = stream;
    const source = audioContextRef.current.createMediaStreamSource(stream);
    sourceRef.current = source;
    const processor = audioContextRef.current.createScriptProcessor(8192, 1, 1);
    processorRef.current = processor;
    processor.onaudioprocess = (event) => {
      const inputBuffer = event.inputBuffer.getChannelData(0);
      const pcmData = new Int16Array(inputBuffer.length);
      for (let i = 0; i < inputBuffer.length; i++) {
        pcmData[i] = Math.max(-32768, Math.min(32767, inputBuffer[i] * 32767));
      }
      console.log('[REC][CHUNK]', { samples: pcmData.length, bytes: pcmData.byteLength });
      onProcess(pcmData.buffer);
    };
    source.connect(processor);
    processor.connect(audioContextRef.current.destination);
  };

  const teardownAudio = async () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current.onaudioprocess = null as any;
    }
    if (sourceRef.current) sourceRef.current.disconnect();
    if (audioContextRef.current) await audioContextRef.current.close();
    if (mediaStreamRef.current) mediaStreamRef.current.getTracks().forEach(t => t.stop());
  };

  const startStreaming = async () => {
    if (isRecording) return;
    // reset transcripts for selected stream
    if (streamProvider === 'whisper') (socketHook as any).whisperTranscript = "";
    if (streamProvider === 'google') (socketHook as any).googleTranscript = "";
    if (streamProvider === 'gemini') (socketHook as any).geminiTranscript = "";
    if (streamProvider === 'fw') (socketHook as any).fwTranscript = "";
    await setupAudio((pcm) => {
      if (streamProvider === 'whisper') socketHook.socket?.emit?.('audio transcribe whisper', { latest, audioblob: pcm });
      if (streamProvider === 'google') socketHook.socket?.emit?.('audio transcribe google', { latest, audioblob: pcm });
      if (streamProvider === 'gemini') socketHook.socket?.emit?.('audio transcribe gemini', { latest, audioblob: pcm });
      if (streamProvider === 'fw') socketHook.socket?.emit?.('audio transcribe fw', { latest, audioblob: pcm });
    });
    setIsRecording(true);
  };

  const stopStreaming = async () => {
    await teardownAudio();
    setIsRecording(false);
    if (streamProvider === 'whisper') await socketHook.socket?.emit?.('audio transcribe whisper', { audioblob: null });
    if (streamProvider === 'google') await socketHook.socket?.emit?.('audio transcribe google', { audioblob: null });
    if (streamProvider === 'gemini') await socketHook.socket?.emit?.('audio transcribe gemini', { audioblob: null });
    if (streamProvider === 'fw') await socketHook.socket?.emit?.('audio transcribe fw', { audioblob: null });
    // Snapshot current realtime transcript for comparison list
    const transcriptMap: Record<string, string> = {
      whisper: socketHook.whisperTranscript || '',
      google: (socketHook as any).googleTranscript || '',
      gemini: (socketHook as any).geminiTranscript || '',
      fw: (socketHook as any).fwTranscript || '',
    };
    const text = transcriptMap[streamProvider] || '';
    if (text.trim()) {
      setComparisons(prev => [
        ...prev,
        { id: `${Date.now()}-${streamProvider}`, source: `realtime:${streamProvider}`, text, ts: Date.now() }
      ]);
    }
  };

  const handleUpload = async (file: File) => {
    try {
      const key = uploadProvider === 'fw' ? 'upload-fw' : uploadProvider === 'gemini' ? 'upload-gemini' : 'upload-openai';
      setActivePanel('upload');
      setActiveTranscriptSource(key as any);
      setUploadResults(prev => ({ ...prev, [key]: '(processing...)' }));
      const form = new FormData();
      form.append('file', file);
      // qs placeholder removed; building query from uploadLang below
      const ENV = (import.meta as any).env || {};
      const API_BASE_RAW = (ENV.VITE_REACT_APP_BACKEND_URL).toString();
      const API_BASE = API_BASE_RAW ? API_BASE_RAW.replace(/\/$/, '') : '';
      const base = API_BASE ? `${API_BASE}` : '';
      let path = '/api/stt/whisper-upload';
      if (uploadProvider === 'gemini') path = '/api/stt/gemini-upload';
      if (uploadProvider === 'openai') path = '/api/stt/openai-upload';
      const qp = uploadLang.trim() ? `?language=${encodeURIComponent(uploadLang.trim())}` : '';
      const res = await fetch(`${base}${path}${qp}`, { method: 'POST', body: form });
      const json = await res.json();
      const text = json?.text || json?.content || '';
      setUploadResults(prev => ({ ...prev, [key]: text || '(empty)' }));
      // Save to comparisons list in call order
      if ((text || '').trim()) {
        setComparisons(prev => [
          ...prev,
          { id: `${Date.now()}-${key}`, source: `upload:${uploadProvider}`, text, ts: Date.now() }
        ]);
      }
    } catch (e: any) {
      const key = uploadProvider === 'fw' ? 'upload-fw' : uploadProvider === 'gemini' ? 'upload-gemini' : 'upload-openai';
      setUploadResults(prev => ({ ...prev, [key]: `Error: ${e?.message || e}` }));
    }
  };

  // Compute single transcript view based on selection
  const transcriptMap: Record<string, string> = {
    whisper: socketHook.whisperTranscript || '',
    google: (socketHook as any).googleTranscript || '',
    gemini: (socketHook as any).geminiTranscript || '',
    fw: (socketHook as any).fwTranscript || '',
    'upload-fw': uploadResults['upload-fw'] || '',
    'upload-gemini': uploadResults['upload-gemini'] || '',
    'upload-openai': uploadResults['upload-openai'] || '',
  };
  const activeTranscript = transcriptMap[activeTranscriptSource] || '(waiting...)';

  return (
    <div style={{ padding: 16, height: '100%', boxSizing: 'border-box' }}>
      <h3 style={{ marginTop: 0, marginBottom: 12 }}>STT Demo – Realtime and File Upload</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16, height: 'calc(100vh - 140px)' }}>
        <div style={{ border: '1px solid #f0f0f0', borderRadius: 8, padding: 12, overflow: 'auto' }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <button onClick={() => setActivePanel('realtime')} style={{ fontWeight: activePanel==='realtime'?'bold':undefined }}>Realtime</button>
            <button onClick={() => setActivePanel('upload')} style={{ fontWeight: activePanel==='upload'?'bold':undefined }}>Upload</button>
          </div>

          {activePanel === 'realtime' ? (
            <div>
              <label>Provider</label>
              <select value={streamProvider} onChange={(e) => { const v = e.target.value as any; setStreamProvider(v); setActiveTranscriptSource(v); }} style={{ width: '100%', margin: '6px 0 10px' }}>
                <option value="whisper">OpenAI Whisper (socket)</option>
                <option value="google">Google STT (streaming)</option>
                <option value="gemini">Gemini Live (experimental)</option>
                <option value="fw">faster-whisper (local)</option>
              </select>
              {!isRecording ? (
                <button onClick={startStreaming} style={{ width: '100%' }}>Start recording</button>
              ) : (
                <button onClick={stopStreaming} style={{ width: '100%' }}>Stop</button>
              )}
            </div>
          ) : (
            <div>
              <label>Provider</label>
              <select value={uploadProvider} onChange={(e) => setUploadProvider(e.target.value as any)} style={{ width: '100%', margin: '6px 0 10px' }}>
                <option value="fw">faster-whisper (local)</option>
                <option value="gemini">Gemini (batch)</option>
                <option value="openai">OpenAI (existing logic)</option>
              </select>
              <input placeholder="language (e.g., en) optional" value={uploadLang} onChange={(e) => setUploadLang(e.target.value)} style={{ width: '100%', marginBottom: 8 }} />
              <input type="file" accept="audio/*,video/*" onChange={(e) => { const f = e.target.files?.[0] || null; setSelectedFile(f); }} style={{ width: '100%' }} />
              <button onClick={() => { if (selectedFile) handleUpload(selectedFile); }} disabled={!selectedFile} style={{ width: '100%', marginTop: 8 }}>Transcribe</button>
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>Pick a file to transcribe; result will show on the right.</div>
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <label>View transcript</label>
            <select value={activeTranscriptSource} onChange={(e) => setActiveTranscriptSource(e.target.value as any)} style={{ width: '100%', marginTop: 6 }}>
              <optgroup label="Realtime">
                <option value="whisper">OpenAI Whisper</option>
                <option value="google">Google STT</option>
                <option value="gemini">Gemini Live</option>
                <option value="fw">faster-whisper</option>
              </optgroup>
              <optgroup label="Uploads">
                <option value="upload-fw">Upload – faster-whisper</option>
                <option value="upload-gemini">Upload – Gemini</option>
                <option value="upload-openai">Upload – OpenAI</option>
              </optgroup>
            </select>
          </div>
        </div>

        <div style={{ border: '1px solid #f0f0f0', borderRadius: 8, padding: 16, overflow: 'auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <strong style={{ fontSize: 16 }}>Transcript</strong>
            <span style={{ fontSize: 12, color: '#666' }}>{activeTranscriptSource}</span>
          </div>
          <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5, minHeight: 200 }}>{activeTranscript}</div>

          {comparisons.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>Comparisons (ordered)</strong>
                <button onClick={() => setComparisons([])} style={{ fontSize: 12 }}>Clear</button>
              </div>
              <ol style={{ marginTop: 8, paddingLeft: 18 }}>
                {comparisons
                  .sort((a, b) => a.ts - b.ts)
                  .map(item => (
                    <li key={item.id} style={{ marginBottom: 8 }}>
                      <div style={{ fontSize: 12, color: '#666' }}>{item.source} • {new Date(item.ts).toLocaleTimeString()}</div>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{item.text}</div>
                    </li>
                  ))}
              </ol>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OpenAIRealtimeTest;


