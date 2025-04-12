function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [buffer, setBuffer] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);
  
  const send = useWebSocket(
    'ws://localhost:8000/chat', 
    (msg) => {
      switch (msg.type) {
        case 'assistant':
          if (!isTyping) setIsTyping(true);
          setBuffer(prev => {
            const updated = prev + msg.content;
            if (prev === '') {
              addMessage('assistant', updated);
            } else {
              updateAssistant(updated);
            }
            return updated;
          });
          break;
        case 'final_response':
          setBuffer('');
          setIsTyping(false);
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

  return (
    <div className="flex flex-col h-full p-4">
      <header className="flex justify-between items-center mb-4 pb-3 border-b">
        <h1 className="text-xl font-bold text-blue-600">
          <i className="fas fa-robot mr-2"></i>
          AI Assistant
        </h1>
        <button 
          onClick={clearChat}
          className="text-gray-500 hover:text-red-500 p-1 rounded"
          title="Clear chat"
        >
          <i className="fas fa-trash"></i>
        </button>
      </header>
      
      <div className="flex-1 overflow-y-auto px-2 py-4 bg-gray-50 rounded-lg">
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
      
      <div className="py-4 sticky bottom-0 bg-gray-50">
        <div className="flex items-center bg-white rounded-full border shadow-sm px-3 py-1">
          <input
            className="flex-1 p-2 outline-none"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button
            className="bg-blue-600 text-white p-2 rounded-full w-10 h-10 flex items-center justify-center hover:bg-blue-700 transition-colors disabled:opacity-50"
            onClick={handleSend}
            disabled={!input.trim()}
          >
            <i className="fas fa-paper-plane"></i>
          </button>
        </div>
        <div className="text-xs text-center text-gray-500 mt-2">
          Press Enter to send your message
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);