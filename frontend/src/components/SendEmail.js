import { html } from 'lit';
import { BaseElement } from '../core/BaseElement.js';

class Email extends BaseElement {
   static properties = {
      recipient: { type: String },
      message: { type: String },
      email: { type: String, state: true },
      body: { type: String, state: true },
   };

   constructor() {
      super();
      this.recipient = '';
      this.message = '';
      this.email = this.recipient || '';
      this.body = this.message || '';
   }

   updated(changed) {
      if (changed.has('recipient')) this.email = this.recipient || '';
      if (changed.has('message')) this.body = this.message || '';
   }

   render() {
      return html`
         <h3 class="text-xl my-2 font-bold">Send Email</h3>

         <form class="flex flex-col gap-4" @submit=${this.handleSend}>
            <sl-input
               label="Recipient Email"
               type="email"
               required
               value=${this.email}
               @sl-input=${(e) => (this.email = e.target.value)}
               placeholder="you@example.com"
            ></sl-input>

            <sl-textarea
               label="Message"
               required
               value=${this.body}
               @sl-input=${(e) => (this.body = e.target.value)}
               rows="6"
               placeholder="Type your message here..."
            ></sl-textarea>

            <div class="flex justify-end">
               <sl-button pill variant="primary" type="submit">Send</sl-button>
            </div>
         </form>
      `;
   }

   handleSend(e) {
      e.preventDefault();
      alert(`Email sent to ${this.email}!\n\nMessage:\n${this.body}`);
      this.email = this.recipient || '';
      this.body = this.message || '';
      this.requestUpdate();
   }
}

customElements.define('ui-send-email', Email);
