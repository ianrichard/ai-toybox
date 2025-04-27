import { html } from 'lit';
import { BaseElement } from '../core/BaseElement.js';

class Alert extends BaseElement {
   render() {
      return html`
         <sl-alert open>
            <sl-icon slot="icon" name="info-circle"></sl-icon>
            This is a standard alert. You can customize its content and even the icon.
         </sl-alert>
      `;
   }
}

customElements.define('ui-alert', Alert);
