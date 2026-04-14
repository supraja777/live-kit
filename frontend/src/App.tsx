import { useState } from 'react';
import { 
  LiveKitRoom, 
  VideoConference, 
  RoomAudioRenderer 
} from '@livekit/components-react';
import '@livekit/components-styles';

export default function App() {
  const [token, setToken] = useState("");
  const [room, setRoom] = useState("nomad-trip");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const joinRoom = async () => {
    if (!name || !room) return alert("Please enter both Room and Name");
    setLoading(true);
    try {
      const resp = await fetch(`http://localhost:3001/get-token?room=${room}&username=${name}`);
      if (!resp.ok) throw new Error("Backend server not responding");
      const data = await resp.json();
      setToken(data.token);
    } catch (err) {
      console.error("Connection error:", err);
      alert("Make sure your Node server (server.js) is running on port 3001!");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen w-full bg-slate-950 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-black text-center mb-6 text-slate-900">MOCK INTERVIEW</h1>
          <div className="space-y-4">
            <input 
              className="w-full border-2 border-slate-100 rounded-xl p-4 outline-none focus:border-indigo-500" 
              placeholder="Room ID" value={room} onChange={e => setRoom(e.target.value)} 
            />
            <input 
              className="w-full border-2 border-slate-100 rounded-xl p-4 outline-none focus:border-indigo-500" 
              placeholder="Your Name" value={name} onChange={e => setName(e.target.value)} 
            />
            <button 
              className="w-full py-4 rounded-2xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-all"
              onClick={joinRoom} disabled={loading}
            >
              {loading ? 'CONNECTING...' : 'JOIN INTERVIEW'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-zinc-950 flex flex-col overflow-hidden">
      <LiveKitRoom
        video={false}
        audio={true}
        token={token}
        serverUrl={import.meta.env.VITE_LIVEKIT_URL}
        data-lk-theme="default"
        className="h-full w-full flex flex-col"
      >
        {/* We use a container with a custom class to target tiles via CSS */}
        <div className="flex-grow relative h-full w-full interview-container">
           <VideoConference />
        </div>
        <RoomAudioRenderer />
      </LiveKitRoom>
    </div>
  );
}