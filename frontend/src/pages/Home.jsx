import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  const screens = [
    { path: '/chat-thread', name: 'Screen 1: Proactive Agent Chat Thread' },
    { path: '/agent-stream', name: 'Screen 2: Interactive Agent Stream' },
    { path: '/settings-skills', name: 'Screen 3: Agent Settings & Skills' },
    { path: '/hands-free-voice', name: 'Screen 4: Hands-Free Voice Mode' },
    { path: '/memory-search', name: 'Screen 5: Global Memory Search' },
    { path: '/conversational-core', name: 'Screen 6: Conversational Core Stream' },
    { path: '/task-inbox-cards', name: 'Screen 7: Interactive Task & Inbox Cards' },
    { path: '/mvp-config', name: 'Screen 8: MVP Agent Configuration' },
    { path: '/voice-mode', name: 'Screen 9: Voice Mode (Active)' },
  ];

  return (
    <div className="min-h-screen bg-background-dark text-white p-8 font-display">
      <h1 className="text-3xl font-bold mb-8 text-primary">Proactive Agent Design References</h1>
      <div className="grid gap-4 max-w-2xl">
        {screens.map((screen) => (
          <Link
            key={screen.path}
            to={screen.path}
            className="block p-4 bg-surface-dark border border-white/10 rounded-xl hover:border-primary/50 hover:bg-surface-highlight transition-all"
          >
            <div className="flex justify-between items-center">
              <span className="font-medium">{screen.name}</span>
              <span className="material-symbols-outlined text-primary">arrow_forward</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Home;
