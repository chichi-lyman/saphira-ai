import React from 'react';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import MessageList from './components/chat/MessageList';
import ChatInput from './components/chat/ChatInput';

/**
 * Root Application Component for Saphira AI™
 * Orchestrates layout, conversation stream, and prompt input.
 */
const App: React.FC = () => {
  return (
    <div className="saphira-app">
      <Header />
      <div className="saphira-main">
        <Sidebar />
        <main className="saphira-chat-area">
          <MessageList />
          <ChatInput />
        </main>
      </div>
    </div>
  );
};

export default App;
