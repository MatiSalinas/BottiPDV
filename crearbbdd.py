import sqlite3

# Conectar a la base de datos (creará el archivo de base de datos si no existe)
conn = sqlite3.connect('bottiglia.db')
cursor = conn.cursor()

# Crear la tabla Producto si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE NOT NULL,
        precio REAL NOT NULL,
        precio_compra REAL NOT NULL,
        cantidad INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Promos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT NOT NULL,
        precio REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProductosPromo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo_producto TEXT NOT NULL,
        codigo_promo TEXT NOT NULL,
        cantidad INTEGER NOT NULL
    )
''')

# Crear la tabla Libro si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bebida (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE NOT NULL,
        precio REAL NOT NULL,
        precio_compra REAL NOT NULL,
        cantidad INTEGER NOT NULL,
        tipo TEXT NOT NULL
    )
''')

# Crear la tabla Ventas si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_articulo TEXT,
        nombre_articulo TEXT,
        precio_unitario REAL,
        cantidad_vendida INTEGER,
        total REAL NOT NULL,
        turno_id INTEGER NOT NULL
    )
''')

# Crear la tabla Caja si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turno INTEGER NOT NULL,
        vendedor TEXT NOT NULL,
        num_ventas INTEGER NOT NULL,
        sobrante INTEGER NOT NULL,
        caja REAL NOT NULL,
        estado BIT DEFAULT 0
    )
''')

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()