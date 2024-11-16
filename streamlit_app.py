Conversación abierta; 1 mensaje no leído

Ir al contenido
Cómo usar Gmail con lectores de pantalla
Habilita las notificaciones de escritorio para Gmail.
   Aceptar  No, gracias
1 de 9,578
(sin asunto)
Recibidos

Andres Felipe Beltran Ibanez <andresf.beltrani@ecci.edu.co>
Adjuntos
7:30 p.m. (hace 16 minutos)
para mí



AVISO: Los servicios del correo ecci.edu.co son soportados tecnológicamente por © Google para toda la comunidad de la Universidad ECCI (Administrtivos, Docentes y Estudiantes), las opiniones que contenga este mensaje son exclusivas de su autor y no representan necesariamente la opinión de la Universidad ECCI. La Universidad ECCi no garantiza la utilización de un antivirus ya que se menciona los servicios son soportados © Google, si su antivirus detecta alguna anomalía por favor reportelo y elimine, la Universidad no se responsabiliza por los daños causados por cualquier virus transmitido en este correo electrónico.

La información contenida en este mensaje y en los archivos adjuntos es confidencial y reservada y está dirigida exclusivamente a su destinatario, sin la intención de que sea conocida por terceros, por lo tanto, de conformidad con las normas legales vigentes, su interceptación, sustracción, extravío, reproducción, lectura o uso esta prohibido a cualquier persona diferente. Se les exige expresamente a la comunidad ECCI (Administrtivos, Docentes y Estudiantes) que no realicen declaraciones difamatorias, no infrinjan ni autoricen ninguna infracción de las leyes de propiedad intelectual o cualquier otro derecho legal mediante comunicaciones por correo electrónico.La Universidad ECCI no garantizar guardar una copia de respaldo de los archivos, correos.

Si por error ha recibido este mensaje por favor discúlpenos, notifiquenoslo y elimínelo.

AVISO: Los servicios del correo ecci.edu.co son soportados tecnológicamente por © Google para toda la comunidad de la Universidad ECCI (Administrtivos, Docentes y Estudiantes), las opiniones que contenga este mensaje son exclusivas de su autor y no representan necesariamente la opinión de la Universidad ECCI. La Universidad ECCi no garantiza la utilización de un antivirus ya que se menciona los servicios son soportados © Google, si su antivirus detecta alguna anomalía por favor reportelo y elimine, la Universidad no se responsabiliza por los daños causados por cualquier virus transmitido en este correo electrónico.

La información contenida en este mensaje y en los archivos adjuntos es confidencial y reservada y está dirigida exclusivamente a su destinatario, sin la intención de que sea conocida por terceros, por lo tanto, de conformidad con las normas legales vigentes, su interceptación, sustracción, extravío, reproducción, lectura o uso esta prohibido a cualquier persona diferente. Se les exige expresamente a la comunidad ECCI (Administrtivos, Docentes y Estudiantes) que no realicen declaraciones difamatorias, no infrinjan ni autoricen ninguna infracción de las leyes de propiedad intelectual o cualquier otro derecho legal mediante comunicaciones por correo electrónico.La Universidad ECCI no garantizar guardar una copia de respaldo de los archivos, correos.

Si por error ha recibido este mensaje por favor discúlpenos, notifiquenoslo y elimínelo.
 Un archivo adjunto
  •  Analizado por Gmail







​
Auto
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from database import init_db, register_user

# Inicializar la base de datos
init_db()

st.set_page_config(page_title="AforoSmart Restaurant", layout="wide")

# Inicializar el estado de la sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "refresh" not in st.session_state:
    st.session_state.refresh = False

# Función para autenticar usuarios
def authenticate(username, password):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Liberar mesas automáticamente si han pasado más de 2 horas desde la última reserva
def release_old_reservations():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    current_time = datetime.now()
    cursor.execute("""
        DELETE FROM reservations
        WHERE status = 'Reservado' 
        AND datetime(date || ' ' || time) < datetime(?, '-2 hours')
    """, (current_time.strftime('%Y-%m-%d %H:%M:%S'),))
    cursor.execute("""
        UPDATE tables
        SET available = 1
        WHERE id NOT IN (
            SELECT table_id FROM reservations WHERE status = 'Reservado'
        )
    """)
    conn.commit()
    conn.close()

# Función para el panel del administrador
def admin_dashboard():
    st.header("Panel del Administrador")
    st.subheader("Gestión de Mesas")

    # Conectar a la base de datos
    conn = sqlite3.connect('restaurant.db')

    # Mostrar todas las mesas
    df = pd.read_sql_query("SELECT * FROM tables", conn)
    st.dataframe(df)

    # Agregar una nueva mesa
    st.subheader("Agregar Mesa")
    table_number = st.number_input("Número de mesa", min_value=1, key="table_number")
    seats = st.number_input("Cantidad de asientos", min_value=1, key="seats")
    
    if st.button("Agregar mesa"):
        if table_number > 0 and seats > 0:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tables (table_number, seats, available) VALUES (?, ?, ?)", (table_number, seats, True))
            conn.commit()
            st.success(f"Mesa {table_number} agregada exitosamente con {seats} asientos.")
        else:
            st.error("Por favor, ingresa el número de mesa y la cantidad de asientos.")
    
    # Eliminar una mesa
    st.subheader("Eliminar Mesa")
    delete_table_id = st.number_input("ID de la mesa a eliminar", min_value=1)
    if st.button("Eliminar mesa"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tables WHERE id = ?", (delete_table_id,))
        conn.commit()
        st.success(f"Mesa con ID {delete_table_id} eliminada.")

    # Ver todas las reservas activas
    st.subheader("Reservas Activas")
    df_reservations = pd.read_sql_query("""
        SELECT r.id AS reservation_id, r.date, r.time, t.table_number, u.username AS customer
        FROM reservations r
        JOIN tables t ON r.table_id = t.id
        JOIN users u ON r.user_id = u.id
        WHERE r.status = 'Reservado'
    """, conn)
    st.dataframe(df_reservations)
    conn.close()

# Función para el panel del cliente
def client_dashboard():
    st.header("Panel del Cliente")
    st.subheader("Realizar Reserva")

    # Liberar mesas automáticamente si han pasado más de 2 horas desde la última reserva
    release_old_reservations()

    # Conectar a la base de datos
    conn = sqlite3.connect('restaurant.db')
    df = pd.read_sql_query("SELECT id, table_number, seats FROM tables WHERE available = 1", conn)
    
    if df.empty:
        st.info("No hay mesas disponibles actualmente.")
        conn.close()
        return

    st.dataframe(df)

    # Seleccionar mesa disponible
    table_id = st.selectbox("Selecciona el ID de la mesa", df['id'])

    # Limitar la selección de la fecha a los próximos 7 días
    min_date = datetime.now()
    max_date = min_date + timedelta(days=7)
    date = st.date_input("Fecha de la reserva", min_value=min_date, max_value=max_date)

    # Generar intervalos de dos horas
    time_slots = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]

    # Verificar los horarios disponibles para la mesa seleccionada
    cursor = conn.cursor()
    available_slots = []
    for slot in time_slots:
        cursor.execute("""
            SELECT * FROM reservations 
            WHERE table_id = ? AND date = ? AND time = ? AND status = 'Reservado'
        """, (table_id, date.strftime('%Y-%m-%d'), f"{slot}:00"))
        if not cursor.fetchone():
            available_slots.append(slot)
    
    if available_slots:
        selected_time = st.selectbox("Selecciona el horario", available_slots)
    else:
        st.warning("No hay horarios disponibles para esta mesa en la fecha seleccionada.")
        conn.close()
        return

    user_id = 1  # Aquí se debería utilizar el ID del cliente autenticado

    if st.button("Reservar"):
        reservation_time = f"{selected_time}:00"

        try:
            cursor.execute("""
                INSERT INTO reservations (user_id, table_id, date, time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, table_id, date.strftime('%Y-%m-%d'), reservation_time, 'Reservado'))
            conn.commit()
            st.success("Reserva realizada con éxito")
        except Exception as e:
            st.error(f"Error al realizar la reserva: {e}")
        finally:
            conn.close()

# Función principal
def main():
    st.title("AforoSmart Restaurant")

    if not st.session_state.authenticated:
        action = st.radio("Seleccione una opción", ("Iniciar sesión", "Registrar"))

        if action == "Iniciar sesión":
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type='password')
            if st.button("Iniciar sesión"):
                user = authenticate(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.role = user[1]
                    st.experimental_rerun()
        elif action == "Registrar":
            st.subheader("Formulario de Registro")
            username = st.text_input("Nuevo usuario")
            password = st.text_input("Nueva contraseña", type='password')
            role = st.selectbox("Selecciona el rol", ("administrador", "cliente"))
            if st.button("Registrar"):
                register_user(username, password, role)
                st.success("Usuario registrado con éxito. Ahora puedes iniciar sesión.")
    else:
        if st.session_state.role == "administrador":
            admin_dashboard()
        elif st.session_state.role == "cliente":
            client_dashboard()

if __name__ == "__main__":
    main()
aforo de restauranbte daniel alejadnro.txt
Mostrando aforo de restauranbte daniel alejadnro.txt
