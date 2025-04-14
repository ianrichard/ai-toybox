function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [buffer, setBuffer] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);
  
  const send = useWebSocket(
    'ws://localhost:8000/chat', 
    (msg) => {
      switch (msg.type) {
        case 'assistant':
          if (!isTyping) setIsTyping(true);
          
          // If it's just a completion signal without content, don't update the message
          if (msg.content || !msg.complete) {
            setBuffer(prev => {
              const updated = prev + (msg.content || "");
              if (prev === '') {
                addMessage('assistant', updated);
              } else {
                updateAssistant(updated);
              }
              return updated;
            });
          }
          
          // Check if this is the final message (complete flag)
          if (msg.complete) {
            setBuffer('');
            setIsTyping(false);
          }
          break;
        case 'tool_call':
          setIsTyping(false);
          addMessage('tool-call', msg.content);
          break;
        case 'tool_result':
          addMessage('tool-result', msg.content);
          break;
        case 'error':
          setIsTyping(false);
          addMessage('error', msg.content);
          break;
      }
    },
    (errorMessage) => {
      // Handle error
      setIsTyping(false);
      addMessage('error', errorMessage);
    }
  );

  const addMessage = (type, content) => {
    setMessages(prev => [...prev, { type, content }]);
  };

  const updateAssistant = (content) => {
    setMessages(prev => {
      const last = [...prev];
      if (last.length && last[last.length - 1].type === 'assistant') {
        last[last.length - 1] = { ...last[last.length - 1], content };
      }
      return last;
    });
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // Add the user's message to the history
    const history = messages.map((msg) => ({
      type: msg.type,
      content: msg.content,
    }));

    addMessage('user', trimmed);
    setIsTyping(true);
    send({ type: 'chat', content: trimmed, history });
    setInput('');
  };
  
  const clearChat = () => {
    setMessages([]);
    setBuffer('');
    setIsTyping(false);
  };
  
  const greetingMessage = "Hi there! I'm an AI assistant. How can I help you today?";
  
  useEffect(() => {
    if (messages.length === 0) {
      addMessage('assistant', greetingMessage);
    }
  }, []);

  // Add dark mode toggle functionality
  const [darkMode, setDarkMode] = useState(
    document.documentElement.getAttribute('data-theme') === 'dark'
  );
  
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  return (
    <div className="flex flex-col h-full p-4">
      <header className="flex justify-between items-center mb-4 pb-3 border-b dark:border-gray-700">
        <h1 className="text-xl font-bold text-blue-600 dark:text-blue-400">
          <i className="fas fa-robot mr-2"></i>
          AI Assistant
        </h1>
        <div className="flex items-center">
          {/* Dark mode toggle button */}
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="text-gray-500 hover:text-yellow-500 dark:hover:text-yellow-300 p-1 rounded mr-2"
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            <i className={`fas ${darkMode ? 'fa-sun' : 'fa-moon'}`}></i>
          </button>
          
          <button 
            onClick={clearChat}
            className="text-gray-500 hover:text-red-500 dark:hover:text-red-400 p-1 rounded"
            title="Clear chat"
          >
            <i className="fas fa-trash"></i>
          </button>
        </div>
      </header>
      
      <div className="flex-1 overflow-y-auto px-2 py-4 rounded-lg">
        <div>
          {messages.map((msg, i) => (
            <Message 
              key={i} 
              type={msg.type} 
              content={msg.content}
              isLastMessage={i === messages.length - 1} 
            />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="py-4 sticky bottom-0">
        <div className="flex items-center bg-white dark:bg-gray-700 rounded-full border dark:border-gray-600 shadow-sm px-3 py-1">
          <input
            ref={inputRef}
            className="flex-1 p-2 outline-none bg-transparent text-gray-800"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button
            className="bg-blue-600 dark:bg-blue-500 text-white p-2 rounded-full w-10 h-10 flex items-center justify-center hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors disabled:opacity-50"
            onClick={handleSend}
            disabled={!input.trim()}
          >
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
        <div className="text-xs text-center text-gray-500 dark:text-gray-400 mt-2">
          Press Enter to send your message
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);