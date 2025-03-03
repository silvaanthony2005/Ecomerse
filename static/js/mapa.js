document.addEventListener('DOMContentLoaded', function() {
    // Coordenadas de la ubicación
    const coordenadas = {
        lat: 10.495145,
        lng: -66.829104
    };
    
    // Inicializar el mapa
    const map = L.map('map').setView([coordenadas.lat, coordenadas.lng], 19);
    
    // Añadir la capa de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Añadir un marcador en la ubicación
    L.marker([coordenadas.lat, coordenadas.lng])
        .addTo(map)
        .bindPopup('¡Nuestra ubicación!')
        .openPopup();
}); 