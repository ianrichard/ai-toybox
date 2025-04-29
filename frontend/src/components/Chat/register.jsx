import React from 'react';
import ReactDOM from 'react-dom/client';
import reactToWebComponent from 'react-to-webcomponent';
import { MantineProvider } from '@mantine/core';
import Chat from './Chat.jsx';
import '@mantine/core/styles.css';

function ChatWithProvider(props) {
   return (
      <MantineProvider>
         <Chat {...props} />
      </MantineProvider>
   );
}

const ChatElement = reactToWebComponent(ChatWithProvider, React, ReactDOM);
customElements.define('ui-chat', ChatElement);
