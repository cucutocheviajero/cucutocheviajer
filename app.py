# -*- coding: utf-8 -*-  #permite usar caracteres especiales, tildes, etc

#BLOQUE 1 CONFIGURACION DE LAS LIBRERIAS - librerias importantes framwork flask
from flask import Flask, render_template, request, flash, redirect, url_for

import psycopg2  #modulo para conectarse a la base de datos

#lineas para enviar correos electronicos
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#
import os
import sqlite3

app = Flask(__name__)
app.secret_key = '12345678'  # Cambia esto por una clave única
#HASTA ACA TERMINA EL BLOQUE 1


#BLOQUE 2 FUNCIONES AUXILIARES
# Configuración de la base de datos
DATABASE_URL = "postgresql://cucutoche:123456@localhost:5433/cucutoche"

#CONECCION A LA BASE DE DATOS
def connect_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

#FUNCION AUXILIAR REENVIO DE CORREOS ELECTRONICOS
def send_email(name, email, message):
    # Configuración del servidor de correo electrónico
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'cucutenioviajero@gmail.com'
    smtp_password = 'hsux ywio toyt zfrp'

    # Crea el objeto MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = smtp_username
    msg['Subject'] = 'Nuevo mensaje desde cucutocheviajero.com'

    # Crea el cuerpo del correo electrónico
    body = f"Nombre: {name}\nCorreo electrónico: {email}\nMensaje:\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    # Envía el correo electrónico
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
    return True
#HASTA ACA TERMINA EL BLOQUE 2

#BLOQUE 3 FUNCIONES DE INICIALIZACIÓN - CREACION DE TABLAS
#TABLA CONTACTANOS
def create_table_messages_contacts():
    """Crea la tabla de mensajes si no existe"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages_contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        message TEXT,
        state VARCHAR(100)
    )
    """)
    conn.commit()  #GUARDA LOS CAMBIOS EN LA BASE DE DATOS
    cur.close()
    conn.close()  #CIERRA LA CONEXION CORRECTAMENTE

#TABLA MUNICIPIOS
def create_table_municipalities():
    """Create municipalities table and insert data from folders."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS municipalities (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE,
        subtitle TEXT,
        information TEXT,
        video TEXT,
        image TEXT,
        background TEXT
    )
    """)
    conn.commit()
 
#PERMITE CARGAR AUTOMATICAMENTELA INFORMACION DE LOS MUNICIPIOS, DESDE CARPETAS LOCALES
    for municipalitie in os.listdir('static/municipalitie'):  #RECONOCE LA CARPETA
        municipalitie_path = os.path.join('static/municipalitie', municipalitie) #CONSTRUYE LA RUTA A LA CARPETA
        
        if os.path.isdir(municipalitie_path):
            # Rutas de BUCAR LOS archivos
            information_path = os.path.join(municipalitie_path, 'information.txt')
            subtitle_path = os.path.join(municipalitie_path, 'subtitle.txt')
            video_path = os.path.join(municipalitie_path, 'video.mp4')
            image_path = os.path.join(municipalitie_path, 'image.jpg')
            background_path = os.path.join(municipalitie_path, 'background.jpg')

            # Diccionario con los datos que vamos a insertar
            data = {'name': municipalitie}
	    
            #AGREGA LOS ARCHIVOS SI LA CARPETA EXISTE
            if os.path.exists(subtitle_path):
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    data['subtitle'] = f.read()

            if os.path.exists(information_path):
                with open(information_path, 'r', encoding='utf-8') as f:
                    data['information'] = f.read()

            if os.path.exists(video_path):
                data['video'] = f'/static/municipalitie/{municipalitie}/video.mp4'

            if os.path.exists(image_path):
                data['image'] = f'/static/municipalitie/{municipalitie}/image.jpg'

            if os.path.exists(background_path):
                data['background'] = f'/static/municipalitie/{municipalitie}/background.jpg'

            # Construcción dinámica de la consulta
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = list(data.values())
            try:
                cur.execute(
                    f"INSERT INTO municipalities ({columns}) VALUES ({placeholders}) ON CONFLICT (name) DO NOTHING",
                    values
                )
            except Exception as e:
                print(f"Error inserting {municipalitie}: {e}")

    conn.commit()
    cur.close()
    conn.close()

#TABLA LUGARES TURISTICOS
def create_table_places():
    """Creates the places table and inserts data from folders."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id SERIAL PRIMARY KEY,
        municipality_id INTEGER REFERENCES municipalities(id) ON DELETE CASCADE, 
        name TEXT,
        information TEXT,
        video TEXT,
        image TEXT,
        background TEXT,
        UNIQUE(municipality_id, name) -- Avoids conflicts with duplicate names within the same municipality
    )
    """)
    conn.commit()

#LECUTRA DE LOS LUGARES TURISTICOS DE CADA MUNICIPIO
    # Insert data from directories
    for municipality in os.listdir('static/municipalitie'):
        municipality_path = os.path.join('static/municipalitie', municipality, 'places') #BUSCA SUBCARPETA PLACES DE LUGARES
        if os.path.isdir(municipality_path):
            # Get the municipality ID
            cur.execute("SELECT id FROM municipalities WHERE name = %s", (municipality,)) #BUSCA EL ID DEL MUNICIPIO COMO LLAVE FORANEA
            municipality_data = cur.fetchone()
            if municipality_data:
                municipality_id = municipality_data[0]  # Municipality ID
                for place in os.listdir(municipality_path):
                    place_path = os.path.join(municipality_path, place)
                    if os.path.isdir(place_path):
                        name_place = place.replace("_", " ")  # Replace underscores with spaces
                        # File paths
                        information_path = os.path.join(place_path, 'information.txt')
                        video_path = os.path.join(place_path, 'video.mp4')
                        image_path = os.path.join(place_path, 'image.jpg')
                        background_path = os.path.join(place_path, 'background.jpg')
                        # Validate existence of files before assigning
                        information = None
                        if os.path.exists(information_path):
                            with open(information_path, 'r', encoding='utf-8') as f:
                                information = f.read()
                        video = video_path if os.path.exists(video_path) else None
                        image = image_path if os.path.exists(image_path) else None
                        background_path if os.path.exists(background_path) else None
                        try:
                            cur.execute(
                                "INSERT INTO places (municipality_id, name, information, video, image, background) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (municipality_id, name) DO NOTHING",
                                (municipality_id, name_place, information, video, image, background_path)
                            )
                        except Exception as e:
                            print(f"Error inserting {name_place} in {municipality}: {e}")
            else:
                print(f"Municipality {municipality} not found in the municipalities table.")

    conn.commit()
    cur.close()
    conn.close()
#HASTA ACA TERMINA EL BLOQUE 3 DE FUNCIONES DE INICIALIZACION


#BLOQUE 4 VISTAS
#RUTA 1 - MOSTRAS LOS LUGARES TURISTICOS DE UN MUNICIPIO
@app.route('/departments/<department>/<municipality>')
def show_places(department, municipality):
    base_path = os.path.join(app.static_folder, 'departments', department, municipality)
    places = []
    if os.path.isdir(base_path):
        for place in os.listdir(base_path):
            place_dir = os.path.join(base_path, place)
            if os.path.isdir(place_dir):
                images = []
                for file in os.listdir(place_dir):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        image_url = url_for('static', filename=f'departments/{department}/{municipality}/{place}/{file}')
                        images.append(image_url)
                if images:
                    places.append({'name': place, 'images': images})
    return render_template('placestwo.html', department=department, municipality=municipality, places=places)

#RUTA 2 - MOSTRAR MUNICIPIOS DE UN DEPARTAMENTO
@app.route('/departments/<department_name>')
def show_department(department_name):
    department_path = os.path.join(app.static_folder, 'departments', department_name) #ingresa a la carpeta departamentos y busca los municipios
    municipalities = []
    if os.path.exists(department_path):
        for municipio in os.listdir(department_path):
            municipio_path = os.path.join(department_path, municipio)
            background = os.path.join(municipio_path, 'background.jpg')
            if os.path.isdir(municipio_path) and os.path.exists(background):
                municipalities.append({
                    'name': municipio,
                    'background_url': url_for('static', filename=f'departments/{department_name}/{municipio}/background.jpg'),
                    'link': f'/departments/{department_name}/{municipio}'
                })
    return render_template('departments.html', department_name=department_name, municipalities=municipalities)

#RUTA 3 PRINCIPAL DEL SISTEMA  PAGINA INICIO
#CONEXIONA LA BASEDE DATOS PARA MOSTRAR MUNICIPIOS
@app.route('/')
def home():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, background FROM municipalities") #CONSULTA TODOS LOS MUNICIPIOS REGISTRADOS
    municipalities = [{'id': row[0], 'name': row[1], 'background_url': row[2]} for row in cur.fetchall()]
    conn.close()

    departments_path = os.path.join(app.static_folder, 'departments') #SE LEE LOS ARCHIVOS DE LOS DEPARTAMENTOS
    departments = []

    for dept in os.listdir(departments_path):
        dept_dir = os.path.join(departments_path, dept)
        background_path = os.path.join(dept_dir, 'background.jpg')

        if os.path.isdir(dept_dir) and os.path.exists(background_path):
            departments.append({
                'name': dept,
                'background_url': url_for('static', filename=f'departments/{dept}/background.jpg'),
                'link': f'/departments/{dept}'
            })
    
#SE DEFINE LA RUTA DESDE LAS CARPETAS LOCALES
#PAGINA HOME O INICIO
    home_path = os.path.join(app.static_folder, 'home')
    home_sections = []

    for folder in sorted(os.listdir(home_path)):
        folder_path = os.path.join(home_path, folder)
        if not os.path.isdir(folder_path):
            continue

        # Leer information.txt
        info_txt = ""
        info_path = os.path.join(folder_path, 'information.txt')
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                info_txt = f.read()

        # Leer imágenes del carrusel principal
        carousel_path = os.path.join(folder_path, 'carousel')
        carousel_images = []
        if os.path.exists(carousel_path):
            for img in sorted(os.listdir(carousel_path)):
                if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    carousel_images.append(url_for('static', filename=f'home/{folder}/carousel/{img}'))

        # Leer lugares (places)
        places_path = os.path.join(folder_path, 'places')
        places = []
        if os.path.exists(places_path):
            for place in sorted(os.listdir(places_path)):
                place_path = os.path.join(places_path, place)
                if not os.path.isdir(place_path):
                    continue

                # Leer info del lugar
                place_info_txt = ""
                place_info_path = os.path.join(place_path, 'information.txt')
                if os.path.exists(place_info_path):
                    with open(place_info_path, 'r', encoding='utf-8') as f:
                        place_info_txt = f.read()

                # Leer imágenes del carrusel del lugar
                place_carousel_path = os.path.join(place_path, 'carousel')
                place_images = []
                if os.path.exists(place_carousel_path):
                    for img in sorted(os.listdir(place_carousel_path)):
                        if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            place_images.append(url_for('static', filename=f'home/{folder}/places/{place}/carousel/{img}'))

                places.append({
                    'name': place,
                    'info': place_info_txt,
                    'carousel': place_images
                })

        # Añadir sección completa
        home_sections.append({
            'title': folder,
            'info': info_txt,
            'carousel': carousel_images,
            'places': places
        })

    return render_template('home.html', municipalities=municipalities, departments=departments, home_sections=home_sections)

#RUTA 4 SECCION DE EL VIAJERO 
def get_images_from_folder(folder_name):
    folder_path = os.path.join('static', 'img', folder_name)
    if not os.path.exists(folder_path):
        return []
    return [
        f'/static/img/{folder_name}/{img}' 
        for img in sorted(os.listdir(folder_path))
        if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    ]

@app.route('/about')
def about():
    mision_imgs = get_images_from_folder('mision')
    vision_imgs = get_images_from_folder('vision')
    valores_imgs = get_images_from_folder('valores')
    biografia_imgs = get_images_from_folder('biografia')
    cabezera_imgs = get_images_from_folder('cabezera')
    return render_template(
        'about.html',
        mision_imgs=mision_imgs,
        vision_imgs=vision_imgs,
        valores_imgs=valores_imgs,
        biografia_imgs=biografia_imgs,
        cabezera_imgs=cabezera_imgs
    )
#TERMINA EL VIAJERO ACA

#RUTA 5 MUNICIPIO 
@app.route('/municipality/<int:municipality_id>')
def municipality_page(municipality_id):
    conn = connect_db()
    cur = conn.cursor()

    # Consulta SQL para obtener los datos del municipio específico
    query = """
    SELECT 
        m.name, m.subtitle, m.information, m.video, m.image,
        p.id, p.name, p.information, p.video, p.image
    FROM 
        municipalities m
    LEFT JOIN 
        places p ON m.id = p.municipality_id
    WHERE 
        m.id = %s
    ORDER BY 
        p.name
    """
    cur.execute(query, (municipality_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Organizar datos del municipio y sus lugares
    municipality_data = None
    places = []
    for row in rows:
        if not municipality_data:
            municipality_data = {
                "id": municipality_id,
                "name": row[0],
                "subtitle": row[1],
                "information": row[2],
                "video": row[3],
                "image": row[4],
                "places": []
            }

        if row[5]:  # Si hay lugares de interés
            places.append({
                "id": row[5],
                "name": row[6],
                "information": row[7],
                "video": row[8],
                "image": row[9]
            })

    if municipality_data:
        municipality_data["places"] = places
    return render_template("municipalities.html", municipalities=municipality_data)

#RUTA VISTA 6 DE LUGARES TURISTICOS
@app.route('/places/<int:place_id>')
def place_detail(place_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.name as municipality_name, p.name, p.information, p.video, p.image, p.background
        FROM places p
        JOIN municipalities m ON p.municipality_id = m.id
        WHERE p.id = %s
    """, (place_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        municipality = row[0]
        # place_name = row[1].replace(" ", "_")  # Para formar el path del folder
        carrusel_path = f'static/municipalitie/{municipality}/places/{row[1]}/carousel'
        # Buscar imágenes en la carpeta
        carrusel_images = []
        if os.path.exists(carrusel_path):
            for file in sorted(os.listdir(carrusel_path)):
                if file.lower().endswith(('.jpg')):
                    carrusel_images.append(f'/{carrusel_path}/{file}')
        place = {
            "id": place_id,
            "municipality": municipality,
            "name": row[1],
            "information": row[2],
            "video": row[3],
            "image": row[4],
            "background": row[5],
            "carrusel_images": carrusel_images
        }
        return render_template('places.html', places=[place])
    else:
        return "Lugar no encontrado", 404


#RUTA VISTA 6 CONTACTENOS
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        conn = connect_db()
        cur = conn.cursor()
        try:
            send_email(name, email, message)
            cur.execute("INSERT INTO messages_contacts (name, email, message, state) VALUES (%s, %s, %s, %s)", (name, email, message, 'Envio exitoso'))
            conn.commit()
            flash('¡Tu mensaje se envió correctamente!', 'success')
        except Exception as e:
            cur.execute("INSERT INTO messages_contacts (name, email, message, state) VALUES (%s, %s, %s, %s)", (name, email, message, 'Envio fallido'))
            conn.commit()
            flash('Hubo un problema al enviar tu mensaje. Por favor, intenta nuevamente.', 'error')
        cur.close()
        cur.close()
        conn.close()
        return redirect(url_for('contact'))
    return render_template('contact.html')

#RUTA VISTA 7 DEPARTAMENTOS
@app.route('/departments')
def departments():
    return render_template('departments.html')
#ACA TERMINA LA SECCION VISTA

#bloque INICIO DEL SERVIDOR
if __name__ == '__main__':
    create_table_messages_contacts()  # Crear la tabla al iniciar la aplicación
    create_table_municipalities()  # Crear la tabla al iniciar la aplicación
    create_table_places()  # Crear la tabla al iniciar la aplicación
    app.run(host="0.0.0.0", port=5000, debug=True)

