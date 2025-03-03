// Variable global para almacenar todos los cursos
let allCourses = [];

// Función para inicializar los cursos
function initializeCourses() {
    allCourses = Array.from(document.querySelectorAll('.curso-card')).map(card => ({
        element: card.parentElement,
        title: card.querySelector('.card-title').textContent.toLowerCase(),
        description: card.querySelector('.card-text').textContent.toLowerCase(),
        price: parseFloat(card.querySelector('.card-text strong').textContent.replace('$', '')),
        category: card.querySelector('.card-text').textContent.toLowerCase(),
        date: new Date(card.dataset.date)
    }));
}

// Función para mostrar los cursos
function displayCourses(courses) {
    const container = document.getElementById('cursosContainer');
    container.innerHTML = '';
    courses.forEach(curso => {
        container.appendChild(curso.element);
    });
}

// Función para filtrar y ordenar cursos
function filterAndSortCourses() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filterValue = document.getElementById('filterSelect').value;
    
    // Aplicar filtro de búsqueda
    let filteredCourses = allCourses.filter(curso => 
        curso.title.includes(searchTerm) || 
        curso.description.includes(searchTerm)
    );

    // Aplicar ordenamiento
    filteredCourses.sort((a, b) => {
        switch(filterValue) {
            case 'recent':
                return b.date - a.date;
            case 'price_asc':
                return a.price - b.price;
            case 'price_desc':
                return b.price - a.price;
            case 'programming':
                return a.category.includes('programación') ? -1 : 1;
            case 'web':
                return a.category.includes('desarrollo web') ? -1 : 1;
            case 'data':
                return a.category.includes('ciencia de datos') ? -1 : 1;
            case 'design':
                return a.category.includes('diseño') ? -1 : 1;
            case 'marketing':
                return a.category.includes('marketing') ? -1 : 1;
            default:
                return 0;
        }
    });

    // Mostrar los cursos filtrados y ordenados
    document.getElementById('loadingIndicator').classList.add('active');
    setTimeout(() => {
        document.getElementById('loadingIndicator').classList.remove('active');
        displayCourses(filteredCourses);
    }, 300);
}

// Inicializar los cursos al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    initializeCourses();
    
    // Event listeners
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        filterAndSortCourses();
    });

    document.getElementById('filterSelect').addEventListener('change', filterAndSortCourses);
    
    // Evento para el input de búsqueda
    document.getElementById('searchInput').addEventListener('input', function() {
        filterAndSortCourses();
    });
});

// Función para registrar en curso
async function registrarEnCurso(curso_id) {
    try {
        const response = await fetch(`/registrar_curso/${curso_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            alert('Registro en el curso exitoso');
            window.location.href = '/portal_empleado';
        } else {
            const data = await response.json();
            alert(data.error || 'Error al registrarse en el curso');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al registrarse en el curso');
    }
}

async function sendMessage() {
    const userInput = document.getElementById('chatInput').value;
    if (!userInput.trim()) return;

    try {
        const response = await fetch('/get_bot_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userInput })
        });

        const data = await response.json();
        if (data.response) {
            // Mostrar la respuesta en el chat
            addMessageToChat('bot', data.response);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Hubo un error al comunicarse con el servidor.');
    }
}