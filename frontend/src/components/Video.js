import { html } from 'lit';
import { BaseElement } from '../core/BaseElement.js';

class VideoPlayer extends BaseElement {
   static properties = {
      poster: { type: String },
      src: { type: String },
   };

   constructor() {
      super();
      this.poster =
         'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80';
      this.src = 'https://www.w3schools.com/html/mov_bbb.mp4';
   }

   render() {
      return html`
         <div class="${this.constructor.baseClass}">
            <video controls class="w-full rounded" poster="${this.poster}">
               <source src="${this.src}" type="video/mp4" />
               Your browser does not support the video tag.
            </video>
            <div class="mt-2">
               <strong class="block text-lg font-bold">Sample Stock Video</strong>
               <p class="text-gray-600 text-sm mt-1">
                  This is a stock video for demonstration purposes.
               </p>
            </div>
         </div>
      `;
   }
}

customElements.define('ui-video-player', VideoPlayer);
