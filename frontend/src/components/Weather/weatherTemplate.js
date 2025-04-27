import { html } from 'lit';
import {
   getWeatherDescription,
   getWeatherIcon,
   formatTime,
   formatShortDate,
} from './weatherUtils.js';

// Utility: wraps content in <sl-skeleton> if not loaded, otherwise renders content as-is
function renderContent(loaded, content) {
   return loaded ? content : '-';
}

export function renderWeather({
   location,
   mockMode,
   current_weather,
   hourly,
   daily,
   currentHour,
   loading = false,
}) {
   const isLoaded = !loading && current_weather && hourly && daily;

   // Current weather
   const currentWeatherCode = isLoaded ? current_weather.weathercode : null;
   const currentTemp = isLoaded ? Math.round(current_weather.temperature) : '';
   const weatherDesc = isLoaded ? getWeatherDescription(currentWeatherCode) : '';

   // Hourly forecast
   let hourlyForecast = [];
   let startIndex = 0;
   if (isLoaded) {
      const currentTimeIndex = hourly.time.findIndex(
         (time) => new Date(time).getHours() >= currentHour,
      );
      startIndex = currentTimeIndex >= 0 ? currentTimeIndex : 0;
      hourlyForecast = hourly.time.slice(startIndex, startIndex + 8).map((time, idx) => {
         const arrayIndex = startIndex + idx;
         return {
            time,
            temp: Math.round(hourly.temperature_2m[arrayIndex]),
            code: hourly.weathercode[arrayIndex],
         };
      });
   } else {
      hourlyForecast = Array(8).fill({});
   }

   // Daily forecast
   const dailyCount = 5;
   let dailyForecast = [];
   if (isLoaded) {
      dailyForecast = daily.time.slice(0, dailyCount).map((day, idx) => ({
         day,
         code: daily.weathercode[idx],
         max: Math.round(daily.temperature_2m_max[idx]),
         min: Math.round(daily.temperature_2m_min[idx]),
      }));
   } else {
      dailyForecast = Array(dailyCount).fill({});
   }

   return html`
      <div class="p-4 pb-2">
         <!-- Current weather -->
         <div class="flex items-center justify-between">
            <div>
               <div class="flex items-center text-gray-600">
                  <sl-icon name="geo-alt" class="text-sm mr-1"></sl-icon>
                  <span class="text-lg font-medium"> ${renderContent(isLoaded, location)} </span>
                  ${mockMode && isLoaded
                     ? html`<span class="ml-2 text-xs bg-blue-100 text-blue-800 px-1 rounded"
                          >MOCK</span
                       >`
                     : ''}
               </div>
               <div class="text-5xl font-bold mt-1">
                  ${renderContent(isLoaded, html`${currentTemp}°`)}
               </div>
               <div class="text-gray-600 text-sm">${renderContent(isLoaded, weatherDesc)}</div>
            </div>
            <div>
               ${isLoaded
                  ? html`<sl-icon
                       name="${getWeatherIcon(currentWeatherCode)}"
                       style="font-size: 56px; color: #4b96ff;"
                    ></sl-icon>`
                  : html`<sl-skeleton
                       ><sl-icon name="circle" style="font-size: 56px;"></sl-icon
                    ></sl-skeleton>`}
            </div>
         </div>

         <!-- Weather details -->
         <div class="grid grid-cols-3 gap-2 mt-4 text-center text-sm">
            <div class="flex flex-col items-center">
               <sl-icon name="wind" class="mb-1 text-gray-600"></sl-icon>
               <div class="text-gray-600">
                  ${renderContent(isLoaded, isLoaded ? `${current_weather.windspeed} mph` : '')}
               </div>
            </div>
            <div class="flex flex-col items-center">
               <sl-icon name="moisture" class="mb-1 text-gray-600"></sl-icon>
               <div class="text-gray-600">
                  ${renderContent(
                     isLoaded,
                     isLoaded ? `${hourly.relativehumidity_2m?.[startIndex]} %` : '',
                  )}
               </div>
            </div>
            <div class="flex flex-col items-center">
               <sl-icon name="speedometer" class="mb-1 text-gray-600"></sl-icon>
               <div class="text-gray-600">
                  ${renderContent(
                     isLoaded,
                     isLoaded ? `${hourly.pressure_msl?.[startIndex]} hPa` : '',
                  )}
               </div>
            </div>
         </div>

         <!-- Hourly forecast -->
         <div class="mt-4 flex gap-4 overflow-x-auto py-2">
            ${hourlyForecast.map(
               (forecast, idx) => html`
                  <div class="flex flex-col items-center min-w-[60px]">
                     <div class="text-xs text-gray-600">
                        ${renderContent(isLoaded, forecast.time ? formatTime(forecast.time) : '')}
                     </div>
                     <div>
                        ${isLoaded && forecast.code !== undefined
                           ? html`<sl-icon
                                name="${getWeatherIcon(forecast.code)}"
                                class="my-1"
                                style="color: #4b96ff;"
                             ></sl-icon>`
                           : html`<sl-icon name="circle" class="my-1"></sl-icon>`}
                     </div>
                     <div class="text-sm font-medium">
                        ${renderContent(
                           isLoaded,
                           forecast.temp !== undefined ? `${forecast.temp}°` : '',
                        )}
                     </div>
                  </div>
               `,
            )}
         </div>
      </div>

      <!-- Daily forecast -->
      <div class="border-t border-gray-100 mt-2">
         ${dailyForecast.map(
            (dayObj, idx) => html`
               <div
                  class="flex items-center justify-between p-3 ${idx < dailyCount - 1
                     ? 'border-b border-gray-100'
                     : ''}"
               >
                  <div class="flex items-center">
                     <div class="w-24">
                        ${renderContent(
                           isLoaded,
                           idx === 0
                              ? html`<span class="font-medium">Today</span>`
                              : idx === 1
                                ? html`<span class="font-medium">Tomorrow</span>`
                                : html`<span class="font-medium"
                                     >${dayObj.day ? formatShortDate(dayObj.day) : ''}</span
                                  >`,
                        )}
                     </div>
                     <div>
                        ${isLoaded && dayObj.code !== undefined
                           ? html`<sl-icon
                                name="${getWeatherIcon(dayObj.code)}"
                                class="ml-1"
                                style="color: #4b96ff;"
                             ></sl-icon>`
                           : html`<sl-skeleton
                                ><sl-icon name="circle" class="ml-1"></sl-icon
                             ></sl-skeleton>`}
                     </div>
                  </div>
                  <div class="flex items-center gap-2">
                     <span class="font-medium">
                        ${renderContent(isLoaded, dayObj.max !== undefined ? `${dayObj.max}°` : '')}
                     </span>
                     <span class="text-gray-400 text-sm">
                        ${renderContent(isLoaded, dayObj.min !== undefined ? `${dayObj.min}°` : '')}
                     </span>
                  </div>
               </div>
            `,
         )}
      </div>
   `;
}
