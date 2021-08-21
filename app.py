from flask import Flask,app,config,render_template,request,redirect,flash,url_for,session
from flask.sessions import SessionInterface
from flaskext.mysql import MySQL
from datetime import datetime
import os #Nos permite acceder a los archivos
from flask import send_from_directory #Acceso a las carpetas
validacion=False # Bandera de usuario registrado
usuario="" # Nombre de usuario

def estrellas(valor):
    puntaje=""
    i=0
    while i < valor:
        puntaje=puntaje+"*"
        i+=1
    return puntaje


app = Flask(__name__) # Inicialización de aplicación
app.secret_key="18980413Guille"
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost' # Configuración de host DB
app.config['MYSQL_DATABASE_USER']='root' # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD']='' # Contraseña DB

mysql.init_app(app) # Inicialización de SQL
CARPETA= os.path.join('fotos') # Referencia a la carpeta
app.config['CARPETA']=CARPETA # Indicamos que vamos a guardar esta ruta de la carpeta

#CREACION DE BASE DE DATOS Y TABLAS
conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS `herreria`;")
cursor.execute("CREATE TABLE IF NOT EXISTS `herreria`.`categorias` ( `id_categoria` INT(10) NOT NULL AUTO_INCREMENT , `categoria` VARCHAR(255) NOT NULL , `descripcion_c` VARCHAR(5000) NOT NULL , PRIMARY KEY (`id_categoria`))")
cursor.execute("CREATE TABLE IF NOT EXISTS `herreria`.`productos` ( `id_producto` INT(10) NOT NULL AUTO_INCREMENT , `id_categoria` INT(10) NOT NULL  , `nombre` VARCHAR(255) NOT NULL , `descripcion_p` VARCHAR(5000) NOT NULL , `precio` FLOAT NOT NULL , `costo_envio` FLOAT NOT NULL , `largo` FLOAT NOT NULL , `alto` FLOAT NOT NULL , `ancho` FLOAT NOT NULL , `foto` VARCHAR(5000) NOT NULL , PRIMARY KEY (`id_producto`) );")
cursor.execute("INSERT IGNORE `herreria`.`usuarios`(`Usuario`,`password`) VALUES ('guillermo', '123456789');")
cursor.execute("CREATE TABLE IF NOT EXISTS `herreria`.`recetas` ( `id` INT(10) NOT NULL AUTO_INCREMENT , `nombre` VARCHAR(50) NOT NULL , `nombreReceta` VARCHAR(50) NOT NULL , `porciones` INT(5) NOT NULL , `ingredientes` VARCHAR(5000) NOT NULL , `receta` VARCHAR(5000) NOT NULL , PRIMARY KEY (`id`))")
cursor.execute("CREATE TABLE IF NOT EXISTS `herreria`.`comentarios` ( `id` INT(10) NOT NULL AUTO_INCREMENT , `email` VARCHAR(255) NOT NULL , `nombre` VARCHAR(50) NOT NULL , `atencion` INT(2) NOT NULL , `calidad` INT(2) NOT NULL , `precio` INT(2) NOT NULL , `comentario` VARCHAR(5000) NOT NULL , PRIMARY KEY (`id`))")
conn.commit()

# PARTE PARA EL USUARIO_______________________________________________________________
# Renderización de pagina principal
@app.route("/")
def index():
    return render_template("vistas/index.html")

#Renderizacion de pagina base
@app.route("/base")
def base():
    return render_template("vistas/base.html")


# Renderizacion de pagina de productos
@app.route("/productos/<int:id_categoria>") # Recibe como parámetro el id de categoría
def productos(id_categoria):
    conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
    cursor = conn.cursor() # Almacenaremos lo que ejecutamos
    cursor.execute("SELECT * FROM `herreria`.`categorias`") # Buscar todas las categorías de la tabla "categorías"
    categorias=cursor.fetchall() # Guardar los datos obtenidos de la tabla "categorías"
    titulo=""
    if id_categoria==0: # Si no hay categoría seleccionada
        cursor.execute("SELECT * FROM `herreria`.`productos`, `herreria`.`categorias` WHERE`categorias`.`id_categoria`=`productos`.`id_categoria`ORDER BY nombre;") # Buscar todos los productos de la tabla "productos"
        titulo="TODOS LOS PRODUCTOS"
    else: # Si hay categoría seleccionada
        sql = "SELECT * FROM `herreria`.`productos` WHERE`id_categoria` LIKE %s ORDER BY nombre;"
        cursor.execute(sql,id_categoria) # Buscar los productos de la tabla de dicha categoría
        for categoria in categorias:
            if categoria[0]==id_categoria:
                titulo=categoria[1].upper()
    productos=cursor.fetchall() # Guardar los productos extraidos de la tabla "productos"
    conn.commit() # Cerrar conexión
    return render_template("vistas/productos.html", productos=productos, categorias=categorias, titulo=titulo) # Renderizar productos.html con la información obtenida

@app.route('/ubicacion', methods=['POST'])
def ubicacion():
   return render_template("vistas/ubicacion.html")

@app.route('/comentarios')
def comentarios():
    conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
    cursor = conn.cursor() # Almacenaremos lo que ejecutamos
    cursor.execute("SELECT * FROM `herreria`.`recetas`;")
    recetas=cursor.fetchall()
    cursor.execute("SELECT * FROM `herreria`.`comentarios`;")
    cali=cursor.fetchall()
    calificaciones=[]
    for i in cali:
        calificaciones.append(list(i))
    for calificacion in calificaciones:
        calificacion[3]=estrellas(calificacion[3])
        calificacion[4]=estrellas(calificacion[4])
        calificacion[5]=estrellas(calificacion[5])
        print(calificacion[3])
    print(len(cali),len(calificaciones), calificaciones )
    return render_template("vistas/comentarios.html",recetas=recetas,calificaciones=calificaciones)

@app.route('/cargaReceta')
def carga_receta():
   nombre=request.form['nombre']
   nombreReceta=request.form['nombre_receta']
   porciones=(request.form['porciones'])
   ingredientes=request.form['ingredientes']
   receta=request.form['receta']
   datos= (nombre, nombreReceta, porciones, ingredientes, receta)
   sql="INSERT INTO `herreria`.`recetas`(`nombre`,`nombreReceta`,`porciones`,`ingredientes`,`receta`) VALUES(%s,%s,%s,%s,%s)"
   conn =mysql.connect()
   cursor = conn.cursor()
   cursor.execute(sql,datos)
   conn.commit()
   return redirect('/comentarios')

@app.route('/cargaCalificacion', methods=['POST'])
def carga_calificacion():
   email=request.form['email']
   nombre=request.form['nombre']
   atencion=(request.form['atención'])
   calidad=(request.form['calidad'])
   precio=(request.form['precio'])
   comentario=request.form['comentario']
   datos= (email, nombre, atencion, calidad, precio, comentario)
   sql="INSERT INTO `herreria`.`comentarios`(`email`,`nombre`,`atencion`,`calidad`,`precio`,`comentario`) VALUES(%s,%s,%s,%s,%s,%s)"
   conn =mysql.connect()
   cursor = conn.cursor()
   cursor.execute(sql,datos)
   conn.commit()
   return redirect('/comentarios')

# FIN DE PARTE PARA EL USUARIO________________________________________________________


# PARTE PARA EL PROPIETARIO ___________________________________________________________

# Borrado de productos
@app.route('/destroy/<int:id>') # Recibe como parámetro el id del producto
def destroy(id):
    if "username" in session: # Si es usuario registrado
        conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT foto FROM `herreria`.`productos` WHERE id_producto=%s",id) # Buscamos la foto
        fila= cursor.fetchall() # Traemos toda la información
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Elimina la foto de la carpeta
        cursor.execute("DELETE FROM `herreria`.`productos` WHERE id_producto=%s", (id)) # Eliminamos el producto de la DB por su ID
        conn.commit() # Cerramos la conexión
        return redirect('/administracion') # Volvemos a la pagina de administración de DB
    else: # Si NO es usuario registrado
        return redirect('/') # Redireccionamos a Inicio

# Renderización de pagina de editado de productos
@app.route('/edit/<int:id>') # Recibe como parámetro el id del producto
def edit(id):
    if "username" in session: # Si es usuario registrado
        conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT * FROM `herreria`.`productos` WHERE id_producto=%s", (id)) # Buscamos el producto de la DB por su id
        producto=cursor.fetchall() # Traemos toda la información
        cursor.execute("SELECT * FROM `herreria`.`categorias`;") # Buscar todas las categorías de la tabla "categorías"
        categorias=cursor.fetchall() # Almacenamos lo que ejecutamos
        conn.commit() #Cerramos la conexión
        return render_template('propietario/edit.html', producto=producto[0],categorias=categorias) # Renderizar edit.html con la información obtenida
    else: # Si NO es usuario registrado
        return redirect('/') # Redireccionamos a Inicio

# Editado de productos
@app.route('/update', methods=['POST']) # Recibimos los datos desde el formulario de edición, del producto a editar
def update():
    if "username" in session: # Si es usuario registrado
        # Obtenemos los datos correspondientes y los almacenamos
        _nombre=request.form['txtNombre']
        _id_categoria=request.form['txtId_categoria']
        _costo_envio=request.form['txtCosto_envio']
        _largo=request.form['txtLargo']
        _alto=request.form['txtAlto']
        _ancho=request.form['txtAncho']
        _descripcion_p=request.form['txtDescripcion_p']
        _id_producto=request.form['txtId_producto']
        _foto=request.files['txtFoto']
        sql = "UPDATE `herreria`.`productos` SET `nombre`=%s , `id_categoria`=%s , `costo_envio`=%s , `largo`=%s , `alto`=%s , `ancho`=%s , `descripcion_p`=%s WHERE id_producto=%s;" # Definimos la actualización del producto
        datos=(_nombre, _id_categoria, _costo_envio, _largo, _alto, _ancho, _descripcion_p, _id_producto) # Definimos los nuevos valores del producto
        conn = mysql.connect() # Se conecta a la conexión mysql.init_app(app)
        now= datetime.now() # Obtenemos la fecha y la hora actuales, para definir el nombre de la foto, y evitar repetir este
        tiempo= now.strftime("%Y%H%M%S_") #dia mes horas minutos y segundos
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT foto FROM `herreria`.`productos`   WHERE id_producto=%s", _id_producto) #Buscamos la foto
        fila= cursor.fetchall() #Traemos toda la información
        extension=_foto.filename.split(".") # Recuperamos la extensión del archivo foto
        if _foto.filename !="": # Si el campo foto no esta vacío
            nuevoNombreFoto=tiempo+_nombre+"."+extension[1] # Renombramos la foto
            _foto.save("fotos/"+nuevoNombreFoto) # Guardamos la foto nueva
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Borramos la foto vieja
            data=(nuevoNombreFoto, _id_producto) # Definimos los valores a actualizar
            cursor.execute("UPDATE `herreria`.`productos` SET `foto`=%s WHERE id_producto=%s", data) # Definimos la sentencia para actualizar la foto
        cursor.execute(sql,datos) # Actualizamos la foto del producto
        conn.commit() #Cerramos la conexión
        return redirect('/administracion')  # Volvemos a la pagina de administración de DB
    else:  # Si NO es usuario registrado
        return redirect('/') # Redireccionamos a inicio

# Renderizacion pagina administracion
@app.route("/administracion")
def administracion():
    if "username" in session: # Si es usuario registrado
        conn = mysql.connect() # Se conecta a la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT * FROM `herreria`.`productos`, `herreria`.`categorias`   WHERE`categorias`.`id_categoria`=`productos`.`id_categoria`ORDER BY nombre;") # Buscamos todos los productos de la tabla
        productos=cursor.fetchall() # Almacenamos los resultados
        cursor.execute("SELECT `id_categoria`,`categoria`FROM `herreria`.`categorias`") # Buscamos el ID y el nombre de cada categoria
        categorias=cursor.fetchall() # Almacenamos los resultados
        conn.commit() # Cerramos conexión
        return render_template("/propietario/administracion.html",productos=productos,categorias=categorias) # Renderizamos administracion.html con los datos obtenidos
    else: # Si NO es usuario registrado
        return redirect('/login') # Redireccionamos a inicio

# Creación de productos y/o categoria y almacenado en tabla
@app.route('/store', methods=['POST']) # Recibimos los datos desde el formulario
def storage():
    if "username" in session: # Si es usuario registrado
        _nombre=request.form["txtNombre"].title()
        _id_categoria=int(request.form["txtId_categoria"])
        _foto=request.files["txtFoto"]
        _descripcion_p=request.form["txtDescripcion_p"]
        _precio=float(request.form["txtPrecio"])
        _costo_envio=float(request.form["txtCosto_envio"])
        _largo=float(request.form["txtLargo"])
        _alto=float(request.form["txtAlto"])
        _ancho=float(request.form["txtAncho"])
        _categoria=request.form["txtCategoria"].upper()
        _descripcion_c=request.form["txtDescripcion_c"]

        if _categoria !="": # Si el campo categoria no esta vacío
            conn=mysql.connect() # Realizamos la conexión con la DB
            cursor=conn.cursor()
            sql="INSERT INTO `herreria`.`categorias` (`id_categoria`,`categoria`,`descripcion_c`) VALUES (NULL,%s,%s)" # Definimos la creación de la nueva categoria
            datos=(_categoria,_descripcion_c) # Definimos los datos de la nueva categoria
            cursor.execute(sql,datos) # Ejecutamos la creación
            cursor.execute("SELECT id_categoria FROM `herreria`.`categorias` WHERE categoria=%s",(_categoria)) # Buscamos el ID de categoria de la nueva categoria
            _id_categoria=cursor.fetchall() # Asignamos ese valor a la variable correspondiente para el nuevo producto
            conn.commit() # Cerramos la conexión

        if _nombre=="" or _id_categoria=="" or _foto.filename=="" or _descripcion_p=="" or _precio=="" or _costo_envio=="" or _largo=="" or _alto=="" or _ancho=="": # Si alguno de los campos esta vacío
            flash("Debe rellenar todos los campos") # Creamos el mensaje para el propietario
            return redirect(url_for('administracion')) # Redirigimos a la pagina
        now=datetime.now() # Obtenemos la fecha para asignarla al nombre de la foto
        tiempo=now.strftime("%Y%H%M%S_") # Obtenemos de la fecha el año, la hora, los minutos y segundos
        extension=_foto.filename.split(".") # Obtenemos la extensión del archivo
        if _foto.filename !="": # Si el campo foto no esta vacío
            nuevoNombreFoto=tiempo+_nombre+"."+extension[1] # Creamos el nombre de la foto
            _foto.save("fotos/"+nuevoNombreFoto) # Guardamos la foto en la carpeta correspondiente

        datos=(_nombre,_id_categoria,_descripcion_p,_precio , _costo_envio, _largo, _alto, _ancho, nuevoNombreFoto) # Definimos los valores del producto
        sql="INSERT INTO `herreria`.`productos`  (`id_producto`, `nombre`, `id_categoria`, `descripcion_p`, `precio`, `costo_envio`, `largo`, `alto`, `ancho`, `foto`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s);" # Definimos la sentencia de creación del producto
        conn=mysql.connect() # Abrimos la conexión con la DB
        cursor=conn.cursor()
        cursor.execute(sql,datos) # Gurdamos en la DB el producto
        conn.commit() # Cerramos la conexión
        return redirect('/administracion') # Volvemos a la pagina de carga
    else: # Si NO es usuario registrado
        return redirect('/') # Redireccionamos al inicio

# Creacion de nuevo usuario
@app.route('/crear_usuario', methods=['POST']) # Recibimos los datos del formulario
def crear_usuario():
    if "username" in session: # Si es un usuario registrado
        nUsuario=request.form["txtUsuario"] # Nuevo usuario
        pUsuario=request.form['txtPassword'] # Password nuevo usuario
        usuario=nUsuario,pUsuario #Agrupamos los datos
        sql="INSERT INTO `herreria`.`usuarios` (`Usuario`, `password`) VALUES (%s, %s)" # Creamos la sentencia
        conn = mysql.connect() # Abrimos la conexión
        cursor = conn.cursor()
        cursor.execute("SELECT `Usuario` FROM `herreria`.`usuarios` ;") # Buscamos los nombres de usuarios registrados
        usuarios=cursor.fetchall()
        if nUsuario not in usuarios: # Nos fijamos si el nuevo nombre de usuario no existe en la tabla(ya que debe ser único)
            cursor.execute(sql,usuario) # Creamos el usuario
        else: # Si el nombre ya existe, solicitamos que use otro
            flash("Nombre de usuario no disponible")
        conn.commit() # Cerramos conexión 
        return redirect('/administracion') # Retornamos a administracion
    else: return redirect('/login') #Redireccionamos a la pagina de login

# Edicion datos usuario
@app.route("/modificar_usuario", methods=['POST']) # recibimos los datos del formulario correspondiente
def modificar_usuario():
    if "username" in session: # Si es un usuario registrado
        nUsuario=request.form["txtUsuario"] # Nuevo nombre de usuario
        pUsuario=request.form['txtPassword'] # Nuevo password de usuario
        usuario1=(nUsuario,pUsuario,usuario[0][0]) # Agrupamos los datos, junto al nombre viejo del usuario
        sql="UPDATE `herreria`.`usuarios` SET `Usuario`= %s, `password`= %s WHERE `Usuario`=%s;" # Armamos la sentencia para la actualización del usuario
        conn = mysql.connect() # Abrimos la conexión con DB
        cursor = conn.cursor()
        cursor.execute("SELECT `Usuario` FROM `herreria`.`usuarios` ;") # Buscamos todos los nombres de usuarios registrados
        usuarios=cursor.fetchall() # Almacenamos los datos en una tupla
        if nUsuario not in usuarios or nUsuario==usuario[0][0]: # Si el nuevo nombre de usuario no existe en la tabla, o si es igual al nombre viejo
            cursor.execute(sql,usuario1) # Hacemos la actualización del usuario
        else: # Si el nuevo nombre de usuario existe en la tabla, y no es igual al nombre viejo
            flash("Nombre de usuario no disponible") # Escribimos un mensaje al usuario
        conn.commit() # Cerramos la conexión
        return redirect('/administracion') # Retornamos a la pagina administracion

# Renderizacion de pagina de ingreso para el propietario
@app.route('/login')
def login():
   return render_template("/propietario/login.html")

# Procesado del login
@app.route('/ingresar', methods=['POST']) # Recibimos los datos del formulario correspondiente
def ingresar():
    _usuario=request.form["txtUsuario"]
    _password=request.form["txtPassword"]
    sql="SELECT * FROM `herreria`.`usuarios` WHERE `Usuario` LIKE %s" # Definimos la busqueda todos los datos del usuario según el nombre de usuario
    conn = mysql.connect() # Abrimos la conexión con DB
    cursor = conn.cursor()
    cursor.execute(sql,_usuario) # Ejecutamos la busqueda
    global usuario # Declaramos que la siguiente asignación de la variable usuario es a nivel global
    usuario=cursor.fetchall() # Asignamos el resultado de la busqueda en la DB
    conn.commit() # Cerramos conexión
    if usuario!=() and _password==usuario[0][1]: # Si se encontró el nombre de usuario en la DB y el password ingresado coincide con el correspondiente en la DB
        session["username"]=_usuario # Creamos la cookie para validar que es un usuario registrado
        session.set_cookie('username', '', expires=0)
        return redirect("administracion") # Redireccionamos a la pagina administracion
    else: # Si los datos ingresados no se corresponden con el de un usuario registrado
        flash("Usuario o contraseña erroneos") # Escribimos un mensaje al usuario
        return render_template("propietario/login.html") # y lo enviamos a la pagina de login

#procesamiento de logout
@app.route('/logout')
def logout():
   session.pop("username", None)
   return redirect("/")

# Almacenamiento de la foto del producto
@app.route('/fotos/<nombreFoto>') #Recibimos como parametro el nombre de la foto
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto) # Guardamos la foto en la carpeta destinada a tal fin, con su nombre correspondiente
#FIN DE PARTE PARA EL PROPIETARIO _____________________________________________________

if __name__=="__main__":
    app.run(debug=True, host="192.168.100.3", port=5001)


