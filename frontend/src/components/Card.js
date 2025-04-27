import { html } from 'lit';
import { BaseElement } from '../core/BaseElement.js';

class Card extends BaseElement {
   static useShadow = true;

   render() {
      return html`
         <sl-card class="shadow-lg max-w-lg mx-auto my-6 p-0">
            <slot></slot>
         </sl-card>
      `;
   }
}

customElements.define('ui-card', Card);
