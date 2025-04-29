import '@shoelace-style/shoelace/dist/themes/light.css';
// import '@shoelace-style/shoelace/dist/components/button/button.js';
// import '@shoelace-style/shoelace/dist/components/icon/icon.js';
import '@shoelace-style/shoelace/dist/shoelace.js';


import { setBasePath } from '@shoelace-style/shoelace/dist/utilities/base-path.js';

setBasePath('/node_modules/@shoelace-style/shoelace/dist');

// Import component entry points from each component folder
const componentModules = import.meta.glob('./components/*/index.js');

// Fall back to direct component files for any that don't use the folder structure yet
const legacyComponents = import.meta.glob('./components/*.js');

// Load all components
for (const path in componentModules) {
   componentModules[path]();
}

for (const path in legacyComponents) {
   legacyComponents[path]();
}

// Optional: Expose for debugging
window.__components__ = { ...componentModules, ...legacyComponents };
