import sqlite3
import hashlib

DB_NAME = "InventarioBD_2.db"

def hash_password(password):
    """Cifra la contraseña usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_and_add_column(cursor, table_name, column_name, column_type):
    """
    Revisa si una columna existe en una tabla. Si no, la añade.
    """
    try:
        # PRAGMA table_info devuelve la lista de columnas
        cursor.execute(f"PRAGMA table_info({table_name})")
        # Creamos una lista de los nombres de columnas existentes
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Si la columna no está en la lista, la añadimos
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            print(f"Columna '{column_name}' añadida con éxito a la tabla '{table_name}'.")
        else:
            print(f"Columna '{column_name}' ya existe en la tabla '{table_name}'.")
            
    except sqlite3.Error as e:
        print(f"Error al verificar/añadir columna {column_name} en {table_name}: {e}")

def setup():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. Crear tabla de usuarios (si no existe) ---
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NOMBRE TEXT UNIQUE NOT NULL,
            CONTRASEÑA TEXT NOT NULL,
            "ULTIMO INICIO DE SESION" TEXT
        )
        ''')
        print("Tabla 'usuarios' creada o ya existente.")
    except sqlite3.Error as e:
        print(f"Error al crear la tabla 'usuarios': {e}")
        conn.close()
        return

    # --- 2. Insertar los 3 usuarios (si no existen) ---
    usuarios_a_crear = [
        ("Admin", "admin123"),
        ("almacen", "almacen11"),
        ("productos", "producto19")
    ]
    try:
        for nombre, password in usuarios_a_crear:
            password_cifrada = hash_password(password)
            # 'INSERT OR IGNORE' evita errores si el usuario ya existe
            cursor.execute("INSERT OR IGNORE INTO usuarios (NOMBRE, CONTRASEÑA) VALUES (?, ?)", 
                           (nombre, password_cifrada))
        conn.commit()
        print("Usuarios base verificados/insertados.")
    except sqlite3.Error as e:
        print(f"Error al insertar usuarios: {e}")

    # --- 3. Añadir las NUEVAS columnas (de forma segura) ---
    print("\n--- Actualizando esquema de la Base de Datos ---")
    
    # Añadir 'rol' a 'usuarios'
    check_and_add_column(cursor, 'usuarios', 'rol', 'TEXT')
    
    # Añadir columnas de auditoría a 'productos'
    check_and_add_column(cursor, 'productos', 'fecha_ultima_modificacion', 'TEXT')
    check_and_add_column(cursor, 'productos', 'ultimo_usuario_en_modificar', 'TEXT')
    
    # Añadir columnas de auditoría a 'almacenes'
    check_and_add_column(cursor, 'almacenes', 'fecha_ultima_modificacion', 'TEXT')
    check_and_add_column(cursor, 'almacenes', 'ultimo_usuario_en_modificar', 'TEXT')
    
    print("-------------------------------------------------")

    # --- 4. Asignar los ROLES a los usuarios ---
    try:
        cursor.execute("UPDATE usuarios SET rol = 'ADMIN' WHERE NOMBRE = 'Admin'")
        cursor.execute("UPDATE usuarios SET rol = 'PRODUCTOS' WHERE NOMBRE = 'productos'")
        cursor.execute("UPDATE usuarios SET rol = 'ALMACENES' WHERE NOMBRE = 'almacen'")
        conn.commit()
        print("\nRoles asignados a los usuarios con éxito.")
    except sqlite3.Error as e:
        print(f"\nError al asignar roles: {e}")
    finally:
        conn.close()
        print("Configuración de la base de datos completada.")

if __name__ == "__main__":
    setup()