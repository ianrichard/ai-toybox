import { LitElement, html } from 'lit';

export class BaseElement extends LitElement {
   static useShadow = false;
   static baseClass = 'my-5'; // Default class, can be overridden in subclasses

   createRenderRoot() {
      return this.constructor.useShadow ? super.createRenderRoot() : this;
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
