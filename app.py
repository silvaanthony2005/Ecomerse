from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from utils import DatabaseManager, validar_email, validar_password
import os
import pandas as pd                                     # Manipular datos y convertirlo a excel
from io import BytesIO                                  # Leer y escribir datos en memoria en lugar de en archivos
from functools import wraps                             # Realizar operaciones de logging, autenticación y autorización en funciones sin alterar su comportamiento original
from flask import after_this_request
from werkzeug.utils import secure_filename
import io

app = Flask(__name__,
            template_folder='templates',                # Carpeta donde están los templates
            static_folder='static')                     # Carpeta donde están los archivos estáticos
app.secret_key = os.urandom(24)                         # touken de seguridad verificando las cookies de sesión
db = DatabaseManager()                                  # Controlar base de datos

# Añadir ruta principal
@app.route('/')
def home():
    # Obtener parámetros de filtrado
    filter_type = request.args.get('filter', 'recent')
    search_term = request.args.get('search', '')

    # Obtener los cursos desde la base de datos
    cursos = db.get_all_cursos()

    # Aplicar filtros
    if search_term:
        cursos = [curso for curso in cursos if 
                 search_term.lower() in curso['titulo'].lower() or 
                 search_term.lower() in curso['descripcion'].lower()]

    if filter_type == 'recent':
        cursos.sort(key=lambda x: x['id'], reverse=True)
    elif filter_type == 'price_asc':
        cursos.sort(key=lambda x: x['precio'])
    elif filter_type == 'price_desc':
        cursos.sort(key=lambda x: x['precio'], reverse=True)
    elif filter_type in ['programming', 'web', 'data', 'design', 'marketing']:
        cursos = [curso for curso in cursos if 
                 filter_type in curso['categoria'].lower()]

    return render_template('home.html', cursos=cursos)
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        success, role = db.verify_user(email, password)
        if success:
            session['user_email'] = email
            session['user_role'] = role  # Almacena el rol en la sesión
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form.get('phone', '')  # Obtener el teléfono si está presente

        # Validaciones
        if not validar_email(email):
            flash('Formato de email inválido', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')

        is_valid_password, msg = validar_password(password)
        if not is_valid_password:
            flash(msg, 'error')
            return render_template('register.html')

        if db.email_exists(email):
            flash('El email ya está registrado', 'error')
            return render_template('register.html')

        # Registrar usuario como usuario normal
        success, message = db.register_user(username, email, phone, 'user', password)
        if success:
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
            return render_template('register.html')

    return render_template('register.html')

# Añadir  decorador para proteger rutas y toma una funcion como argumento
def login_required(f):
    @wraps(f)                                                                           # Decorador que se usa para preservar la metadata de la funcion original
    def decorated_function(*args, **kwargs):                                            # Funcion que se ejecuta en vez de la funcion original pero contiene los mismo argumentos de la original
        @after_this_request                                                             # La funcion se ejecutara despues que se envie una respuesta HTTP 
        def add_header(response):                                                       # La funcion toma la respuesta HTTP como argumento
            # Prevenir cacheo del navegador
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'   # El navegador no almacena el cache, nisiquiera temporalmente y el navegador tiene que revalidad la respuesta con el servidor
            response.headers['Pragma'] = 'no-cache'                                     # Politicas de cacle en navegadores antiguos
            response.headers['Expires'] = '0'                                           # Establece que la respuesta HTTP expira automáticamente haciendo que se use las respuestas del servidor        
            return response
            
        if 'user_email' not in session:                                                 # Verificar si el usuario está autenticado
            flash('Debes iniciar sesión primero', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)                                                       # Si el usuario está autenticado, se ejecuta la función original f con los argumentos *args y **kwargs.
    return decorated_function

# Ruta del dashboard para usar el decorador
@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_role') == 'admin':
        # Lógica para el dashboard de administradores
        user = db.get_user_by_email(session['user_email'])
        usuarios = db.get_all_users(role='user')
        administradores = db.get_all_users(role='admin')
        cursos = db.get_all_cursos()
        
        return render_template('dashboard.html', 
                             user=user, 
                             usuarios=usuarios,
                             administradores=administradores,
                             cursos=cursos)
    else:
        # Lógica para el portal de empleados
        return redirect(url_for('portal_empleado'))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    current_password = request.form['current_password']
    new_password = request.form.get('new_password')
    nombre = request.form['nombre']
    email = request.form['email']
    phone = request.form['phone']

    # Verificar contraseña actual
    success, role = db.verify_user(session['user_email'], current_password)
    if not success:
        flash('Contraseña actual incorrecta', 'error')
        return redirect(url_for('dashboard'))

    # Validar nueva contraseña si se proporciona
    if new_password:
        is_valid_password, msg = validar_password(new_password)
        if not is_valid_password:
            flash(msg, 'error')
            return redirect(url_for('dashboard'))

    # Actualizar perfil
    success, message = db.update_user_profile(
        session['user_email'],
        nombre,
        email,
        phone,
        new_password if new_password else None
    )

    if success:
        session['user_email'] = email
        flash('Perfil actualizado exitosamente', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))

@app.route('/api/exportar/usuarios')
@login_required
def exportar_usuarios():
    try:
        usuarios = db.get_all_users(role='user')
        if not usuarios:
            flash('No hay datos para exportar', 'error')
            return redirect(url_for('dashboard'))
        
        # Crear DataFrame con los nuevos campos
        df = pd.DataFrame(usuarios)
        
        # Seleccionar y renombrar columnas
        columnas = {
            'name_surname': 'Nombre Completo',
            'email_user': 'Email',
            'phone': 'Teléfono',
            'created_user': 'Fecha de Registro',
            'role': 'Rol'
        }
        df = df[list(columnas.keys())]
        df = df.rename(columns=columnas)
        
        # Formatear fechas
        df['Fecha de Registro'] = pd.to_datetime(df['Fecha de Registro']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Usuarios', index=False)
            
            # Obtener libro y hoja de trabajo
            workbook = writer.book
            worksheet = writer.sheets['Usuarios']
            
            # Formato para encabezados
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9D9D9',
                'border': 1
            })
            
            # Aplicar formato y ajustar ancho de columnas
            for col_num, (col_name, col_data) in enumerate(df.items()):
                worksheet.write(0, col_num, col_name, header_format)
                
                # Determinar el ancho máximo
                max_len = max(
                    col_data.astype(str).apply(len).max(),  # Longitud de los datos
                    len(col_name)                          # Longitud del encabezado
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 50))  # Limitar a 50 caracteres
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_usuarios.xlsx'
        )
        
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()  # Limpia toda la sesión en lugar de solo eliminar user_email
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/recuperar-clave', methods=['GET', 'POST'])
def recuperar_clave():
    if request.method == 'POST':
        email = request.form['email ']
        if not validar_email(email):
            flash('Formato de email inválido', 'error')
            return render_template('recuperar-clave.html')
            
        if not db.email_exists(email):
            flash('Email no registrado', 'error')
            return render_template('recuperar-clave.html')
        
        # Contraseña por defecto
        nueva_password = "Ab12345$"
        
        # Actualizar la contraseña en la base de datos
        if db.update_password(email, nueva_password):
            flash(f'Tu contraseña ha sido restablecida a: {nueva_password}', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al restablecer la contraseña', 'error')
            
    return render_template('recuperar-clave.html')

@app.route('/api/usuario/<int:id>', methods=['DELETE'])
@login_required
def usuario_api(id):
    # Verificar que no se está intentando eliminar al usuario actual
    current_user = db.get_user_by_email(session['user_email'])
    if current_user and current_user['id'] == id:
        return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
    
    success = db.delete_user(id)
    return jsonify({'success': success})

@app.route('/portal_empleado')
@login_required
def portal_empleado():
    empleado = db.get_user_by_email(session['user_email'])
    cursos_inscritos = db.obtener_cursos_inscritos(empleado['id'])  # Obtener cursos inscritos
    return render_template('portal_empleado.html', empleado=empleado, inscripciones=cursos_inscritos)

@app.route('/update_empleado_profile', methods=['POST'])
@login_required
def update_empleado_profile():
    # Obtener el email del usuario actual desde la sesión
    current_email = session['user_email']
    
    # Obtener los datos del formulario
    current_password = request.form['current_password']
    new_password = request.form.get('new_password')
    name_surname = request.form['name_surname']
    email = request.form['email']
    phone = request.form['phone']

    # Verificar contraseña actual
    if not db.verify_user(current_email, current_password)[0]:
        flash('Contraseña actual incorrecta', 'error')
        return redirect(url_for('portal_empleado'))

    # Verificar si el nuevo email ya existe (excepto si es el mismo)
    if email != current_email and db.email_exists(email):
        flash('El email ya está registrado', 'error')
        return redirect(url_for('portal_empleado'))

    # Actualizar perfil
    success, message = db.update_user_profile(
        current_email,
        name_surname,
        email,
        phone,
        new_password if new_password else None
    )

    if success:
        session['user_email'] = email  # Actualizar el email en la sesión si cambió
        flash('Perfil actualizado exitosamente', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('portal_empleado'))

@app.route('/curso/imagen/<int:id_curso>')
def curso_imagen(id_curso):
    """Sirve la imagen del curso desde la base de datos"""
    resultado = db.get_curso_imagen(id_curso)
    if resultado and resultado[0]:
        return send_file(
            io.BytesIO(resultado[0]),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=resultado[1]
        )
    return send_file('static/images/default_course.jpg', mimetype='image/jpeg')

@app.route('/admin/cursos')
@login_required
def admin_cursos():
    """Página de administración de cursos"""
    if session.get('user_role') != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    cursos = db.get_all_cursos()
    return redirect(url_for('dashboard', cursos=cursos))

@app.route('/admin/curso/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_curso():
    """Añadir nuevo curso"""
    if session.get('user_role') != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        datos = {
            'titulo': request.form['titulo'],
            'descripcion': request.form['descripcion'],
            'precio': request.form['precio'],
            'categoria': request.form['categoria']
        }
        imagen = request.files.get('imagen')
        
        success, message = db.add_curso(datos, imagen)
        flash(message, 'success' if success else 'error')
        return redirect(url_for('admin_cursos'))
    
    return render_template('curso_form.html')

@app.route('/admin/curso/<int:id>', methods=['GET'])
@login_required
def get_curso(id):
    """Obtiene los datos de un curso específico"""
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    curso = db.get_curso(id)
    if curso is None:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    return jsonify(curso)

@app.route('/admin/curso/<int:id>/editar', methods=['POST'])
@login_required
def editar_curso(id):
    """Edita un curso existente"""
    if session.get('user_role') != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('login'))
    
    datos = {
        'titulo': request.form['titulo'],
        'descripcion': request.form['descripcion'],
        'precio': request.form['precio'],
        'categoria': request.form['categoria']
    }
    
    imagen = request.files.get('imagen')
    success, message = db.update_curso(id, datos, imagen)
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('dashboard'))

@app.route('/admin/curso/<int:id>', methods=['DELETE'])
@login_required
def eliminar_curso(id):
    """Elimina un curso"""
    if session.get('user_role') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    success, message = db.delete_curso(id)
    return jsonify({'success': success, 'message': message})

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    if session.get('user_role') != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('dashboard'))

    user_name = request.form['user_name']
    user_email = request.form['user_email']
    user_phone = request.form['user_phone']
    user_role = request.form['user_role']

    # Validaciones
    if not validar_email(user_email):
        flash('Formato de email inválido', 'error')
        return redirect(url_for('dashboard'))

    if db.email_exists(user_email):
        flash('El email ya está registrado', 'error')
        return redirect(url_for('dashboard'))

    # Registrar usuario con el rol especificado
    success, message = db.register_user(user_name, user_email, user_phone, role=user_role)
    if success:
        flash('Usuario añadido exitosamente.', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))

@app.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if session.get('user_role') != 'admin':
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('dashboard'))

    user_name = request.form['user_name']
    user_email = request.form['user_email']
    user_phone = request.form['user_phone']

    # Obtener el usuario actual
    current_user = db.get_user_by_id(user_id)
    if not current_user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('dashboard'))

    # Verificar si el nuevo email ya existe (excepto si es el mismo)
    if user_email != current_user['email_user'] and db.email_exists(user_email):
        flash('El email ya está registrado', 'error')
        return redirect(url_for('dashboard'))

    # Actualizar usuario
    success, message = db.update_user(user_id, user_name, user_email, user_phone)
    if success:
        flash('Usuario actualizado exitosamente.', 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('dashboard'))

@app.route('/api/exportar/administradores')
@login_required
def exportar_administradores():
    try:
        # Obtener solo administradores
        administradores = db.get_all_users(role='admin')
        
        if not administradores:
            return jsonify({'error': 'No hay administradores para exportar'}), 404
        
        # Crear DataFrame
        df = pd.DataFrame(administradores)
        
        # Seleccionar y renombrar columnas
        columnas = {
            'name_surname': 'Nombre Completo',
            'email_user': 'Email',
            'phone': 'Teléfono',
            'created_user': 'Fecha de Registro'
        }
        df = df[list(columnas.keys())]
        df = df.rename(columns=columnas)
        
        # Formatear fechas
        df['Fecha de Registro'] = pd.to_datetime(df['Fecha de Registro']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Administradores', index=False)
            
            # Formato para encabezados
            workbook = writer.book
            worksheet = writer.sheets['Administradores']
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9D9D9',
                'border': 1
            })
            
            # Aplicar formato y ajustar ancho de columnas
            for col_num, (col_name, col_data) in enumerate(df.items()):
                worksheet.write(0, col_num, col_name, header_format)
                column_len = max(col_data.astype(str).apply(len).max(), len(col_name))
                worksheet.set_column(col_num, col_num, min(column_len + 2, 50))
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_administradores.xlsx'
        )
        
    except Exception as e:
        print(f"Error en exportar_administradores: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/registrar_curso/<int:curso_id>', methods=['POST'])
@login_required
def registrar_curso(curso_id):
    if session.get('user_role') != 'user':
        flash('Solo los usuarios pueden registrarse en cursos', 'error')
        return redirect(url_for('home'))
    
    user_id = db.get_user_by_email(session['user_email'])['id']
    success, message = db.registrar_usuario_en_curso(user_id, curso_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('portal_empleado'))  # Redirigir al portal del empleado

if __name__ == '__main__':          #se verifica si estamos en el archivo inicial
    app.run(debug=True, port= 300)             #lanzar app con el debug activado, o sea ver los cambios mientras se hace