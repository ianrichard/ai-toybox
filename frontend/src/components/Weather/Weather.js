import { html } from 'lit';
import { BaseElement } from '../../core/BaseElement.js';
import { MOCK_DATA } from './weatherMocks.js';
import { fetchCoordinates, fetchWeather } from './weatherApi.js';
import { renderWeather } from './weatherTemplate.js';

export class WeatherWidget extends BaseElement {
   static properties = {
      mockMode: { type: Boolean },
      location: { type: String },
      lat: { type: Number },
      lon: { type: Number },
      weatherData: { type: Object },
      loading: { type: Boolean },
      currentHour: { type: Number },
   };

   constructor() {
      super();
      this.mockMode = true;
      this.location = '';
      this.lat = null;
      this.lon = null;
      this.weatherData = null;
      this.loading = true;
      this.currentHour = new Date().getHours();
   }

   connectedCallback() {
      super.connectedCallback();
      this.updateLocationDefaults();
   }

   async firstUpdated() {
      if (this.mockMode) {
         this.useMockData();
      } else {
         await this.useRealData();
      }
   }

   useMockData() {
      setTimeout(() => {
         this.weatherData = MOCK_DATA;
         this.loading = false;
      }, 800);
   }

   async useRealData() {
      if (!this.lat || !this.lon) {
         await this.fetchLatLonFromLocation();
      }
      await this.fetchWeatherData();
   }

   async fetchLatLonFromLocation() {
      if (!this.location) return;
      const coords = await fetchCoordinates(this.location);
      if (coords) {
         this.lat = coords.lat;
         this.lon = coords.lon;
      }
   }

   async fetchWeatherData() {
      if (!this.lat || !this.lon) return;
      this.loading = true;
      const data = await fetchWeather(this.lat, this.lon);
      if (data) {
         this.weatherData = data;
      }
      this.loading = false;
   }

   render() {
      return renderWeather({
         location: this.location,
         mockMode: this.mockMode,
         ...this.weatherData,
         currentHour: this.currentHour,
         loading: this.loading,
      });
   }
}

customElements.define('ui-weather-widget', WeatherWidget);
