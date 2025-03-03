# EduCursos - Plataforma de Educación en Línea

## Descripción General
EduCursos es una plataforma de educación en línea que permite a los usuarios registrarse, iniciar sesión, inscribirse en cursos, y gestionar su perfil. Los administradores pueden gestionar usuarios, cursos, y generar reportes. La plataforma está desarrollada con Flask (Python) para el backend, SQLite para la base de datos, y HTML/CSS/JavaScript para el frontend.

## Estructura del Proyecto

### Archivos Principales
- **app.py**: Contiene la lógica principal de la aplicación Flask, incluyendo las rutas y la gestión de sesiones.
- **schema.py**: Define la estructura de la base de datos, incluyendo las tablas de usuarios, cursos, y registros de cursos.
- **utils.py**: Contiene funciones de utilidad como validación de email y contraseña, y la clase `DatabaseManager` para interactuar con la base de datos.
- **templates/**: Contiene los archivos HTML para las diferentes vistas de la plataforma.
- **static/**: Contiene archivos estáticos como CSS, JavaScript, e imágenes.

## Funcionalidades

### Autenticación y Registro
- **Registro de Usuarios**: Los usuarios pueden registrarse proporcionando un nombre, email, y contraseña. La contraseña se valida para asegurar que cumple con los requisitos de seguridad.
- **Inicio de Sesión**: Los usuarios pueden iniciar sesión con su email y contraseña. La sesión se mantiene activa hasta que el usuario cierra sesión.
- **Recuperación de Contraseña**: Los usuarios pueden recuperar su contraseña proporcionando su email. Se genera una contraseña temporal y se envía al usuario.

### Gestión de Cursos
- **Listado de Cursos**: Los cursos se muestran en la página principal con opciones para filtrar y ordenar por categoría, precio, y fecha.
- **Inscripción en Cursos**: Los usuarios pueden inscribirse en cursos desde la página principal o desde su portal de empleado.
- **Gestión de Cursos (Admin)**: Los administradores pueden añadir, editar, y eliminar cursos. También pueden subir imágenes para los cursos.

### Gestión de Usuarios
- **Perfil de Usuario**: Los usuarios pueden actualizar su perfil, incluyendo su nombre, email, teléfono, y contraseña.
- **Gestión de Usuarios (Admin)**: Los administradores pueden añadir, editar, y eliminar usuarios. También pueden cambiar el rol de los usuarios (usuario o administrador).

### Reportes
- **Exportación de Reportes**: Los administradores pueden exportar listas de usuarios y administradores a archivos Excel.

### Interfaz de Usuario
- **Navegación**: La barra de navegación permite a los usuarios acceder a diferentes secciones de la plataforma, como el inicio, cursos, y su perfil.
- **Modales**: Se utilizan modales para añadir y editar usuarios y cursos, y para mostrar mensajes de confirmación.

## Detalles Técnicos

### Base de Datos
- **Tabla de Usuarios**: Almacena la información de los usuarios, incluyendo su nombre, email, contraseña, rol, y teléfono.
- **Tabla de Cursos**: Almacena la información de los cursos, incluyendo el título, descripción, precio, categoría, y la imagen del curso.
- **Tabla de Registros de Cursos**: Almacena las inscripciones de los usuarios en los cursos.

### Backend (Flask)
- **Rutas**: Las rutas en `app.py` manejan las solicitudes HTTP y devuelven las respuestas adecuadas, como renderizar plantillas o devolver datos JSON.
- **Sesiones**: Las sesiones se utilizan para mantener el estado de autenticación del usuario y su rol.
- **Validación**: Se validan los datos de entrada, como el email y la contraseña, antes de procesarlos.

### Frontend (HTML/CSS/JavaScript)
- **Plantillas**: Las plantillas HTML se utilizan para generar las vistas de la plataforma. Se extienden de una plantilla base para mantener un diseño consistente.
- **JavaScript**: Se utiliza JavaScript para manejar la interacción del usuario, como la búsqueda y filtrado de cursos, y la gestión de modales.
- **Mapa**: Se utiliza Leaflet.js para mostrar un mapa con la ubicación de la empresa.

## Ejecución del Proyecto
1. **Instalación de Dependencias**: Asegúrate de tener Python instalado y ejecuta `pip install -r requirements.txt` para instalar las dependencias necesarias.
2. **Ejecución de la Aplicación**: Ejecuta `python app.py` para iniciar la aplicación Flask.
3. **Acceso a la Plataforma**: Abre tu navegador y visita `http://localhost:5000` para acceder a la plataforma.

## Conclusión
EduCursos es una plataforma robusta y escalable para la gestión de cursos y usuarios en línea. Con su interfaz intuitiva y funcionalidades completas, es una solución ideal para instituciones educativas que buscan ofrecer cursos en línea.
