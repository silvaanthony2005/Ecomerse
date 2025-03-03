// selecciona elementos del DOM pasandole alguna especificacion com el id
function getElement(selector) {
    return document.querySelector(selector);
}

// Esta función agrega un evento a un elemento del DOM  y verifica si el elemento existe. Si el elemento no existe, no hace nada.
function addEventListenerSafe(element, event, handler) {
    if (element) {
        element.addEventListener(event, handler);
    }
}

// Esta función se ejecuta cuando el documento HTML ha terminado de cargarse. Se utiliza para inicializar los elementos de la página.
document.addEventListener('DOMContentLoaded', function() {
    // Navegación
    document.querySelectorAll('.nav-links a').forEach(link => {     // selecciona a todos los elemetos con la clase nav-links y les agrega un evento de clic.
        addEventListenerSafe(link, 'click', function(e) {
            if (this.classList.contains('logout')) return;          // Si el enlace tiene la clase logout, no hace nada.
            
            e.preventDefault();                                     // Evita que el enlace se comporte como un enlace normal (es decir, no redirige a otra página).
            const sectionId = this.dataset.section;
            
            document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));       // Obtiene el ID de la sección que se debe mostrar a partir del atributo data-section del enlace.
            this.classList.add('active');
            
            document.querySelectorAll('.section').forEach(section => section.classList.remove('active')); // Elimina la clase active de todos los enlaces y secciones.
            const targetSection = getElement(`#${sectionId}`);
            if (targetSection) targetSection.classList.add('active');                                     // Agrega la clase active al enlace actual y a la sección correspondiente.
        });
    });

    // Esta función selecciona el formulario con la clase profile-form y le agrega un evento de envío.
    const profileForm = getElement('.profile-form');                        
    addEventListenerSafe(profileForm, 'submit', function(e) {
        const newPassword = getElement('#new_password')?.value;
        const confirmPassword = getElement('#confirm_password')?.value;     // Obtiene los valores de los campos de contraseña y confirmación de contraseña.
        // evalua si no es vacio   //evalua si son distintas
        if (newPassword && newPassword !== confirmPassword) {               // Si las contraseñas no coinciden, evita que el formulario se envíe y muestra un mensaje de alerta.
            e.preventDefault();
            alert('Las contraseñas no coinciden');
        }
    });
});

// funcion para cerrar el modal
function closeModal(modalId) {                               
    document.getElementById(modalId).style.display = 'none';    // se oculta el modal con el parámetro none
}

// Cerrar modal con la X o clicking fuera
document.querySelectorAll('.modal').forEach(modal => {          //selecciona todos los elementos de la clase modal.
    modal.addEventListener('click', function(e) {               
        if (e.target === this || e.target.classList.contains('close')) {       // verifica si el elemento al que se le hizo clic está dentro del modal o si tiene la clase close  
            this.style.display = 'none';                                       
        }
    });
});

// Exportar a Excel

async function exportarReporteUsuarios() {
    try {
        const response = await fetch('/api/exportar/usuarios');
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'usuarios.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Mostrar notificación de éxito
        alert('Exportación completada exitosamente');
    } catch (error) {
        console.error('Error al exportar usuarios:', error);
        alert('Error al exportar los usuarios. Por favor intente nuevamente.');
    }
}

// Funciones para usuarios
async function eliminarUsuario(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este usuario?')) return;
    
    try {
        const response = await fetch(`/api/usuario/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Error al eliminar usuario');
        
        // Eliminar la fila de la tabla
        const row = document.querySelector(`tr[data-id="${id}"]`);
        if (row) {
            row.remove();
            alert('Usuario eliminado exitosamente');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el usuario');
    }
}

// Funciones para administradores
async function eliminarAdministrador(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este administrador?')) return;
    
    try {
        const response = await fetch(`/api/usuario/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Error al eliminar administrador');
        
        // Eliminar la fila de la tabla
        const row = document.querySelector(`tr[data-id="${id}"]`);
        if (row) {
            row.remove();
            alert('Administrador eliminado exitosamente');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el administrador');
    }
}

// Mostrar modal para añadir administrador
function showModalAdmin(modalId) {
    const modal = document.getElementById(modalId);
    const form = document.getElementById('admin-form');
    
    // Resetear el formulario
    form.reset();
    form.method = 'POST';
    form.action = '/add_admin';
    form.onsubmit = null;
    
    modal.style.display = 'block';
}

// Funciones para cursos
function showModalCurso(modalId) {
    const modal = document.getElementById(modalId);
    const form = document.getElementById('curso-form');
    
    // Resetear el formulario
    form.reset();
    form.method = 'POST';
    form.action = '/admin/curso/nuevo';
    form.onsubmit = null;
    
    // Cambiar el título
    modal.querySelector('h2').textContent = 'Añadir Curso';
    
    // Limpiar previsualización de imagen
    const preview = document.querySelector('.image-preview');
    if (preview) {
        preview.style.display = 'none';
        preview.src = '';
    }
    
    modal.style.display = 'block';
}

async function editarCurso(id) {
    try {
        const response = await fetch(`/admin/curso/${id}`);
        if (!response.ok) throw new Error('Error al obtener datos del curso');
        
        const curso = await response.json();
        
        const modal = document.getElementById('add-curso-modal');
        modal.style.display = 'block';
        
        const form = document.getElementById('curso-form');
        form.curso_id.value = id;
        form.titulo.value = curso.titulo;
        form.descripcion.value = curso.descripcion;
        form.precio.value = curso.precio;
        form.categoria.value = curso.categoria;
        
        // Cambiar el título y la acción del formulario
        modal.querySelector('h2').textContent = 'Editar Curso';
        form.action = `/admin/curso/${id}/editar`;
        
        // Mostrar imagen actual si existe
        if (curso.imagen_nombre) {
            const preview = document.querySelector('.image-preview');
            if (preview) {
                preview.src = `/curso/imagen/${id}`;
                preview.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar los datos del curso');
    }
}

async function eliminarCurso(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este curso?')) return;
    
    try {
        const response = await fetch(`/admin/curso/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Error al eliminar curso');
        
        const row = document.querySelector(`tr[data-id="${id}"]`);
        if (row) {
            row.remove();
            alert('Curso eliminado exitosamente');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el curso');
    }
}

// Previsualización de imagen
document.getElementById('imagen')?.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.querySelector('.image-preview');
            if (!preview) {
                const img = document.createElement('img');
                img.className = 'image-preview';
                this.parentElement.appendChild(img);
            }
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

function showEditUserModal(userId, userName, userEmail, userPhone, userRole) {
    const modal = document.getElementById('edit-user-modal');
    modal.style.display = 'block';

    // Actualizar el formulario con los datos del usuario
    const form = document.getElementById('edit-user-form');
    form.action = `/edit_user/${userId}`;  // Actualizar la URL con el user_id
    
    document.getElementById('edit_user_id').value = userId;
    document.getElementById('edit_user_name').value = userName;
    document.getElementById('edit_user_email').value = userEmail;
    document.getElementById('edit_user_phone').value = userPhone;
}

function showAddUserModal() {
    const modal = document.getElementById('add-user-modal');
    modal.style.display = 'block';
}

function closeModal() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => modal.style.display = 'none');
}

window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
}

async function exportarReporteAdministradores() {
    try {
        const response = await fetch('/api/exportar/administradores');
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'administradores.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Mostrar notificación de éxito
        alert('Exportación completada exitosamente');
    } catch (error) {
        console.error('Error al exportar administradores:', error);
        alert('Error al exportar los administradores. Por favor intente nuevamente.');
    }
}