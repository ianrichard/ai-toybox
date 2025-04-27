import { LitElement, html } from 'lit';
import { discover } from 'https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.20.1/cdn/shoelace-autoloader.js';

export class BaseElement extends LitElement {
   static useShadow = false;
   static baseClass = 'my-5'; // Default class, can be overridden in subclasses

   createRenderRoot() {
      return this.constructor.useShadow ? super.createRenderRoot() : this;
   }

   firstUpdated() {
      super.firstUpdated?.();
      discover(this.shadowRoot ?? this);
   }

   render() {
      // Subclasses can override this.renderContent()
      return html`
         <div class="${this.constructor.baseClass}">
            ${this.renderContent ? this.renderContent() : ''}
         </div>
      `;
   }
}
