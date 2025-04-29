import { html, nothing } from 'lit';
import { formatContent } from './chatUtils.js';

export function Avatar(type) {
  if (type === 'tool-call') {
    return html`<div class="mt-2 w-8 h-8 rounded-full bg-yellow-500 text-white flex items-center justify-center flex-shrink-0">
      <sl-icon name="tools"></sl-icon>
    </div>`;
  }
  if (type === 'tool-result') {
    return html`<div class="mt-2 w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center flex-shrink-0">
      <sl-icon name="tools"></sl-icon>
    </div>`;
  }
  if (type === 'error') {
    return html`<div class="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center flex-shrink-0">
      <sl-icon name="exclamation-triangle"></sl-icon>
    </div>`;
  }
  return nothing;
}

export function renderMessage(msg, idx, expanded, toggleExpand) {
  if (msg.type === 'tool-call' || msg.type === 'tool-result') {
    const isExpanded = !!expanded[idx];
    return html`
      <div class="flex mb-2">
        ${Avatar(msg.type)}
        <div class="ml-2 ${msg.type === 'tool-call'
          ? 'bg-yellow-100 border-l-4 border-yellow-500 font-mono text-sm px-4 py-3 rounded-xl'
          : 'bg-green-50 border-l-4 border-green-500 text-green-700 font-mono text-sm px-4 py-3 rounded-xl'}">
          <div class="font-semibold mb-1 flex items-center cursor-pointer" @click=${() => toggleExpand(idx)}>
            <span>${msg.content.name}</span>
            <sl-icon name="chevron-down" class=${isExpanded ? 'rotate-180' : ''} style="margin-left:8px"></sl-icon>
          </div>
          ${isExpanded ? html`
            <div class="mb-2">
              <div class="text-xs text-gray-500 mb-1">Input</div>
              <pre class="bg-gray-100 p-2 rounded text-sm overflow-auto">${JSON.stringify(msg.content.args, null, 2)}</pre>
            </div>
            ${msg.type === 'tool-result' && msg.content.results !== undefined ? html`
              <div>
                <div class="text-xs text-gray-500 mb-1">Result</div>
                <pre class="bg-gray-100 p-2 rounded text-sm overflow-auto">
${typeof msg.content.results === 'object'
  ? JSON.stringify(msg.content.results, null, 2)
  : msg.content.results}
                </pre>
              </div>
            ` : html`
              <div class="text-xs mt-2 text-gray-500 flex items-center">
                <sl-icon name="hourglass-split" class="mr-1"></sl-icon> Loading results
              </div>
            `}
          ` : nothing}
        </div>
      </div>
    `;
  }
  // Error/system/user/assistant
  return html`
    <div class="flex mb-2 ${msg.type === 'user' ? 'justify-end' : ''}">
      ${Avatar(msg.type)}
      <div class="${msg.type === 'user'
        ? 'bg-blue-600 text-white px-4 py-3 rounded-xl mb-3 max-w-[85%]'
        : msg.type === 'assistant'
          ? 'text-gray-800 my-4 max-w-[85%]'
          : msg.type === 'error'
            ? 'bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-xl mb-3 ml-2 max-w-[85%]'
            : 'text-gray-800'}">
        ${formatContent(msg.content)}
      </div>
    </div>
  `;
}