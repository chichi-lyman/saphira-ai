import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './assets/global.css';
import { UserProvider } from './context/UserContext';
import { ChatProvider } from './context/ChatContext';
import { registerServiceWorker } from './registerServiceWorker';

registerServiceWorker();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <UserProvider>
      <ChatProvider>
        <App />
      </ChatProvider>
    </UserProvider>
  </React.StrictMode>
);
