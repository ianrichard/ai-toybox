import React, { useRef, useState, useEffect } from "react";
import { Paper, Textarea, Button, Group, ScrollArea, Stack, Text } from "@mantine/core";
import { IconArrowUp } from "@tabler/icons-react";
import { formatContent } from "./chatUtils.jsx";
import { handleWSMessageReact } from "./chatApi.jsx";

export default function Chat() {
  const [messages, setMessages] = useState([
    { type: "assistant", content: "Hi there! I'm an AI assistant. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [toolCalls, setToolCalls] = useState({});
  const [expanded, setExpanded] = useState({});
  const wsRef = useRef(null);
  const scrollRef = useRef(null);

  // Add or update assistant message
  const addOrUpdateAssistant = (content) => {
    setMessages((msgs) => {
      const last = msgs[msgs.length - 1];
      if (last && last.type === "assistant") {
        return [...msgs.slice(0, -1), { ...last, content }];
      }
      return [...msgs, { type: "assistant", content }];
    });
  };

  // Add message
  const addMessage = (type, content) => {
    setMessages((msgs) => [...msgs, { type, content }]);
  };

  // WebSocket setup
  useEffect(() => {
    wsRef.current = new window.WebSocket("ws://localhost:3001"); // Change URL as needed
    wsRef.current.onopen = () => addMessage("system", "WebSocket connected");
    wsRef.current.onclose = () => addMessage("system", "WebSocket closed");
    wsRef.current.onerror = () => addMessage("system", "WebSocket error");
    wsRef.current.onmessage = (e) =>
      handleWSMessageReact(e.data, {
        addMessage,
        addOrUpdateAssistant,
        setIsTyping,
        setMessages,
        setToolCalls,
      });
    return () => wsRef.current && wsRef.current.close();
    // eslint-disable-next-line
  }, []);

  // Scroll to bottom on new message
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  // Send message
  const sendMessage = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== 1) return;
    addMessage("user", input);
    wsRef.current.send(JSON.stringify({ type: "chat", content: input }));
    setInput("");
    setIsTyping(true);
  };

  // Expand/collapse (if needed)
  const toggleExpand = (idx) => {
    setExpanded((exp) => ({ ...exp, [idx]: !exp[idx] }));
  };

  // Render message
  const renderMessage = (msg, idx) => (
    <Group key={idx} position={msg.type === "user" ? "right" : "left"}>
      <Paper radius="xl" p="sm" withBorder>
        <Text>{formatContent(msg.content)}</Text>
      </Paper>
    </Group>
  );

  return (
    <Paper shadow="md" radius="md" p="md" style={{ minHeight: "80vh", display: "flex", flexDirection: "column" }}>
      <ScrollArea style={{ flex: 1, marginBottom: 16 }} viewportRef={scrollRef}>
        <Stack spacing="sm">
          {messages.map((msg, idx) => renderMessage(msg, idx))}
          {isTyping && (
            <Group position="left">
              <Text color="dimmed" italic>
                Assistant is typing...
              </Text>
            </Group>
          )}
        </Stack>
      </ScrollArea>
      <Group spacing="xs" mt="xs" align="end">
        <Textarea
          autosize
          minRows={1}
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          placeholder="Type your message…"
          style={{ flex: 1 }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />
        <Button
          radius="xl"
          size="md"
          disabled={!input.trim()}
          onClick={sendMessage}
          leftIcon={<IconArrowUp size={18} />}
        >
          Send
        </Button>
      </Group>
    </Paper>
  );
}