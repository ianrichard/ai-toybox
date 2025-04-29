// filepath: /Users/ian/Sites/ai-toybox/frontend/src/components/Chat/chatApi.js
export function connectWebSocket({ onMessage, onOpen, onError, onClose }) {
  const ws = new WebSocket('ws://localhost:8000/chat');
  ws.onopen = onOpen;
  ws.onmessage = (e) => onMessage(e.data);
  ws.onerror = onError;
  ws.onclose = onClose;
  return ws;
}

export function handleWSMessage(data, ctx) {
    let msg;
    try {
      msg = JSON.parse(data);
    } catch {
      ctx.addMessage('assistant', data);
      ctx.isTyping = false;
      return;
    }
    switch (msg.type) {
      case 'assistant':
        ctx.isTyping = !msg.complete;
        if (msg.content || !msg.complete) {
          ctx.addOrUpdateAssistant(msg.content || "");
        }
        break;
      case 'tool':
        ctx.isTyping = false;
        if (msg.results !== undefined) {
          ctx.messages = ctx.messages.map(m =>
            m.type === 'tool-call' && m.content.id === msg.id
              ? { ...m, type: 'tool-result', content: { ...m.content, results: msg.results } }
              : m
          );
          ctx.toolCalls = { ...ctx.toolCalls, [msg.id]: undefined };
        } else if (msg.args !== undefined) {
          const toolCall = { id: msg.id, name: msg.name, args: msg.args };
          ctx.toolCalls = { ...ctx.toolCalls, [msg.id]: toolCall };
          ctx.addMessage('tool-call', toolCall);
        }
        break;
      case 'error':
        ctx.isTyping = false;
        ctx.addMessage('error', msg.content);
        break;
      case 'status':
        break;
      default:
        ctx.addMessage('assistant', data);
    }
  }