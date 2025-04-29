// Example: formatContent for React
export function formatContent(content) {
  if (typeof content !== 'string') {
    return <pre>{JSON.stringify(content, null, 2)}</pre>;
  }
  let formatted = content
    .replace(/```(\w+)?\n([\s\S]*?)\n```/g, (_, lang, code) => `<pre><code>${code}</code></pre>`)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
  return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
}