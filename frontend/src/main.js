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
