const { useState, useEffect, useRef } = React;

function useWebSocket(url, onMessage, onError) {
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => console.log("Connected to WebSocket");
    ws.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      if (onError) onError('WebSocket connection error');
    };
    ws.onclose = () => console.log("WebSocket closed");

    return () => ws.close();
  }, [url]);

  const sendMessage = (data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };

  return sendMessage;
}

function formatContent(content) {
  if (typeof content !== 'string') {
    return <pre>{JSON.stringify(content, null, 2)}</pre>;
  }
  
  // Simple markdown-like formatting
  let formatted = content;
  
  // Format code blocks
  formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)\n```/g, 
    (_, lang, code) => `<pre><code>${code}</code></pre>`);
  
  // Format inline code
  formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Format bold text
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  
  // Format italic text
  formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  
  // Replace line breaks with <br> tags
  formatted = formatted.replace(/\n/g, '<br>');
  
  return <div dangerouslySetInnerHTML={{ __html: formatted }} />;
}

function Avatar({ type }) {
  if (type === 'assistant') {
    return (
      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-robot"></i>
      </div>
    );
  }
  
  if (type === 'user') {
    return (
      <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center flex-shrink-0">
        <i className="fas fa-user"></i>
      </div>
    );
  }
  
  if (type === 'tool-call') {
    return (
      <div className="w-8 h-8 rounded-full bg-yellow-500 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-tools"></i>
      </div>
    );
  }
  
  if (type === 'tool-result') {
    return (
      <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-check-circle"></i>
      </div>
    );
  }
  
  if (type === 'error') {
    return (
      <div className="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-exclamation-triangle"></i>
      </div>
    );
  }
  
  return null;
}

function Message({ type, content, isLastMessage }) {
  const base = "px-4 py-3 rounded-xl mb-3 max-w-[85%] message-appear";
  
  const styleMap = {
    'user': "bg-blue-600 text-white",
    'assistant': "bg-white text-gray-800 border border-gray-200 shadow-sm",
    'tool-call': "bg-yellow-100 border-l-4 border-yellow-500 font-mono text-sm",
    'tool-result': "bg-green-50 border-l-4 border-green-500 font-mono text-sm",
    'error': "bg-red-50 border-l-4 border-red-500 text-red-700",
  };
  
  const wrapperClasses = type === 'user' 
    ? "flex justify-end mb-2" 
    : "flex mb-2";
  
  return (
    <div className={wrapperClasses}>
      {type !== 'user' && <Avatar type={type} />}
      
      <div className={`${base} ${styleMap[type] || 'bg-white'} ml-2 mr-2`}>
        {formatContent(content)}
      </div>
      
      {type === 'user' && <Avatar type={type} />}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex mb-2">
      <Avatar type="assistant" />
      <div className="ml-2 bg-white px-4 py-3 rounded-xl typing-indicator">
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full mr-1"></span>
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full mr-1"></span>
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full"></span>
      </div>
    </div>
  );
}