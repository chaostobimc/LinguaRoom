import { useCallback, useEffect, useState } from 'react';
import Landing from './components/Landing.jsx';
import ChatRoom from './components/ChatRoom.jsx';

function getRoomId() {
  const m = window.location.pathname.match(/^\/r\/([\w-]+)/);
  return m ? m[1] : null;
}

export default function App() {
  const [roomId, setRoomId] = useState(getRoomId());

  const navigate = useCallback((to) => {
    window.history.pushState({}, '', to);
    setRoomId(getRoomId());
  }, []);

  useEffect(() => {
    const onPop = () => setRoomId(getRoomId());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  if (roomId) {
    return <ChatRoom roomId={roomId} navigate={navigate} />;
  }
  return <Landing navigate={navigate} />;
}
