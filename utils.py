import re                           # para buscar patrones
import bcrypt
from sqlite3 import IntegrityError  # para valores repetidos en la base de datos
import sqlite3
from schema import USER_TABLE, PRODUCT_TABLE, CURSOS, REGISTRO_CURSOS_TABLE

def validar_email(email):
    """Valida el formato del email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None  #patrones al inicio de la cadena

def validar_password(password):
    """Valida que la contraseña cumpla con los requisitos"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):   #patrones en cualquier parte de la candena
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un caracter especial"
    return True, "Contraseña válida"

def hash_password(password):
    """Encripta la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Verifica si la contraseña coincide con el hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

class DatabaseManager:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.init_db()  # Crear tablas si no existen

    def init_db(self):
        """Inicializa la base de datos creando las tablas si no existen"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            # Crear tablas
            cursor.execute(USER_TABLE)
            cursor.execute(PRODUCT_TABLE)
            cursor.execute(REGISTRO_CURSOS_TABLE)

            # Verificar si la tabla cursos está vacía
            cursor.execute("SELECT COUNT(*) FROM cursos")
            count = cursor.fetchone()[0]
            
            # Solo insertar cursos si la tabla está vacía
            if count == 0:
                cursor.execute(CURSOS)
            
            conn.commit()
        
        # Crear un único administrador inicial
        self.create_initial_admin()

    def get_db(self):
        return sqlite3.connect(self.db_name)

    def create_initial_admin(self):
        """Crea un único administrador inicial si no existe"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT email_user FROM users WHERE email_user = ?', ('ejemplo@gmail.com',))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO users (name_surname, email_user, pass_user, role) VALUES
                        (?, ?, ?, ?)
                    ''', ('ejemplo', 'ejemplo@gmail.com', hash_password('Ab12345$'), 'admin'))
                    conn.commit()
        except Exception as e:
            print(f"Error al crear el administrador inicial: {str(e)}")

    def email_exists(self, email):
        """Verifica si el email ya existe en la base de datos"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT email_user FROM users WHERE email_user = ?', (email,))
            return cursor.fetchone() is not None

    def register_user(self, name_surname, email, phone, role='user', password=None):
        """Registra un nuevo usuario en la base de datos"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                hashed_password = hash_password(password) if password else hash_password('Ab12345$')
                cursor.execute('''
                    INSERT INTO users (name_surname, email_user, pass_user, phone, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name_surname, email, hashed_password, phone, role))
                conn.commit()
                return True, "Usuario registrado exitosamente"
        except IntegrityError:
            return False, "El email ya está registrado"
        except Exception as e:
            return False, f"Error al registrar usuario: {str(e)}"

    def verify_user(self, email, password):
        """Verifica las credenciales del usuario"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT pass_user, role FROM users WHERE email_user = ?', (email,))
            result = cursor.fetchone()
            if result and check_password(password, result[0]):
                return True, result[1]  # Retorna el rol del usuario
            return False, None

    def get_user_by_email(self, email):
        """Obtiene la información del usuario por email"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name_surname, email_user, phone, created_user 
                FROM users WHERE email_user = ?
            ''', (email,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name_surname': result[1],
                    'email_user': result[2],
                    'phone': result[3],
                    'created_user': result[4]
                }
            return None

    def get_user_by_id(self, user_id):
        """Obtiene la información del usuario por ID"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name_surname, email_user, phone, role 
                FROM users WHERE id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name_surname': result[1],
                    'email_user': result[2],
                    'phone': result[3],
                    'role': result[4]
                }
            return None

    def get_all_users(self, role=None):
        """Obtiene todos los usuarios, opcionalmente filtrados por rol"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT id, name_surname, email_user, phone, role, created_user 
                FROM users
            '''
            params = ()
            
            if role:
                query += ' WHERE role = ?'
                params = (role,)
            
            cursor.execute(query, params)
            columns = ['id', 'name_surname', 'email_user', 'phone', 'role', 'created_user']
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_user_profile(self, current_email, new_name, new_email, new_phone, new_password=None):
        """Actualiza el perfil del usuario"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                if new_password:
                    hashed_password = hash_password(new_password)
                    cursor.execute('''
                        UPDATE users 
                        SET name_surname = ?, email_user = ?, phone = ?, pass_user = ?
                        WHERE email_user = ?
                    ''', (new_name, new_email, new_phone, hashed_password, current_email))
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET name_surname = ?, email_user = ?, phone = ?
                        WHERE email_user = ?
                    ''', (new_name, new_email, new_phone, current_email))
                conn.commit()
                return True, "Perfil actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar perfil: {str(e)}"

    def delete_user(self, user_id):
        """Elimina un usuario por su ID"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
                return True
        except Exception:
            return False

    def get_all_cursos(self):
        """Obtiene todos los cursos de la base de datos"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id_curso, titulo, descripcion, precio, 
                           categoria, imagen_nombre 
                    FROM cursos 
                    ORDER BY id_curso ASC
                ''')
                cursos = cursor.fetchall()
                
                # Convertir los resultados a una lista de diccionarios
                cursos_list = []
                for curso in cursos:
                    cursos_list.append({
                        'id': curso[0],
                        'titulo': curso[1],
                        'descripcion': curso[2],
                        'precio': float(curso[3]),
                        'categoria': curso[4],
                        'imagen_nombre': curso[5]
                    })
                return cursos_list
        except Exception as e:
            print(f"Error al obtener cursos: {str(e)}")
            return []

    def check_cursos(self):
        """Verifica los cursos actuales en la base de datos"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cursos")
            return cursor.fetchall()

    def clear_cursos(self):
        """Limpia la tabla de cursos"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cursos")
            conn.commit()

    def add_curso(self, datos, imagen_file):
        """Añade un nuevo curso con imagen"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                imagen_data = imagen_file.read() if imagen_file else None
                imagen_nombre = imagen_file.filename if imagen_file else None
                
                cursor.execute('''
                    INSERT INTO cursos (titulo, descripcion, precio, categoria, 
                                      imagen_nombre, imagen_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datos['titulo'],
                    datos['descripcion'],
                    float(datos['precio']),
                    datos['categoria'],
                    imagen_nombre,
                    imagen_data
                ))
                conn.commit()
                return True, "Curso añadido exitosamente"
        except Exception as e:
            return False, f"Error al añadir curso: {str(e)}"

    def update_curso(self, id_curso, datos, imagen_file=None):
        """Actualiza un curso existente"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                
                if imagen_file:
                    imagen_data = imagen_file.read()
                    imagen_nombre = imagen_file.filename
                    cursor.execute('''
                        UPDATE cursos 
                        SET titulo = ?, descripcion = ?, precio = ?, 
                            categoria = ?, imagen_nombre = ?, imagen_data = ?
                        WHERE id_curso = ?
                    ''', (
                        datos['titulo'], datos['descripcion'], 
                        float(datos['precio']), datos['categoria'],
                        imagen_nombre, imagen_data, id_curso
                    ))
                else:
                    cursor.execute('''
                        UPDATE cursos 
                        SET titulo = ?, descripcion = ?, precio = ?, categoria = ?
                        WHERE id_curso = ?
                    ''', (
                        datos['titulo'], datos['descripcion'], 
                        float(datos['precio']), datos['categoria'], 
                        id_curso
                    ))
                
                conn.commit()
                return True, "Curso actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar curso: {str(e)}"

    def delete_curso(self, id_curso):
        """Elimina un curso"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cursos WHERE id_curso = ?', (id_curso,))
                conn.commit()
                return True, "Curso eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar curso: {str(e)}"

    def get_curso(self, id_curso):
        """Obtiene un curso específico"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id_curso, titulo, descripcion, precio, categoria, 
                           imagen_nombre 
                    FROM cursos 
                    WHERE id_curso = ?
                ''', (id_curso,))
                curso = cursor.fetchone()
                if curso:
                    return {
                        'id': curso[0],
                        'titulo': curso[1],
                        'descripcion': curso[2],
                        'precio': float(curso[3]),
                        'categoria': curso[4],
                        'imagen_nombre': curso[5]
                    }
                return None
        except Exception as e:
            print(f"Error al obtener curso: {str(e)}")
            return None

    def get_curso_imagen(self, id_curso):
        """Obtiene la imagen de un curso"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT imagen_data, imagen_nombre FROM cursos WHERE id_curso = ?', (id_curso,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener imagen: {str(e)}")
            return None

    def update_user(self, user_id, new_name, new_email, new_phone):
        """Actualiza la información del usuario"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET name_surname = ?, email_user = ?, phone = ?
                    WHERE id = ?
                ''', (new_name, new_email, new_phone, user_id))
                conn.commit()
                return True, "Usuario actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar usuario: {str(e)}"

    def registrar_usuario_en_curso(self, user_id, curso_id):
        """Registra a un usuario en un curso"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                # Verificar si el usuario ya está registrado en el curso
                cursor.execute('''
                    SELECT id FROM registro_cursos 
                    WHERE user_id = ? AND curso_id = ?
                ''', (user_id, curso_id))
                if cursor.fetchone():
                    return False, "El usuario ya está registrado en este curso"
                
                # Registrar al usuario en el curso
                cursor.execute('''
                    INSERT INTO registro_cursos (user_id, curso_id)
                    VALUES (?, ?)
                ''', (user_id, curso_id))
                conn.commit()
                return True, "Registro exitoso"
        except Exception as e:
            return False, f"Error al registrar usuario en el curso: {str(e)}"

    def obtener_cursos_inscritos(self, user_id):
        """Obtiene los cursos en los que está inscrito un usuario"""
        try:
            with self.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.id_curso, c.titulo, c.descripcion, c.precio, c.categoria, c.imagen_nombre
                    FROM cursos c
                    JOIN registro_cursos rc ON c.id_curso = rc.curso_id
                    WHERE rc.user_id = ?
                ''', (user_id,))
                cursos = cursor.fetchall()
                return [{
                    'id': curso[0],
                    'titulo': curso[1],
                    'descripcion': curso[2],
                    'precio': float(curso[3]),
                    'categoria': curso[4],
                    'imagen_nombre': curso[5]
                } for curso in cursos]
        except Exception as e:
            print(f"Error al obtener cursos inscritos: {str(e)}")
            return []

    def verificar_registro_curso(self, user_id, curso_id):
        """Verifica si un usuario está registrado en un curso"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM registro_cursos 
                WHERE user_id = ? AND curso_id = ?
            ''', (user_id, curso_id))
            return cursor.fetchone() is not None