import { useState } from 'react';
import { LiveKitRoom, VideoConference, RoomAudioRenderer } from '@livekit/components-react';
import '@livekit/components-styles';

export default function App() {
  const [token, setToken] = useState("");
  const [room, setRoom] = useState("nomad-trip");
  const [name, setName] = useState("");

  const joinRoom = async () => {
    // Call your local backend server
    const resp = await fetch(`http://localhost:3001/get-token?room=${room}&username=${name}`);
    const data = await resp.json();
    setToken(data.token);
  };

  if (!token) {
    return (
      <div className="p-10 flex flex-col gap-4 max-w-sm">
        <input className="border p-2" placeholder="Room Name" value={room} onChange={e => setRoom(e.target.value)} />
        <input className="border p-2" placeholder="Your Name" value={name} onChange={e => setName(e.target.value)} />
        <button className="bg-blue-500 text-white p-2 rounded" onClick={joinRoom}>Join</button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      video={false}
      audio={true}
      token={token}
      serverUrl={import.meta.env.VITE_LIVEKIT_URL}
      data-lk-theme="default"
    >
      <VideoConference />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}