// This is the base template for all future Web Components in this system.
//
// - Components must extend BaseElement (Lit + Shoelace autoloader + Tailwind support)
// - Components must register using a "ui-" prefix to avoid naming collisions (e.g., <ui-component-name>)
// - Components should use Shoelace Web Components for UI primitives first
// - Tailwind utility classes are allowed for layout, spacing, or minor tweaks
// - All component markup must be semantic, slot-based where appropriate
// - IMPORTANT: Do not include comments of any sort unless something critically confusing

import { html } from 'lit';
import { BaseElement } from '../core/BaseElement.js'; // Always extend BaseElement for consistent behavior

class ComponentName extends BaseElement {
   render() {
      return html`
         <img
            slot="image"
            src="https://images.unsplash.com/photo-1559209172-0ff8f6d49ff7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=80"
            alt="Placeholder image"
            class="w-full h-48 object-cover"
         />

         <strong class="block text-xl font-bold mt-2">Hello World</strong>
         <p class="text-gray-600 text-sm mt-1">
            This is a starter component using Shoelace and Tailwind.
         </p>
         <small class="text-gray-400 block mt-1">Updated just now</small>

         <div slot="footer" class="flex justify-center items-center gap-4 mt-4">
            <sl-button variant="primary" pill @click=${this.sayHello}>Say Hello</sl-button>
            <sl-rating></sl-rating>
         </div>
      `;
   }

   sayHello() {
      alert('Hello from ComponentName component!');
   }
}

// Components must be registered using kebab-case with a "ui-" prefix.
customElements.define('ui-component-name', ComponentName);
