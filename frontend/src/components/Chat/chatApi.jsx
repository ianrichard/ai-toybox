// Example: Adapted for React
export function handleWSMessageReact(data, { addMessage, addOrUpdateAssistant, setIsTyping, setMessages, setToolCalls }) {
    let msg;
    try {
      msg = JSON.parse(data);
    } catch {
      addMessage('assistant', data);
      setIsTyping(false);
      return;
    }
    switch (msg.type) {
      case 'assistant':
        setIsTyping(!msg.complete);
        if (msg.content || !msg.complete) {
          addOrUpdateAssistant(msg.content || "");
        }
        break;
      case 'tool':
        setIsTyping(false);
        if (msg.results !== undefined) {
          setMessages(prevMessages => prevMessages.map(m =>
            m.type === 'tool-call' && m.content.id === msg.id
              ? { ...m, type: 'tool-result', content: { ...m.content, results: msg.results } }
              : m
          ));
          setToolCalls(prevToolCalls => ({ ...prevToolCalls, [msg.id]: undefined }));
        } else if (msg.args !== undefined) {
          const toolCall = { id: msg.id, name: msg.name, args: msg.args };
          setToolCalls(prevToolCalls => ({ ...prevToolCalls, [msg.id]: toolCall }));
          addMessage('tool-call', toolCall);
        }
        break;
      case 'error':
        setIsTyping(false);
        addMessage('error', msg.content);
        break;
      case 'status':
        break;
      default:
        addMessage('assistant', data);
    }
  }