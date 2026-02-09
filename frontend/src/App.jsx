import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import ChatThread from './pages/ChatThread';
import AgentStream from './pages/AgentStream';
import SettingsSkills from './pages/SettingsSkills';
import HandsFreeVoice from './pages/HandsFreeVoice';
import MemorySearch from './pages/MemorySearch';
import ConversationalCore from './pages/ConversationalCore';
import TaskInboxCards from './pages/TaskInboxCards';
import MvpConfig from './pages/MvpConfig';
import VoiceMode from './pages/VoiceMode';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat-thread" element={<ChatThread />} />
        <Route path="/agent-stream" element={<AgentStream />} />
        <Route path="/settings-skills" element={<SettingsSkills />} />
        <Route path="/hands-free-voice" element={<HandsFreeVoice />} />
        <Route path="/memory-search" element={<MemorySearch />} />
        <Route path="/conversational-core" element={<ConversationalCore />} />
        <Route path="/task-inbox-cards" element={<TaskInboxCards />} />
        <Route path="/mvp-config" element={<MvpConfig />} />
        <Route path="/voice-mode" element={<VoiceMode />} />
      </Routes>
    </Router>
  );
}

export default App;
