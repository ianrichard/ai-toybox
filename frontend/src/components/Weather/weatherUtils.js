import { CONFIG } from './weatherConfig.js';

export function getWeatherDescription(code) {
   return CONFIG.weatherIcons[code] || 'Unknown';
}

export function getWeatherIcon(code) {
   return CONFIG.weatherIcons[code] || 'circle';
}

export function formatTime(isoString) {
   const date = new Date(isoString);
   return date.toLocaleTimeString([], { hour: 'numeric', hour12: true });
}

export function formatDay(isoString) {
   const date = new Date(isoString);
   return date.toLocaleDateString([], { weekday: 'long' });
}

export function formatShortDate(isoString) {
   const date = new Date(isoString);
   return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
}
