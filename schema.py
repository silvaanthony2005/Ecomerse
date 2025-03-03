USER_TABLE = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name_surname VARCHAR(50) NOT NULL,
        email_user VARCHAR(50) NOT NULL UNIQUE,
        pass_user VARCHAR NOT NULL,
        role VARCHAR(5) NOT NULL DEFAULT 'user',
        phone VARCHAR(20),
        created_user TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
'''

PRODUCT_TABLE = '''
    CREATE TABLE IF NOT EXISTS cursos (
        id_curso INTEGER PRIMARY KEY,
        titulo VARCHAR(100) NOT NULL,
        descripcion TEXT,
        precio REAL NOT NULL,
        categoria VARCHAR(50),
        imagen_nombre VARCHAR(255),
        imagen_data BLOB,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''

REGISTRO_CURSOS_TABLE = '''
CREATE TABLE IF NOT EXISTS registro_cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id_curso)
);
'''

CURSOS = '''
    INSERT INTO cursos (titulo, descripcion, precio, categoria, imagen_nombre) VALUES
        ('Python para Principiantes', 'Aprende Python desde cero', 29.99, 'Programación', 'python_curso.jpg'),
        ('SQL Básico', 'Aprende SQL desde cero', 39.99, 'Base de datos', 'sql_curso.jpg'),
        ('HTML y CSS', 'Aprende desarrollo web desde cero', 19.99, 'Desarrollo web', 'html_curso.jpg'),
        ('JavaScript Moderno', 'Aprende JavaScript desde cero', 29.99, 'Programación', 'js_curso.jpg'),
        ('Java Programming', 'Aprende Java desde cero', 39.99, 'Programación', 'java_curso.jpg'),
        ('C# para Principiantes', 'Aprende C# desde cero', 49.99, 'Programación', 'csharp_curso.jpg'),
        ('React.js', 'Desarrollo frontend con React', 59.99, 'Desarrollo web', 'react_curso.jpg'),
        ('Node.js', 'Desarrollo backend con Node.js', 49.99, 'Programación', 'node_curso.jpg'),
        ('Marketing Digital', 'Estrategias de marketing online', 39.99, 'Marketing', 'marketing_curso.jpg'),
        ('Diseño UX/UI', 'Diseño de interfaces', 44.99, 'Diseño', 'uxui_curso.jpg'),
        ('Angular Framework', 'Desarrollo con Angular', 54.99, 'Desarrollo web', 'angular_curso.jpg'),
        ('Vue.js', 'Desarrollo frontend con Vue', 49.99, 'Desarrollo web', 'vue_curso.jpg'),
        ('PHP y MySQL', 'Desarrollo web con PHP', 34.99, 'Programación', 'php_curso.jpg'),
        ('Docker', 'Contenedores y despliegue', 64.99, 'DevOps', 'docker_curso.jpg'),
        ('AWS Básico', 'Servicios en la nube', 69.99, 'Cloud Computing', 'aws_curso.jpg'),
        ('Data Science', 'Análisis de datos', 79.99, 'Ciencia de Datos', 'datascience_curso.jpg'),
        ('Machine Learning', 'Aprendizaje automático', 89.99, 'Inteligencia Artificial', 'ml_curso.jpg'),
        ('Flutter', 'Desarrollo de apps móviles', 59.99, 'Desarrollo Móvil', 'flutter_curso.jpg'),
        ('Git y GitHub', 'Control de versiones', 29.99, 'Desarrollo', 'git_curso.jpg'),
        ('Ciberseguridad', 'Seguridad informática', 69.99, 'Seguridad', 'security_curso.jpg')
'''