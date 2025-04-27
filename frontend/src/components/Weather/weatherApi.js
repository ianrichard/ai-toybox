export async function fetchCoordinates(location) {
   if (!location) return null;
   try {
      const response = await fetch(
         `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}`,
      );
      const results = await response.json();
      if (results.length > 0) {
         return {
            lat: parseFloat(results[0].lat),
            lon: parseFloat(results[0].lon),
         };
      }
      return null;
   } catch (error) {
      console.error('Error fetching location data:', error);
      return null;
   }
}

export async function fetchWeather(lat, lon) {
   if (!lat || !lon) return null;
   try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=temperature_2m,weathercode,relativehumidity_2m,pressure_msl&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto&temperature_unit=fahrenheit`;
      const response = await fetch(url);
      return await response.json();
   } catch (error) {
      console.error('Error fetching weather data:', error);
      return null;
   }
}
