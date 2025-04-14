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
  // Only show avatar for tool-related messages
  if (type === 'tool-call') {
    return (
      <div className="mt-2 w-8 h-8 rounded-full bg-yellow-500 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-tools"></i>
      </div>
    );
  }
  
  if (type === 'tool-result') {
    return (
      <div className="mt-2 w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center flex-shrink-0">
        <i className="fas fa-tools"></i>
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
  
  // Return null for assistant and user (no avatar)
  return null;
}

function Message({ type, content, isLastMessage }) {
  const [expanded, setExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(type === 'tool-call');
  
  // Base styling for different message types
  const styleMap = {
    'user': "bg-blue-600 text-white px-4 py-3 rounded-xl mb-3 max-w-[85%] message-appear",
    'assistant': "text-gray-800 dark:text-gray-200 my-4 max-w-[85%] message-appear", // No bubble, just vertical margin
    'tool-call': "bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-100 border-l-4 border-yellow-500 font-mono text-sm px-4 py-3 rounded-xl mb-3 ml-2 max-w-[85%] message-appear",
    'tool-result': "bg-green-50 dark:bg-green-900 dark:text-green-100 border-l-4 border-green-500 text-green-700 dark:text-green-200 font-mono text-sm px-4 py-3 rounded-xl mb-3 ml-2 max-w-[85%] message-appear",
    'error': "bg-red-50 dark:bg-red-900 dark:text-red-100 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-xl mb-3 ml-2 max-w-[85%] message-appear",
  };
  
  // Adjust wrapper classes
  const wrapperClasses = type === 'user' 
    ? "flex justify-end mb-2" // Keep right alignment but no margin for avatar
    : "flex mb-2";
  
  // Helper function to safely parse JSON
  const safeJsonParse = (jsonString) => {
    try {
      return typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
    } catch (e) {
      console.error("Failed to parse JSON:", e, jsonString);
      return jsonString;
    }
  };
  
  const renderContent = () => {
    if (type === 'tool-call') {
      return (
        <div className="tool-call">
          <div 
            className="font-semibold mb-1 flex items-center cursor-pointer" 
            onClick={() => setExpanded(!expanded)}
          >
            <span>{content.name}</span>
            <i className={`fas fa-chevron-down ml-2 text-xs transition-transform ${expanded ? 'transform rotate-180' : ''}`}></i>
          </div>
          
          {expanded && (
            <React.Fragment>
              <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-sm overflow-auto">
                {JSON.stringify(safeJsonParse(content.args), null, 2)}
              </pre>
              <div className="text-xs mt-2 text-gray-500 flex items-center">
                <i className="fas fa-spinner fa-spin mr-1"></i> Loading results
              </div>
            </React.Fragment>
          )}
        </div>
      );
    } else if (type === 'tool-result') {
      return (
        <div className="tool-result">
          <div 
            className="font-semibold mb-1 flex items-center cursor-pointer" 
            onClick={() => setExpanded(!expanded)}
          >
            <span>{content.name}</span>
            <i className={`fas fa-chevron-down ml-2 text-xs transition-transform ${expanded ? 'transform rotate-180' : ''}`}></i>
          </div>
          
          {expanded && (
            <React.Fragment>
              <div className="mb-2">
                <div className="text-xs text-gray-500 mb-1">Input</div>
                <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-sm overflow-auto">
                  {JSON.stringify(safeJsonParse(content.args), null, 2)}
                </pre>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Result</div>
                <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-sm overflow-auto">
                  {typeof content.results === 'object' 
                    ? JSON.stringify(content.results, null, 2) 
                    : content.results}
                </pre>
              </div>
            </React.Fragment>
          )}
        </div>
      );
    } else {
      return formatContent(content);
    }
  };
  
  return (
    <div className={wrapperClasses}>
      {/* Only show avatar for tool-related messages and errors */}
      {(type === 'tool-call' || type === 'tool-result' || type === 'error') && <Avatar type={type} />}
      
      <div className={styleMap[type] || 'text-gray-800'}>
        {renderContent()}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex mb-2">
      <div className="my-4 ml-2 typing-indicator">
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full mr-1"></span>
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full mr-1"></span>
        <span className="inline-block w-2 h-2 bg-gray-600 rounded-full"></span>
      </div>
    </div>
  );
}