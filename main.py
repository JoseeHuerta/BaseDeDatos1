import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style 
from PIL import Image, ImageTk
import os
import sqlite3
import hashlib
import datetime
import sys 

# --- FUNCIÓN DE AYUDA PARA PYINSTALLER ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Constante de Base de Datos ---
DB_NAME = resource_path("InventarioBD_2.db")

def hash_password(password):
    """Cifra la contraseña usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# --- Página de Inicio de Sesión ---

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        form_frame = ttk.Frame(self)
        form_frame.pack(expand=True, padx=40, pady=20)
        
        # Logo
        try:
            image_path = resource_path(os.path.join("assets", "logo_unison.png"))
            img = Image.open(image_path)
            img_resized = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img_resized)

            label_logo = ttk.Label(form_frame, image=self.logo_image, background="white")
            label_logo.pack(pady=(10, 20))
        except Exception as e:
            print(f"Error al cargar imagen en Login: {e}")

        # Título
        ttk.Label(form_frame, text="Inicio de Sesión", font=("Arial", 24, "bold"), bootstyle="primary").pack(pady=10)
        
        # Usuario
        user_frame = ttk.Frame(form_frame)
        user_frame.pack(pady=10, padx=20)
        ttk.Label(user_frame, text="Usuario: ", font=("Arial", 14)).pack(side="left", padx=5)
        self.entry_usuario = ttk.Entry(user_frame, font=("Arial", 14), width=20)
        self.entry_usuario.pack(side="left")

        # Contraseña
        pass_frame = ttk.Frame(form_frame)
        pass_frame.pack(pady=10, padx=20)
        ttk.Label(pass_frame, text="Contraseña: ", font=("Arial", 14)).pack(side="left", padx=5)
        self.entry_pass = ttk.Entry(pass_frame, font=("Arial", 14), width=20, show="*")
        self.entry_pass.pack(side="left")
        
        # Botón
        btn_login = ttk.Button(form_frame, text="Ingresar", 
                               command=self.intentar_login, bootstyle="primary",
                               width=20)
        btn_login.pack(pady=20)

        self.label_error = ttk.Label(form_frame, text="", bootstyle="danger", font=("Arial", 12))
        self.label_error.pack(pady=5)
        
        self.controller.bind('<Return>', self.intentar_login)

    def intentar_login(self, event=None):
        usuario = self.entry_usuario.get()
        password = self.entry_pass.get()

        if not usuario or not password:
            self.label_error.config(text="Por favor, ingrese usuario y contraseña")
            return

        password_cifrada = hash_password(password)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute("SELECT CONTRASEÑA, rol, NOMBRE FROM usuarios WHERE NOMBRE = ?", (usuario,))
            resultado = cursor.fetchone() 

            if resultado and resultado[0] == password_cifrada:
                self.label_error.config(text="")
                user_role = resultado[1]
                user_name_db = resultado[2]
                now = datetime.datetime.now().isoformat()
                cursor.execute('UPDATE usuarios SET "ULTIMO INICIO DE SESION" = ? WHERE NOMBRE = ?', (now, usuario))
                conn.commit()
                self.controller.login_exitoso(user_name_db, user_role)
            else:
                self.label_error.config(text="Usuario o contraseña incorrectos")
        except sqlite3.Error as e:
            self.label_error.config(text=f"Error de base de datos: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
        self.controller.unbind('<Return>')


# --- Página 1: Página Principal (HomePage) ---

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 

        nav_frame = ttk.Frame(self)
        nav_frame.pack(side="top", fill="x", pady=20, padx=20)

        btn_productos = ttk.Button(nav_frame, text="Lista de Productos",
                                   command=lambda: controller.show_frame("FormularioProductos"),
                                   bootstyle="secondary")
        btn_productos.pack(side="left", padx=10)

        btn_almacenes = ttk.Button(nav_frame, text="Lista de Almacenes",
                                   command=lambda: controller.show_frame("FormularioAlmacenes"),
                                   bootstyle="secondary")
        btn_almacenes.pack(side="left", padx=10)

        center_frame = ttk.Frame(self)
        center_frame.pack(fill="both", expand=True)

        try:
            image_path = resource_path(os.path.join("assets", "logo_unison.png"))
            img = Image.open(image_path)
            img_resized = img.resize((250, 250), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img_resized)
            label_logo = ttk.Label(center_frame, image=self.logo_image, background="white")
            label_logo.pack(pady=20)
        except Exception as e:
            print(f"Error al cargar imagen en Home: {e}")
            label_logo = ttk.Label(center_frame, 
                                  text="Error: Logo no encontrado.", 
                                  font=("Arial", 14), bootstyle="danger")
            label_logo.pack(pady=20)

        user_name = self.controller.current_user_name
        user_role = self.controller.current_user_role
        
        label_saludo = ttk.Label(center_frame, text=f"Bienvenido, {user_name} (Rol: {user_role})", 
                                 font=("Arial", 16), bootstyle="secondary")
        label_saludo.pack(pady=10)


# --- Página 2: Formulario de (Lista de) Productos ---

class FormularioProductos(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Frame de Navegación
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=(20, 10), padx=20, fill="x")

        btn_home = ttk.Button(top_frame, text="< Regresar a Inicio",
                             command=lambda: controller.show_frame("HomePage"),
                             bootstyle="link")
        btn_home.pack(side="left")

        self.btn_agregar = ttk.Button(top_frame, text="➕ Agregar Producto Nuevo",
                                      command=self.abrir_formulario_nuevo,
                                      bootstyle="success")
        self.btn_agregar.pack(side="right")

        # Frame de Filtros (Botones)
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=(0, 10), padx=20, fill="x", anchor="e")

        self.btn_filtros = ttk.Button(filter_frame, text="⚙️ Filtros Avanzados",
                                      command=self.abrir_ventana_filtros,
                                      bootstyle="info")
        self.btn_filtros.pack(side="right")
        
        self.btn_limpiar = ttk.Button(filter_frame, text="🔄 Ver Todo",
                                      command=self.cargar_productos,
                                      bootstyle="secondary-outline")
        self.btn_limpiar.pack(side="right", padx=5)

        # Título
        label = ttk.Label(self, text="Gestión de Productos", font=("Arial", 18, "bold"), bootstyle="primary")
        label.pack(pady=5)
        
        # Tabla
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, selectmode="extended", bootstyle="secondary")
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Columnas
        self.tree["columns"] = ("id", "nombre", "precio", "cantidad", "departamento", "almacen", "fecha_mod", "usuario_mod")
        self.tree.column("#0", width=0, stretch=tk.NO) 
        self.tree.column("id", anchor=tk.W, width=40)
        self.tree.column("nombre", anchor=tk.W, width=150)
        self.tree.column("precio", anchor=tk.E, width=80) 
        self.tree.column("cantidad", anchor=tk.E, width=80)
        self.tree.column("departamento", anchor=tk.W, width=120)
        self.tree.column("almacen", anchor=tk.W, width=120)
        self.tree.column("fecha_mod", anchor=tk.W, width=150)
        self.tree.column("usuario_mod", anchor=tk.W, width=100)

        # Encabezados
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("id", text="ID", anchor=tk.W)
        self.tree.heading("nombre", text="Nombre", anchor=tk.W)
        self.tree.heading("precio", text="Precio", anchor=tk.E)
        self.tree.heading("cantidad", text="Cantidad", anchor=tk.W)
        self.tree.heading("departamento", text="Departamento", anchor=tk.W)
        self.tree.heading("almacen", text="Almacén", anchor=tk.W)
        self.tree.heading("fecha_mod", text="Última Modificación", anchor=tk.W)
        self.tree.heading("usuario_mod", text="Modificado por", anchor=tk.W)

        # Etiqueta de feedback creada ANTES de cargar
        self.label_feedback = ttk.Label(self, text="", font=("Arial", 12))
        self.label_feedback.pack(pady=5)

        self.cargar_productos()
        
        self.tree.bind("<Double-1>", self.abrir_formulario_editar)
        self.aplicar_permisos()

    def cargar_productos(self):
        """Carga todos los productos (sin filtros)"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            sql_query = """
                SELECT 
                    p.id, p.nombre, p.precio, p.cantidad, p.departamento, 
                    a.nombre as nombre_almacen,
                    p.fecha_ultima_modificacion, p.ultimo_usuario_en_modificar
                FROM productos p
                LEFT JOIN almacenes a ON p.almacen = a.id
            """
            cursor.execute(sql_query)
            for row in cursor.fetchall():
                self.tree.insert(parent="", index="end", values=row)
            
            if hasattr(self, 'label_feedback'):
                self.label_feedback.config(text="")
                
        except sqlite3.Error as e:
            if hasattr(self, 'label_feedback'):
                self.label_feedback.config(text=f"Error en BD: {e}", bootstyle="danger")
            else:
                print(f"Error en BD: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def abrir_ventana_filtros(self):
        ventana = ttk.Toplevel(self)
        ventana.title("Filtros Avanzados de Productos")
        ventana.geometry("400x600") # Hice la ventana un poco más alta
        
        ttk.Label(ventana, text="Filtrar Productos", font=("Arial", 14, "bold"), bootstyle="primary").pack(pady=10)
        
        form_frame = ttk.Frame(ventana)
        form_frame.pack(padx=20, pady=10, fill="x")

        # Filtros
        ttk.Label(form_frame, text="Nombre contiene:").pack(anchor="w")
        entry_nombre = ttk.Entry(form_frame)
        entry_nombre.pack(fill="x", pady=(0, 5))

        ttk.Label(form_frame, text="Departamento:").pack(anchor="w")
        entry_depto = ttk.Entry(form_frame)
        entry_depto.pack(fill="x", pady=(0, 5))

        ttk.Label(form_frame, text="Nombre de Almacén:").pack(anchor="w")
        entry_almacen = ttk.Entry(form_frame)
        entry_almacen.pack(fill="x", pady=(0, 5))

        # --- NUEVOS FILTROS ---
        ttk.Label(form_frame, text="Modificado por (Usuario):").pack(anchor="w")
        entry_usuario = ttk.Entry(form_frame)
        entry_usuario.pack(fill="x", pady=(0, 5))

        ttk.Label(form_frame, text="Fecha Modificación (contiene ej. 2025-11):").pack(anchor="w")
        entry_fecha = ttk.Entry(form_frame)
        entry_fecha.pack(fill="x", pady=(0, 5))
        # ----------------------

        ttk.Label(form_frame, text="Rango de Precio:").pack(anchor="w")
        price_frame = ttk.Frame(form_frame)
        price_frame.pack(fill="x", pady=(0, 10))
        
        entry_precio_min = ttk.Entry(price_frame, width=10)
        entry_precio_min.pack(side="left")
        ttk.Label(price_frame, text=" - ").pack(side="left")
        entry_precio_max = ttk.Entry(price_frame, width=10)
        entry_precio_max.pack(side="left")
        ttk.Label(price_frame, text="(Mín - Máx)").pack(side="left", padx=5)

        btn_buscar = ttk.Button(ventana, text="🔍 BUSCAR", 
                                bootstyle="success", 
                                command=lambda: self.ejecutar_busqueda_avanzada(
                                    ventana, 
                                    entry_nombre.get(), 
                                    entry_depto.get(), 
                                    entry_almacen.get(), 
                                    entry_precio_min.get(), 
                                    entry_precio_max.get(),
                                    entry_usuario.get(), # Nuevo
                                    entry_fecha.get()    # Nuevo
                                ))
        btn_buscar.pack(pady=20, fill="x", padx=20)

    def ejecutar_busqueda_avanzada(self, ventana, nombre, depto, almacen, p_min, p_max, usuario_mod, fecha_mod):
        ventana.destroy()
        
        sql = """
            SELECT 
                p.id, p.nombre, p.precio, p.cantidad, p.departamento, 
                a.nombre as nombre_almacen,
                p.fecha_ultima_modificacion, p.ultimo_usuario_en_modificar
            FROM productos p
            LEFT JOIN almacenes a ON p.almacen = a.id
            WHERE 1=1 
        """
        params = []

        if nombre:
            sql += " AND p.nombre LIKE ?"
            params.append(f"%{nombre}%")
        
        if depto:
            sql += " AND p.departamento LIKE ?"
            params.append(f"%{depto}%")
            
        if almacen:
            sql += " AND a.nombre LIKE ?"
            params.append(f"%{almacen}%")
        
        if p_min:
            sql += " AND p.precio >= ?"
            params.append(float(p_min))
            
        if p_max:
            sql += " AND p.precio <= ?"
            params.append(float(p_max))
            
        # --- NUEVOS FILTROS SQL ---
        if usuario_mod:
            sql += " AND p.ultimo_usuario_en_modificar LIKE ?"
            params.append(f"%{usuario_mod}%")
            
        if fecha_mod:
            sql += " AND p.fecha_ultima_modificacion LIKE ?"
            params.append(f"%{fecha_mod}%")
        # --------------------------

        for i in self.tree.get_children():
            self.tree.delete(i)
            
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            filas = cursor.fetchall()
            if not filas:
                self.label_feedback.config(text="No se encontraron resultados con esos filtros.", bootstyle="warning")
            else:
                self.label_feedback.config(text=f"Se encontraron {len(filas)} resultados.", bootstyle="success")
                for row in filas:
                    self.tree.insert(parent="", index="end", values=row)
                
        except ValueError:
             self.label_feedback.config(text="Error: El precio debe ser numérico", bootstyle="danger")
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error en búsqueda: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def aplicar_permisos(self):
        rol = self.controller.current_user_role
        if rol not in ['ADMIN', 'PRODUCTOS']:
            self.btn_agregar.config(state="disabled")
            self.tree.unbind("<Double-1>")
            self.label_feedback.config(text="Modo de solo lectura. Rol no autorizado para editar.", bootstyle="info")

    def abrir_formulario_nuevo(self):
        self.controller.navegar_a_edicion("FormularioEdicionProducto", None)

    def abrir_formulario_editar(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        valores = self.tree.item(selected_item, 'values')
        item_id = valores[0]
        self.controller.navegar_a_edicion("FormularioEdicionProducto", item_id)


# --- Página 3: Formulario de (Lista de) Almacenes ---

class FormularioAlmacenes(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Frame Superior
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=(20, 10), padx=20, fill="x") 

        btn_home = ttk.Button(top_frame, text="< Regresar a Inicio",
                             command=lambda: controller.show_frame("HomePage"),
                             bootstyle="link")
        btn_home.pack(side="left")

        self.btn_agregar = ttk.Button(top_frame, text="➕ Agregar Almacén Nuevo",
                                      command=self.abrir_formulario_nuevo,
                                      bootstyle="success")
        self.btn_agregar.pack(side="right")

        # Frame de Filtros
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=(0, 10), padx=20, fill="x", anchor="e")

        self.btn_filtros = ttk.Button(filter_frame, text="⚙️ Filtros Avanzados",
                                      command=self.abrir_ventana_filtros,
                                      bootstyle="info")
        self.btn_filtros.pack(side="right")
        
        self.btn_limpiar = ttk.Button(filter_frame, text="🔄 Ver Todo",
                                      command=self.cargar_almacenes,
                                      bootstyle="secondary-outline")
        self.btn_limpiar.pack(side="right", padx=5)

        # Título
        label = ttk.Label(self, text="Gestión de Almacenes", font=("Arial", 18, "bold"), bootstyle="primary")
        label.pack(pady=5)
        
        # Tabla
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, selectmode="extended", bootstyle="secondary")
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        self.tree["columns"] = ("id", "nombre", "fecha_mod", "usuario_mod")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("id", anchor=tk.W, width=50)
        self.tree.column("nombre", anchor=tk.W, width=200)
        self.tree.column("fecha_mod", anchor=tk.W, width=150)
        self.tree.column("usuario_mod", anchor=tk.W, width=100)

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("id", text="ID", anchor=tk.W)
        self.tree.heading("nombre", text="Nombre", anchor=tk.W)
        self.tree.heading("fecha_mod", text="Última Modificación", anchor=tk.W)
        self.tree.heading("usuario_mod", text="Modificado por", anchor=tk.W)

        # --- CORRECCIÓN: Crear la etiqueta ANTES de cargar ---
        self.label_feedback = ttk.Label(self, text="", font=("Arial", 12))
        self.label_feedback.pack(pady=5)

        self.cargar_almacenes()
        
        self.tree.bind("<Double-1>", self.abrir_formulario_editar)
        self.aplicar_permisos()

    def cargar_almacenes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, fecha_ultima_modificacion, ultimo_usuario_en_modificar FROM almacenes")
            for row in cursor.fetchall():
                self.tree.insert(parent="", index="end", values=row)
            
            if hasattr(self, 'label_feedback'):
                self.label_feedback.config(text="")
                
        except sqlite3.Error as e:
            if hasattr(self, 'label_feedback'):
                self.label_feedback.config(text=f"Error en BD: {e}", bootstyle="danger")
            else:
                print(f"Error en BD: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def abrir_ventana_filtros(self):
        ventana = ttk.Toplevel(self)
        ventana.title("Filtros de Almacenes")
        ventana.geometry("350x350") # Ajustado altura
        
        ttk.Label(ventana, text="Filtrar Almacenes", font=("Arial", 14, "bold"), bootstyle="primary").pack(pady=10)
        
        form_frame = ttk.Frame(ventana)
        form_frame.pack(padx=20, pady=10, fill="x")

        # Campo: Nombre
        ttk.Label(form_frame, text="Nombre contiene:").pack(anchor="w")
        entry_nombre = ttk.Entry(form_frame)
        entry_nombre.pack(fill="x", pady=(0, 5))

        # Campo: Usuario
        ttk.Label(form_frame, text="Modificado por (Usuario):").pack(anchor="w")
        entry_usuario = ttk.Entry(form_frame)
        entry_usuario.pack(fill="x", pady=(0, 5))

        # --- NUEVO: Campo Fecha ---
        ttk.Label(form_frame, text="Fecha Modificación (contiene):").pack(anchor="w")
        entry_fecha = ttk.Entry(form_frame)
        entry_fecha.pack(fill="x", pady=(0, 5))
        # --------------------------

        btn_buscar = ttk.Button(ventana, text="🔍 BUSCAR", 
                                bootstyle="success", 
                                command=lambda: self.ejecutar_busqueda_avanzada(
                                    ventana, 
                                    entry_nombre.get(),
                                    entry_usuario.get(),
                                    entry_fecha.get() # Nuevo
                                ))
        btn_buscar.pack(pady=20, fill="x", padx=20)

    def ejecutar_busqueda_avanzada(self, ventana, nombre, usuario_mod, fecha_mod):
        ventana.destroy()
        
        sql = """
            SELECT id, nombre, fecha_ultima_modificacion, ultimo_usuario_en_modificar 
            FROM almacenes 
            WHERE 1=1 
        """
        params = []

        if nombre:
            sql += " AND nombre LIKE ?"
            params.append(f"%{nombre}%")
        
        if usuario_mod:
            sql += " AND ultimo_usuario_en_modificar LIKE ?"
            params.append(f"%{usuario_mod}%")

        # --- NUEVO FILTRO SQL ---
        if fecha_mod:
            sql += " AND fecha_ultima_modificacion LIKE ?"
            params.append(f"%{fecha_mod}%")
        # ------------------------

        for i in self.tree.get_children():
            self.tree.delete(i)
            
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            
            filas = cursor.fetchall()
            if not filas:
                self.label_feedback.config(text="No se encontraron almacenes.", bootstyle="warning")
            else:
                self.label_feedback.config(text=f"Se encontraron {len(filas)} almacenes.", bootstyle="success")
                for row in filas:
                    self.tree.insert(parent="", index="end", values=row)
                
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error en búsqueda: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def aplicar_permisos(self):
        rol = self.controller.current_user_role
        if rol not in ['ADMIN', 'ALMACENES']:
            self.btn_agregar.config(state="disabled")
            self.tree.unbind("<Double-1>")
            self.label_feedback.config(text="Modo de solo lectura. Rol no autorizado para editar.", bootstyle="info")

    def abrir_formulario_nuevo(self):
        self.controller.navegar_a_edicion("FormularioEdicionAlmacen", None)

    def abrir_formulario_editar(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        valores = self.tree.item(selected_item, 'values')
        item_id = valores[0]
        self.controller.navegar_a_edicion("FormularioEdicionAlmacen", item_id)


# --- NUEVA CLASE: Formulario de Edición de Productos ---

class FormularioEdicionProducto(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.item_id = None
        
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=20, padx=20, fill="x")

        btn_home = ttk.Button(top_frame, text="< Volver a la Lista de Productos",
                             command=self.volver_a_lista,
                             bootstyle="link")
        btn_home.pack(side="left")

        # Título dinámico
        self.label_titulo = ttk.Label(self, text="Agregar Producto Nuevo", font=("Arial", 18, "bold"), bootstyle="primary")
        self.label_titulo.pack(pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=40, fill="x")

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = ttk.Entry(form_frame, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Precio:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_precio = ttk.Entry(form_frame, width=20)
        self.entry_precio.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_cantidad = ttk.Entry(form_frame, width=40)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Departamento:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_depto = ttk.Entry(form_frame, width=20)
        self.entry_depto.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Almacén:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.combo_almacen = ttk.Combobox(form_frame, width=38, state="readonly")
        self.combo_almacen.grid(row=2, column=1, padx=5, pady=5)
        self.almacenes_map = {} 

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20, padx=40, fill="x")

        self.btn_guardar = ttk.Button(btn_frame, text="GUARDAR NUEVO", 
                                     bootstyle="success", command=self.guardar_nuevo)
        self.btn_guardar.pack(side="right", padx=5)

        self.btn_actualizar = ttk.Button(btn_frame, text="ACTUALIZAR", 
                                        bootstyle="info", command=self.actualizar_existente)
        self.btn_actualizar.pack(side="right", padx=5)

        self.btn_eliminar = ttk.Button(btn_frame, text="ELIMINAR", 
                                      bootstyle="danger", command=self.eliminar_item)
        self.btn_eliminar.pack(side="left", padx=5)
        
        self.label_feedback = ttk.Label(self, text="", font=("Arial", 12))
        self.label_feedback.pack(pady=5)

    def cargar_datos(self, item_id=None):
        self.item_id = item_id
        
        self.entry_nombre.delete(0, 'end')
        self.entry_precio.delete(0, 'end')
        self.entry_cantidad.delete(0, 'end')
        self.entry_depto.delete(0, 'end')
        self.label_feedback.config(text="")
        
        self.cargar_opciones_almacen()
        
        if item_id is None:
            # MODO AGREGAR
            self.label_titulo.config(text="Agregar Producto Nuevo")
            self.combo_almacen.set("") 
            self.btn_guardar.pack(side="right", padx=5)
            self.btn_actualizar.pack_forget()
            self.btn_eliminar.pack_forget()
        else:
            # MODO EDITAR
            self.label_titulo.config(text="Editar Producto")
            self.btn_guardar.pack_forget()
            self.btn_actualizar.pack(side="right", padx=5)
            self.btn_eliminar.pack(side="left", padx=5)
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, precio, cantidad, departamento, almacen FROM productos WHERE id = ?", (item_id,))
                data = cursor.fetchone()
                
                if data:
                    self.entry_nombre.insert(0, data[0])
                    self.entry_precio.insert(0, data[1] if data[1] else "")
                    self.entry_cantidad.insert(0, data[2] if data[2] else "")
                    self.entry_depto.insert(0, data[3] if data[3] else "")
                    
                    id_to_name_map = {v: k for k, v in self.almacenes_map.items()}
                    nombre_almacen = id_to_name_map.get(data[4])
                    self.combo_almacen.set(nombre_almacen if nombre_almacen else "")
            except sqlite3.Error as e:
                self.label_feedback.config(text=f"Error al cargar datos: {e}", bootstyle="danger")
            finally:
                if 'conn' in locals():
                    conn.close()

    def cargar_opciones_almacen(self):
        self.almacenes_map = {}
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM almacenes ORDER BY nombre")
            opciones = []
            for row in cursor.fetchall():
                opciones.append(row[1])
                self.almacenes_map[row[1]] = row[0]
            self.combo_almacen['values'] = opciones
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al cargar almacenes: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def guardar_nuevo(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            nombre = self.entry_nombre.get()
            precio = self.entry_precio.get() or None # Guardar NULL si está vacío
            cantidad = self.entry_cantidad.get() or None
            departamento = self.entry_depto.get() or None
            nombre_almacen = self.combo_almacen.get()
            
            fecha = datetime.datetime.now().isoformat()
            usuario = self.controller.current_user_name

            if not nombre or not nombre_almacen:
                self.label_feedback.config(text="Nombre y Almacén son obligatorios", bootstyle="warning")
                return

            almacen_id = self.almacenes_map.get(nombre_almacen)
            
            cursor.execute("""
                INSERT INTO productos (nombre, precio, cantidad, departamento, almacen, fecha_ultima_modificacion, ultimo_usuario_en_modificar)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, precio, cantidad, departamento, almacen_id, fecha, usuario))
            
            conn.commit()
            self.label_feedback.config(text="¡Producto guardado con éxito!", bootstyle="success")
            
            self.entry_nombre.delete(0, 'end')
            self.entry_precio.delete(0, 'end')
            self.entry_cantidad.delete(0, 'end')
            self.entry_depto.delete(0, 'end')
            self.combo_almacen.set("")
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al guardar: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def actualizar_existente(self):
        if not self.item_id:
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            nombre = self.entry_nombre.get()
            precio = self.entry_precio.get() or None
            cantidad = self.entry_cantidad.get() or None
            departamento = self.entry_depto.get() or None
            nombre_almacen = self.combo_almacen.get()
            
            fecha = datetime.datetime.now().isoformat()
            usuario = self.controller.current_user_name

            if not nombre or not nombre_almacen:
                self.label_feedback.config(text="Nombre y Almacén son obligatorios", bootstyle="warning")
                return

            almacen_id = self.almacenes_map.get(nombre_almacen)
            
            cursor.execute("""
                UPDATE productos SET 
                    nombre = ?, precio = ?, cantidad = ?, departamento = ?, almacen = ?, 
                    fecha_ultima_modificacion = ?, ultimo_usuario_en_modificar = ?
                WHERE id = ?
            """, (nombre, precio, cantidad, departamento, almacen_id, fecha, usuario, self.item_id))
            
            conn.commit()
            self.label_feedback.config(text="¡Producto actualizado con éxito!", bootstyle="success")
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al actualizar: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def eliminar_item(self):
        if not self.item_id:
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (self.item_id,))
            conn.commit()
            self.volver_a_lista()
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al eliminar: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def volver_a_lista(self):
        self.controller.regresar_a_lista("FormularioProductos")


# --- NUEVA CLASE: Formulario de Edición de Almacenes ---

class FormularioEdicionAlmacen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.item_id = None
        
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=20, padx=20, fill="x")

        btn_home = ttk.Button(top_frame, text="< Volver a la Lista de Almacenes",
                             command=self.volver_a_lista,
                             bootstyle="link")
        btn_home.pack(side="left")

        # Título dinámico
        self.label_titulo = ttk.Label(self, text="Agregar Almacén Nuevo", font=("Arial", 18, "bold"), bootstyle="primary")
        self.label_titulo.pack(pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10, padx=40, fill="x")

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = ttk.Entry(form_frame, width=40)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20, padx=40, fill="x")

        self.btn_guardar = ttk.Button(btn_frame, text="GUARDAR NUEVO", 
                                     bootstyle="success", command=self.guardar_nuevo)
        self.btn_guardar.pack(side="right", padx=5)

        self.btn_actualizar = ttk.Button(btn_frame, text="ACTUALIZAR", 
                                        bootstyle="info", command=self.actualizar_existente)
        self.btn_actualizar.pack(side="right", padx=5)

        self.btn_eliminar = ttk.Button(btn_frame, text="ELIMINAR", 
                                      bootstyle="danger", command=self.eliminar_item)
        self.btn_eliminar.pack(side="left", padx=5)
        
        self.label_feedback = ttk.Label(self, text="", font=("Arial", 12))
        self.label_feedback.pack(pady=5)

    def cargar_datos(self, item_id=None):
        self.item_id = item_id
        self.entry_nombre.delete(0, 'end')
        self.label_feedback.config(text="")
        
        if item_id is None:
            # MODO AGREGAR
            self.label_titulo.config(text="Agregar Almacén Nuevo")
            self.btn_guardar.pack(side="right", padx=5)
            self.btn_actualizar.pack_forget()
            self.btn_eliminar.pack_forget()
        else:
            # MODO EDITAR
            self.label_titulo.config(text="Editar Almacén")
            self.btn_guardar.pack_forget()
            self.btn_actualizar.pack(side="right", padx=5)
            self.btn_eliminar.pack(side="left", padx=5)
            
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM almacenes WHERE id = ?", (item_id,))
                data = cursor.fetchone()
                if data:
                    self.entry_nombre.insert(0, data[0])
            except sqlite3.Error as e:
                self.label_feedback.config(text=f"Error al cargar datos: {e}", bootstyle="danger")
            finally:
                if 'conn' in locals():
                    conn.close()

    def guardar_nuevo(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            nombre = self.entry_nombre.get()
            fecha = datetime.datetime.now().isoformat()
            usuario = self.controller.current_user_name

            if not nombre:
                self.label_feedback.config(text="El Nombre es obligatorio", bootstyle="warning")
                return
            
            cursor.execute("""
                INSERT INTO almacenes (nombre, fecha_ultima_modificacion, ultimo_usuario_en_modificar)
                VALUES (?, ?, ?)
            """, (nombre, fecha, usuario))
            
            conn.commit()
            self.label_feedback.config(text="¡Almacén guardado con éxito!", bootstyle="success")
            self.entry_nombre.delete(0, 'end')

        except sqlite3.IntegrityError:
             self.label_feedback.config(text=f"Error: El almacén '{nombre}' ya existe", bootstyle="danger")
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al guardar: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def actualizar_existente(self):
        if not self.item_id:
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            nombre = self.entry_nombre.get()
            fecha = datetime.datetime.now().isoformat()
            usuario = self.controller.current_user_name

            if not nombre:
                self.label_feedback.config(text="El Nombre es obligatorio", bootstyle="warning")
                return
            
            cursor.execute("""
                UPDATE almacenes SET 
                    nombre = ?, fecha_ultima_modificacion = ?, ultimo_usuario_en_modificar = ?
                WHERE id = ?
            """, (nombre, fecha, usuario, self.item_id))
            
            conn.commit()
            self.label_feedback.config(text="¡Almacén actualizado con éxito!", bootstyle="success")
        except sqlite3.IntegrityError:
             self.label_feedback.config(text=f"Error: El nombre '{nombre}' ya existe", bootstyle="danger")
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al actualizar: {e}", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def eliminar_item(self):
        if not self.item_id:
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM almacenes WHERE id = ?", (self.item_id,))
            conn.commit()
            self.volver_a_lista()
        except sqlite3.Error as e:
            self.label_feedback.config(text=f"Error al eliminar: {e}", bootstyle="danger")
            if "FOREIGN KEY" in str(e):
                 self.label_feedback.config(text="Error: No se puede borrar, almacén en uso por productos", bootstyle="danger")
        finally:
            if 'conn' in locals():
                conn.close()

    def volver_a_lista(self):
        self.controller.regresar_a_lista("FormularioAlmacenes")


# --- Clase Principal de la Aplicación ---

class App(ttk.Window):
    
    # El método __init__ debe estar indentado
    def __init__(self):
        
        # --- PASO 1: Crear la ventana principal PRIMERO ---
        super().__init__(themename="litera") 

        # --- PASO 3: Definir el tema "unison" usando 'self.style' (que ya existe) ---
        self.style.theme_create("unison", parent="litera", settings={
            "colors": {
                'primary': '#00529e',      # Azul Unison
                'secondary': '#f8bb00',    # Dorado Unison
                'success': '#4CAF50',
                'info': '#01509b',        # Azul Unison Oscuro
                'warning': '#d99e30',     # Dorado Unison Oscuro
                'danger': '#f44336',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'bg': 'white',
                'fg': 'black',
                'selectbg': '#01509b',
                'selectfg': 'white',
                'border': '#dee2e6'
            },
            "TFrame": {"configure": {"background": "white"}},
            "TLabel": {"configure": {"background": "white"}},
            "Treeview": {"configure": {"background": "white", "fieldbackground": "white"}},
            "TCombobox": {"configure": {"selectbackground": "white", "fieldbackground": "white"}}
        })
        
        # --- PASO 4: Aplicar el nuevo tema ---
        self.style.theme_use("unison")

        # --- El resto del código de __init__ sigue igual ---
        self.title("Sistema de Inventario Unison")
        self.geometry("1100x700") 
        
        self.current_user_name = None
        self.current_user_role = None

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame_login = LoginPage(parent=container, controller=self)
        self.frames["LoginPage"] = frame_login
        frame_login.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    # --- INICIO DE MÉTODOS DE APP (INDENTADOS) ---
    
    def show_frame(self, page_name):
        """Muestra un frame por su nombre"""
        frame = self.frames[page_name]
        frame.tkraise()

    def login_exitoso(self, user_name, user_role):
        self.current_user_name = user_name
        self.current_user_role = user_role
        
        container = self.frames["LoginPage"].master 

        for F in (HomePage, FormularioProductos, FormularioAlmacenes, 
                  FormularioEdicionProducto, FormularioEdicionAlmacen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")
        
    def navegar_a_edicion(self, page_name, item_id):
        """
        Función especial para navegar a un formulario de edición,
        pasándole el ID del ítem (o None si es nuevo).
        """
        frame = self.frames[page_name]
        frame.cargar_datos(item_id) # Prepara el formulario
        frame.tkraise()              # Muestra el formulario

    def regresar_a_lista(self, page_name):
        """
        Función para volver a una lista, asegurándose
        de recargar los datos de la tabla.
        """
        lista_frame = self.frames[page_name]
        
        if page_name == "FormularioProductos":
            lista_frame.cargar_productos()
        elif page_name == "FormularioAlmacenes":
            lista_frame.cargar_almacenes()
            
        lista_frame.tkraise()
    
    # --- FIN DE MÉTODOS DE APP ---
        

# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    app = App()
    app.mainloop()