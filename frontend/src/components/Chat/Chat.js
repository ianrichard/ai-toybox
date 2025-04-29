import { html, nothing } from 'lit';
import { BaseElement } from '../../core/BaseElement.js';
import { connectWebSocket, handleWSMessage } from './chatApi.js';
import { renderMessage } from './chatTemplate.js';

class UiChat extends BaseElement {
  static properties = {
    messages: { state: true },
    input: { state: true },
    isTyping: { state: true },
    toolCalls: { state: true },
    expanded: { state: true }
  };

  constructor() {
    super();
    this.messages = [];
    this.input = '';
    this.isTyping = false;
    this.toolCalls = {};
    this.expanded = {};
    this.ws = null;
    this.lastUserMsgIdx = null;
  }

  firstUpdated() {
    this.connectWS();
    this.addMessage('assistant', "Hi there! I'm an AI assistant. How can I help you today?");
    // Listen for Enter+Shift for newline, Enter for send
    this.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
  }

  updated(changed) {
    // Scroll user message to top when sent
    if (changed.has('messages') && this.lastUserMsgIdx !== null) {
      const el = this.renderRoot.querySelector(`[data-msg-idx="${this.lastUserMsgIdx}"]`);
      if (el) {
        const rect = el.getBoundingClientRect();
        window.scrollBy({ top: rect.top - 24, behavior: 'smooth' });
      }
      this.lastUserMsgIdx = null;
    }
  }

  connectWS() {
    this.ws = connectWebSocket({
      onOpen: () => this.addMessage('system', 'WebSocket connected'),
      onMessage: (data) => handleWSMessage(data, this),
      onError: () => this.addMessage('system', 'WebSocket error'),
      onClose: () => this.addMessage('system', 'WebSocket closed')
    });
  }

  addMessage(type, content) {
    this.messages = [...this.messages, { type, content }];
    if (type === 'user') {
      this.lastUserMsgIdx = this.messages.length - 1;
    }
  }

  addOrUpdateAssistant(content) {
    const last = this.messages[this.messages.length - 1];
    if (last && last.type === 'assistant') {
      this.messages = [
        ...this.messages.slice(0, -1),
        { ...last, content: last.content + content }
      ];
    } else {
      this.addMessage('assistant', content);
    }
  }

  handleInput(e) {
    this.input = e.target.value;
    this.autoGrowTextarea(e.target);
  }

  autoGrowTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, window.innerHeight * 0.5) + 'px';
  }

  sendMessage() {
    if (this.input.trim() && this.ws && this.ws.readyState === 1) {
      this.addMessage('user', this.input);
      this.ws.send(JSON.stringify({ type: 'chat', content: this.input }));
      this.input = '';
      this.isTyping = true;
      // Reset textarea height and maintain focus
      const ta = this.renderRoot.querySelector('textarea');
      if (ta) {
        ta.style.height = '';
        ta.focus();
      }
    }
  }

  toggleExpand(idx) {
    this.expanded = { ...this.expanded, [idx]: !this.expanded[idx] };
    this.requestUpdate();
  }

  render() {
    return html`
      <div class="w-full max-w-2xl mx-auto flex flex-col min-h-screen pt-8 pb-[110px] px-2 sm:px-0">
        <div class="flex flex-col gap-4 px-0 pt-0 pb-2">
          ${this.messages.map((msg, idx) => html`
            <div data-msg-idx="${idx}">
              ${renderMessage(msg, idx, this.expanded, this.toggleExpand.bind(this))}
            </div>
          `)}
          ${this.isTyping
            ? html`<div class="italic text-gray-400 px-2">Assistant is typing...</div>`
            : nothing}
          <div style="height: 80px;"></div>
        </div>
        <div class="fixed bottom-0 left-0 w-full flex justify-center pointer-events-none z-50">
          <div class="w-full max-w-2xl px-2 sm:px-0 pb-6 pointer-events-auto">
            <div class="flex items-end bg-white/90 dark:bg-gray-900/90 shadow-xl border border-gray-200 dark:border-gray-800 rounded-lg px-3 py-2">
              <textarea
                class="flex-1 resize-none border-0 bg-transparent outline-none text-lg px-2 py-2 rounded-lg focus:ring-0 focus:outline-none max-h-[50vh] min-h-[44px] transition-all"
                style="overflow:hidden;box-shadow:none;"
                rows="1"
                .value=${this.input}
                @input=${this.handleInput}
                placeholder="Type your message…"
                aria-label="Chat input"
              ></textarea>
              <sl-button
                variant=${this.input.trim() ? "primary" : "default"}
                size="large"
                circle
                class="ml-2 transition-all"
                ?disabled=${!this.input.trim()}
                @click=${this.sendMessage}
                style="--sl-color-primary: #2563eb;"
              >
                <sl-icon name="arrow-up"></sl-icon>
              </sl-button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('ui-chat', UiChat);
export { UiChat };