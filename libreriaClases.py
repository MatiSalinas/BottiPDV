#Grupo 19 libreria

import sqlite3
#TO DO
#interfaz grafica para el programa
class Promo:
    def __init__(self,nombre,codigo,precio,productos=[]):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.productos = productos
        
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()

    def agregar_productos(self,producto,cantidad_producto):
        self.productos.append((producto,cantidad_producto))
    def insertar_promo(self):
        self.cursor.execute('''
        INSERT INTO promos (nombre,codigo,precio)
        VALUES (?,?,?)''',(self.nombre,self.codigo,self.precio))
        self.conn.commit()

        for tupla in self.productos:
            self.cursor.execute('''
            INSERT INTO ProductosPromo (nombre,codigo_producto,codigo_promo,cantidad)
            VALUES (?,?,?,?)''',(tupla[0].nombre,tupla[0].codigo,self.codigo,tupla[1]))
            self.conn.commit()

    def Actualizar_venta(self,unidades):
        for tupla in self.productos:
            tupla[0].Actualizar_venta(tupla[1]*unidades)



class Producto:
    def __init__(self,nombre,codigo,precio,precio_compra,cantidad):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.precio_compra = precio_compra
        self.cantidad = cantidad
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()
    def editar(self,nombre,precio,cantidad):
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
    def editar_tabla(self, nombre, precio, cantidad):
        
        self.cursor.execute('''
            UPDATE Producto
            SET nombre = ?, precio = ?, cantidad = ?
            WHERE codigo = ?
        ''', (nombre, precio, cantidad, self.codigo))
        self.conn.commit()
    
    def insertar_producto(self):
        self.cursor.execute('''
        INSERT INTO Producto (nombre, codigo, precio, cantidad)
        VALUES (?, ?, ?, ?)''', (self.nombre, self.codigo, self.precio, self.cantidad))
        self.conn.commit()
    def Actualizar_venta(self,unidades):
        self.cantidad -= unidades
        self.cursor.execute('''
            UPDATE Producto
            SET cantidad = ?
            WHERE codigo = ?
        ''', ( self.cantidad, self.codigo))
        self.conn.commit()
''''nombre
codigo
precio
precio_compra
cantidad
tipo'''
class Bebida(Producto):
    def __init__(self,nombre,codigo,precio,precio_compra,cantidad,tipo):
        super().__init__(nombre,codigo,precio,precio_compra,cantidad)
        self.tipo = tipo
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()

    def editar(self,nombre,precio,precio_compra,cantidad,tipo):
        self.nombre = nombre
        self.precio = precio
        self.cantidad = cantidad
        self.precio_compra = precio_compra
        self.tipo = tipo   
    def editar_tabla(self, nombre, precio, precio_compra,cantidad,tipo):
        
        self.cursor.execute('''
            UPDATE Libro
            SET nombre = ?, precio = ?, precio_compra = ?,cantidad = ?, tipo = ?
            WHERE codigo = ?
        ''', (nombre, precio, precio_compra,cantidad, tipo, self.codigo))
        self.conn.commit()

    def __str__(self):
        return f"{self.nombre} {self.precio}"
    def insertar_libro(self):
        self.cursor.execute('''
        INSERT INTO Bebida (nombre, codigo, precio,precio_compra,cantidad, tipo)
        VALUES (?, ?, ?, ?, ?, ?)''', (self.nombre, self.codigo, self.precio,self.precio_compra,self.cantidad, self.tipo))
        self.conn.commit()
    def Actualizar_venta(self,unidades):
        self.cantidad -= unidades
        self.cursor.execute('''
            UPDATE Bebida
            SET cantidad = ?
            WHERE codigo = ?
        ''', ( self.cantidad, self.codigo))
        self.conn.commit()


class Inventario:
    def __init__(self):
        self.lista_inventario= []
        self.lista_cajas = []
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()

    def agregar_inventario(self,producto):
        for producto_existente in self.lista_inventario:
            if producto.codigo == producto_existente.codigo:
                print('Ya existe un producto con ese nombre')
                return 0
        self.lista_inventario.append(producto)

    def actualizar_inventario_post_venta(self,codigo,cantidad):
        for producto_existente in self.lista_inventario:
            if str(producto_existente.codigo) == str(codigo):
                producto_existente.Actualizar_venta(cantidad)


    def cargar_cajas_desde_bd(self):
        #Recupera las cajas desde la tabla Cajas
        self.cursor.execute('''SELECT turno, vendedor, num_ventas, sobrante, caja, estado FROM Caja''')
        cajas =self.cursor.fetchall()

        for caja_data in cajas:
            turno, vendedor, num_ventas,sobrante,caja,estado = caja_data
            cajita = Caja(turno, vendedor)
            cajita.num_ventas = num_ventas
            cajita.sobranteFaltante = sobrante
            cajita.caja = caja
            cajita.estado = estado
            self.lista_cajas.append(cajita)

    def abrir_caja(self,turno,cajero):
        cajita = Caja(turno, cajero)
        self.lista_cajas.append(cajita)

    def cargar_inventario_desde_bd(self):
        # Recupera los productos de la tabla Producto
        self.cursor.execute('SELECT nombre, codigo, precio, cantidad FROM Producto')
        productos = self.cursor.fetchall()
        
        # Recupera los libros de la tabla Libro
        self.cursor.execute('SELECT nombre, codigo, precio,precio_compra,cantidad,tipo FROM Bebida')
        bebidas = self.cursor.fetchall()
        
        self.cursor.execute('SELECT nombre,codigo,precio FROM Promos')
        promos= self.cursor.fetchall()

        # Crea objetos de productos y libros y los agrega al inventario
        for producto_data in productos:
            nombre, codigo, precio, cantidad = producto_data
            producto = Producto(nombre, int(codigo), precio, cantidad)
            self.lista_inventario.append(producto)

        
        for bebida_data in bebidas:
            nombre, codigo, precio,precio_compra,cantidad, tipo = bebida_data
            bebida = Bebida(nombre, int(codigo), precio,precio_compra, int(cantidad), tipo) 
            self.lista_inventario.append(bebida)

        for promos_data in promos:
            nombre,codigo,precio = promos_data
            promo = Promo(nombre,codigo,precio)
            self.cursor.execute('SELECT codigo_producto, cantidad FROM ProductosPromo WHERE codigo_promo = ?',(promo.codigo,))
            promos_productos= self.cursor.fetchall()
            for producto in promos_productos:
                codigo_producto,cantidad_producto = producto
                for producto_existente in self.lista_inventario:
                    if str(producto_existente.codigo) == str(codigo_producto):
                        promo.agregar_productos(producto_existente,cantidad_producto)
            self.lista_inventario.append(promo)

    def eliminar_libro(self, codigo):
        for producto_existente in self.lista_inventario:
            if int(codigo) == producto_existente.codigo:
                self.lista_inventario.remove(producto_existente)
                self.cursor.execute('DELETE FROM Bebida WHERE codigo = ?', (codigo,))
                self.conn.commit()
    
    def eliminar_producto(self, codigo):
        for producto_existente in self.lista_inventario:
            if int(codigo) == producto_existente.codigo:
                self.lista_inventario.remove(producto_existente)
                self.cursor.execute('DELETE FROM Producto WHERE codigo = ?', (codigo,))
                self.conn.commit()

class Venta:
    def __init__(self,turno_asociado):
        self.articulos = []
        self.total = 0
        self.turno_asociado = turno_asociado
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()
    
    def agregar_venta(self,codigo,nombre,precio,cantidad):
        dicionarioVenta = {'codigo_articulo': codigo,
        'nombre_articulo': nombre,
        'precio_unitario': precio,
        'cantidad_vendida': cantidad}
        self.articulos.append(dicionarioVenta)
        


    def calcular_total(self):
        self.total = 0
        for articulo in self.articulos:
            self.total += articulo['precio_unitario'] * articulo['cantidad_vendida']
        return self.total

    def insertar_venta(self):
        for articulo in self.articulos:
            total = articulo['precio_unitario']*articulo['cantidad_vendida'] 
            self.cursor.execute('''
            INSERT INTO Ventas (codigo_articulo, nombre_articulo, precio_unitario, cantidad_vendida, total, turno_id)
            VALUES (?, ?, ?, ?, ?, ?)''', (articulo['codigo_articulo'], articulo['nombre_articulo'],articulo['precio_unitario'],articulo['cantidad_vendida'] ,total,self.turno_asociado))
            self.conn.commit()



class Caja:
    def __init__(self,turno,vendedor):
        self.turno =  turno
        self.vendedor =  vendedor
        self.num_ventas = 0
        self.ventas =  []
        self.caja =  0
        self.sobranteFaltante = 0
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()
        self.estado = False
    def crear_venta(self):
        venta = Venta(self.turno)
        self.ventas.append(venta)
    def vender(self,total):
        self.num_ventas += 1
        self.caja = self.caja + total
        

    def abrir_caja(self,vendedor):
        self.estado = True
        self.turno +=1
        self.caja = 0
        self.vendedor = vendedor
        self.num_ventas =0
        self.ventas.clear()
    
    def cerrar_caja(self):
        self.estado = True
    
    def calcular_ingresos(self):
        self.cursor.execute("SELECT total FROM Ventas WHERE turno_id = ?", (self.turno,))
        resultados = self.cursor.fetchall()
        total = 0
        for resultado in resultados:
            total += resultado[0]
        return total

    
    def insertar_caja(self):
        self.cursor.execute('''
        INSERT INTO Caja (turno, vendedor, num_ventas,sobrante ,caja, estado)
        VALUES (?, ?, ?, ?, ?, ?)''', (self.turno, self.vendedor, self.num_ventas, self.sobranteFaltante,self.caja,self.estado))
        self.conn.commit()
    def Actualizar_Caja(self):
        self.cursor.execute('''
            UPDATE Caja
            SET num_ventas = ?,
            sobrante = ?,
            caja = ?,
            estado = ?
            WHERE turno = ?
        ''', ( self.num_ventas, self.sobranteFaltante,self.caja ,self.estado,self.turno))
        self.conn.commit()




caja = Caja(0, "matias")


