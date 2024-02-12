import libreriaClases
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidgetItem, QAbstractItemView , QDialog, QMessageBox, QPushButton
from PyQt6.QtCore import QTime,QTimer
import sqlite3
import csv

#Todo, crear ventana que inicialice la caja y el inventario

inventario = libreriaClases.Inventario()

inventario.cargar_inventario_desde_bd()
inventario.cargar_cajas_desde_bd()

class Mi_Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ventanaPrincipal.ui',self)
        
        #Acomodamos las columnas de la tabla para que esten bien espaciadas
        tabla_ancho = self.tableWidget.width()
        self.tableWidget.setColumnWidth(0, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(1, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(2, int(tabla_ancho*(1/4)))
        self.tableWidget.setColumnWidth(3, int(tabla_ancho*(1/5)))
        self.tableWidget.setColumnWidth(4, int(tabla_ancho*(1/5)))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas


        self.tablaLibros.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas

        self.tablaProductos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas

        self.cargar_inventarioL()#Cargamos el inventario en las tablas de inventario
        self.cargar_inventarioP()
        self.des_habilitar_ventas()

        #seniales para la venta
        self.codigo_barras.returnPressed.connect(self.agregar_producto_codigo)
        self.botonFinalizarVenta.clicked.connect(self.finalizar_venta)
        self.botonAnular.clicked.connect(self.anular_venta)
        self.botonEliminarArticulo.clicked.connect(self.remover_articulo)

        #seniales en los botones de menu
        self.abrirTurno.triggered.connect(self.abrir_caja)
        self.botonCierreCaja.triggered.connect(self.cierre_caja)
        self.botonRendicionCaja.triggered.connect(self.rendicion_caja)
        self.reporte_Ventas.triggered.connect(self.reporte_ventas)
        self.botonPromo.triggered.connect(self.CrearPromo)
        self.editar_promo.triggered.connect(self.editarPromos)
        #ponemos la imagen de lupa como el icono del boton
        self.lupa.setIcon(QtGui.QIcon('lupo.png'))
        self.lupa.setIconSize(QtCore.QSize(self.lupa.width(),self.lupa.height()))


        #ventana buscar conectada a el input de nombre
        self.ventanaBusqueda = VentanaBuscar(self)
        self.nombre_producto.returnPressed.connect(self.buscar_producto)
        self.lupa.clicked.connect(self.buscar_producto)

        self.ventanaCierre = VentanaCierre()
        self.ventanaReporte = VentanaReportVentas()
        self.ventanaEditarPromos = VentanaEditarPromo()

        #RELOJ
        self.lcdNumber.setDigitCount(8)  # Para mostrar una hora en formato HH:MM:SS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)  # Actualizar cada segundo (1000 ms)


        #Compras
        self.rb_crearLibro.toggled.connect(self.ComprasRadio)
        self.rb_CrearProducto.toggled.connect(self.ComprasRadio)
        self.rb_entradaLibro.toggled.connect(self.ComprasRadio)
        self.rb_entradaProducto.toggled.connect(self.ComprasRadio)
        self.ingreso_codigo.editingFinished.connect(self.cargar_compras_codigo)
        self.botonGuardarCompras.clicked.connect(self.guardar_compra)
        validador = QtGui.QIntValidator(0, 10000000)
        validador_float = QtGui.QDoubleValidator(0.00,999999.99,2)
        self.ingreso_precio.setValidator(validador_float)
        self.ingreso_cantidad.setValidator(validador)
        

        #Inventario
        self.InventarioLBorrar.clicked.connect(self.BorrarLInventario)
        self.InventarioPBorrar.clicked.connect(self.BorrarPInventario)
        self.InventarioLEditar.clicked.connect(self.EditarLInventario)
        self.InventarioPEditar.clicked.connect(self.EditarPInventario)

        if inventario.lista_cajas[-1].estado:
            titulo = 'Recordatorio'
            cuerpo = 'Recuerde abrir una caja para proceder con las ventas'
            mensaje(titulo,cuerpo)

    def des_habilitar_ventas(self):
        if inventario.lista_cajas[-1].estado:
            self.principal.setTabEnabled(0,False) #deshabilita el tab con indice 0 
        else:
            self.principal.setTabEnabled(0,True)


    def cargar_inventarioL(self):
        #Todo 
        #re size las columnas asi ocupan toda la tabla
        fila = 0
        self.tablaLibros.setRowCount(fila)
        for item in inventario.lista_inventario:
            if type(item) == libreriaClases.Bebida:
                fila = self.tablaLibros.rowCount()
                self.tablaLibros.setRowCount(fila+1)
                self.tablaLibros.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaLibros.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaLibros.setItem(fila, 2, QTableWidgetItem(str(item.precio)))
                self.tablaLibros.setItem(fila, 3, QTableWidgetItem(str(item.precio_compra)))
                self.tablaLibros.setItem(fila, 4, QTableWidgetItem(str(item.cantidad)))
                self.tablaLibros.setItem(fila, 5, QTableWidgetItem(str(item.tipo)))

    def cargar_inventarioP(self):
        #Todo
        #re size las columnas asi ocupan toda la tabla
        fila = 0
        self.tablaProductos.setRowCount(fila)
        for item in inventario.lista_inventario:
            if type(item) == libreriaClases.Producto:
                fila = self.tablaProductos.rowCount()
                self.tablaProductos.setRowCount(fila + 1)
                self.tablaProductos.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaProductos.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaProductos.setItem(fila, 2, QTableWidgetItem(str(item.precio)))
                self.tablaProductos.setItem(fila, 3, QTableWidgetItem(str(item.cantidad)))

    def BorrarLInventario(self):
        try:
            fila = self.tablaLibros.currentRow()
            codigo = self.tablaLibros.item(fila,0).text()
            inventario.eliminar_libro(codigo)
            self.cargar_inventarioL()
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione una Bebida primero'
                    mensaje(titulo,cuerpo)
    
    def EditarLInventario(self):
        try:
            fila = self.tablaLibros.currentRow()
            codigo = self.tablaLibros.item(fila,0).text()
            nombre = self.tablaLibros.item(fila,1).text()
            precio = self.tablaLibros.item(fila,2).text()
            cantidad = self.tablaLibros.item(fila,3).text()
            autor = self.tablaLibros.item(fila,4).text()
            genero = self.tablaLibros.item(fila,5).text()
            anio = self.tablaLibros.item(fila,6).text()
            num = self.tablaLibros.item(fila,7).text()
        
        
            dialogo = DialogEditarLibro(codigo,nombre,precio,cantidad,autor,genero,anio,num)
            with open('stylesheet.qss','r') as file:
                dialogo.setStyleSheet(file.read())
            if(dialogo.exec()):
                nuevos_datos= dialogo.get_datos()
                codigo = int(nuevos_datos[0])
                nombre = nuevos_datos[1]
                precio = float(nuevos_datos[2])
                cantidad = int(nuevos_datos[3])
                autor = nuevos_datos[4]
                genero = nuevos_datos[5]
                anio = int(nuevos_datos[6])
                num = int(nuevos_datos[7])
                for productos_existentes in inventario.lista_inventario:
                    if str(productos_existentes.codigo) == str(codigo):

                        productos_existentes.editar(nombre,precio,cantidad,autor,genero,anio,num)
                        productos_existentes.editar_tabla(nombre,precio,cantidad,autor,genero,anio,num)
                        self.cargar_inventarioL()
        except AttributeError:
            titulo = 'Error'
            cuerpo = 'Seleccione un libro primero'
            mensaje(titulo,cuerpo)

    def EditarPInventario(self):
        try:
            fila = self.tablaProductos.currentRow()
            codigo = self.tablaProductos.item(fila,0).text()
            nombre = self.tablaProductos.item(fila,1).text()
            precio = self.tablaProductos.item(fila,2).text()
            cantidad = self.tablaProductos.item(fila,3).text()



            dialogo = DialogEditarProducto(codigo,nombre,precio,cantidad)
            with open('stylesheet.qss','r') as file:
                dialogo.setStyleSheet(file.read())
            if(dialogo.exec()):
                nuevos_datos= dialogo.get_datos()
                codigo = int(nuevos_datos[0])
                nombre = nuevos_datos[1]
                precio = float(nuevos_datos[2])
                cantidad = int(nuevos_datos[3])

                for productos_existentes in inventario.lista_inventario:
                    if str(productos_existentes.codigo) == str(codigo):

                        productos_existentes.editar(nombre,precio,cantidad)
                        productos_existentes.editar_tabla(nombre,precio,cantidad)
                        self.cargar_inventarioP()
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione un Producto primero'
                    mensaje(titulo,cuerpo)
    def BorrarPInventario(self):
        try:
            fila = self.tablaProductos.currentRow()
            codigo = self.tablaProductos.item(fila,0).text()
            inventario.eliminar_producto(codigo)
            self.cargar_inventarioP()
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione un Producto primero'
                    mensaje(titulo,cuerpo)
    def ComprasRadio(self):
        #Desactivamos o activamos los campos necesarios para cada opcion
        if self.rb_crearLibro.isChecked():
            self.ingreso_nombre.setEnabled(True)
            self.ingreso_precio.setEnabled(True)
            self.ingreso_precioC.setEnabled(True)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_tipo.setEnabled(True)
            
        if self.rb_CrearProducto.isChecked():
            self.ingreso_nombre.setEnabled(True)
            self.ingreso_precio.setEnabled(True)
            self.ingreso_precioC.setEnabled(True)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_tipo.setEnabled(False)

        if self.rb_entradaLibro.isChecked():
            self.ingreso_nombre.setEnabled(False)
            self.ingreso_precio.setEnabled(False)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_tipo.setEnabled(False)
        if self.rb_entradaProducto.isChecked():
            self.ingreso_nombre.setEnabled(False)
            self.ingreso_precio.setEnabled(False)
            self.ingreso_precioC.setEnabled(False)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_tipo.setEnabled(False)

    def cargar_compras_codigo(self):
        codigo = self.ingreso_codigo.text()
        if self.rb_crearLibro.isChecked():
            pass
            
        if self.rb_CrearProducto.isChecked():
            pass
        if self.rb_entradaLibro.isChecked():
            for producto_existente in inventario.lista_inventario:

                if codigo == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Bebida:
                    self.ingreso_nombre.setText(producto_existente.nombre)
                    self.ingreso_precio.setText(str(producto_existente.precio))
                    self.ingreso_precioC.setText(str(producto_existente.precio_compra))
                    return
            mensaje('Error','No hay una Bebida con ese codigo')
        if self.rb_entradaProducto.isChecked():
            for producto_existente in inventario.lista_inventario:
                if codigo == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Producto:
                    self.ingreso_nombre.setText(producto_existente.nombre)
                    self.ingreso_precio.setText(str(producto_existente.precio))
                    return
            mensaje('Error','No hay un producto con ese codigo')
    
    def guardar_compra(self):
        
        def limpiar():
            self.ingreso_codigo.setText('')
            self.ingreso_nombre.setText('')
            self.ingreso_precio.setText('')
            self.ingreso_precioC.setText('')
            self.ingreso_cantidad.setText('')
        if self.rb_crearLibro.isChecked():    
            try:
                codigo =int(self.ingreso_codigo.text())  
                for producto_existente in inventario.lista_inventario:
                    if codigo == producto_existente.codigo: 
                        mensaje('error','ese codigo ya existe')
                        self.ingreso_codigo.setText('')
                        return
                nombre = self.ingreso_nombre.text()
                precio = float(self.ingreso_precio.text())
                precio_compra = float(self.ingreso_precioC.text())
                cantidad = int(self.ingreso_cantidad.text())
                tipo = self.ingreso_tipo.currentText()
                bebidaNueva = libreriaClases.Bebida(nombre,codigo,precio,precio_compra,cantidad,tipo)
                inventario.lista_inventario.append(bebidaNueva)
                bebidaNueva.insertar_libro()
                self.cargar_inventarioL()
                limpiar()
            except ValueError:
                mensaje('error','Asegurese de llenar todos los campos')
        if self.rb_CrearProducto.isChecked():
            try:         
                codigo =int(self.ingreso_codigo.text())          
                for producto_existente in inventario.lista_inventario:
                    if codigo == producto_existente.codigo: 
                        mensaje('error','ese codigo ya existe')
                        self.ingreso_codigo.setText('')
                        return 
                nombre = self.ingreso_nombre.text()
                precio = float(self.ingreso_precio.text())
                cantidad = int(self.ingreso_cantidad.text())
                productoNuevo = libreriaClases.Producto(nombre,codigo,precio,cantidad)
                inventario.lista_inventario.append(productoNuevo)
                productoNuevo.insertar_producto()
                self.cargar_inventarioP()
                limpiar()
            except ValueError:
                mensaje('error','Asegurese de llenar todos los campos')
        if self.rb_entradaLibro.isChecked():
            codigo =int(self.ingreso_codigo.text())
            for producto_existente in inventario.lista_inventario:
                if str(codigo) == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Bebida:
                    cantidad = int(self.ingreso_cantidad.text()) + producto_existente.cantidad
                    producto_existente.cantidad += int(self.ingreso_cantidad.text())
                    producto_existente.editar_tabla(producto_existente.nombre,producto_existente.precio,producto_existente.precio_compra,cantidad,producto_existente.tipo)
                    limpiar()
                    self.cargar_inventarioL()
        if self.rb_entradaProducto.isChecked():
            codigo =int(self.ingreso_codigo.text())
            for producto_existente in inventario.lista_inventario:
                if str(codigo) == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Producto:
                    cantidad = int(self.ingreso_cantidad.text()) + producto_existente.cantidad
                    producto_existente.cantidad += int(self.ingreso_cantidad.text())
                    producto_existente.editar_tabla(producto_existente.nombre,producto_existente.precio,cantidad)
                    limpiar()
                    self.cargar_inventarioP()

    def CrearPromo(self):
        dialogo = DialogCrearPromo()
        with open('stylesheet.qss','r') as file:
            dialogo.setStyleSheet(file.read())
        if(dialogo.exec()):
            datos= dialogo.get_datos()

            for dato in datos:
                if len(dato) == 3:
                    for producto_existente in inventario.lista_inventario:
                        if str(dato[0]) == str(producto_existente.codigo):
                            mensaje('Error','Ya hay un producto/bebida con ese codigo')
                            return True
        
                    promita = libreriaClases.Promo(dato[1],dato[0],dato[2])
                else:
                    for productos in inventario.lista_inventario:
                        if str(productos.codigo) == dato[0]:
                            promita.agregar_productos(productos,dato[1])

            inventario.lista_inventario.append(promita)
            promita.insertar_promo()


    def abrir_caja(self):
        if inventario.lista_cajas[-1].estado:
            dialogo = DialogAperturaCaja()
            with open('stylesheet.qss','r') as file:
                dialogo.setStyleSheet(file.read())
            if(dialogo.exec()):
                datos= dialogo.get_datos()
                inventario.abrir_caja(int(datos[0]),datos[1])
                inventario.lista_cajas[-1].insertar_caja()
            
            self.des_habilitar_ventas()
        else:
            titulo = 'Error'
            cuerpo = 'Ya hay una caja abierta'
            mensaje(titulo,cuerpo)
    def cierre_caja(self):
        if inventario.lista_cajas[-1].estado:
            titulo = 'Error'
            cuerpo = 'La caja ya esta cerrada!'
            mensaje(titulo,cuerpo)
        else:
            inventario.lista_cajas[-1].cerrar_caja()
            titulo = 'Cierre'
            cuerpo = 'Caja cerrada!'
            mensaje(titulo,cuerpo)
            self.des_habilitar_ventas()
    def rendicion_caja(self):
        if inventario.lista_cajas[-1].estado:
            self.ventanaCierre.show()
            ingresos = str(inventario.lista_cajas[-1].calcular_ingresos())
            turno = str(inventario.lista_cajas[-1].turno)
            self.ventanaCierre.ingresosInput.setText(ingresos)
            self.ventanaCierre.numeroTurno.setText(turno)
        else:
            titulo = 'Error'
            cuerpo = 'Primero cierre la caja.'
            mensaje(titulo,cuerpo)
        
    def editarPromos(self):
        self.ventanaEditarPromos.show()
        self.ventanaEditarPromos.cargar_comboBox()
        with open('stylesheet.qss','r') as file:
            ventana.ventanaEditarPromos.setStyleSheet(file.read())
        
    def reporte_ventas(self):
        self.ventanaReporte.show()
        self.ventanaReporte.cargar_comboBox()

    def buscar_producto(self):
        with open('stylesheet.qss','r') as file:
            ventana.ventanaBusqueda.setStyleSheet(file.read())

        texto = self.nombre_producto.text()
        self.ventanaBusqueda.show()
        self.ventanaBusqueda.buscar.setText(texto)
    def actualizar_hora(self):
        # Obtener la hora actual
        hora_actual = QTime.currentTime()

        # Mostrar la hora actual en el QLCDNumber
        self.lcdNumber.display(hora_actual.toString("hh:mm:ss"))
    
    def agregar_producto_codigo(self):
        
        unidades = self.spinBox.value()
        codigo = int(self.codigo_barras.text())
        if unidades > 0:
            try:
                for producto_existente in inventario.lista_inventario:
                    if str(codigo) == str(producto_existente.codigo):
                        boton_mas = QPushButton('&+')
                        boton_mas.clicked.connect(self.boton_mas)
                        boton_menos = QPushButton('&-')
                        boton_menos.clicked.connect(self.boton_menos)
                        fila = self.tableWidget.rowCount()
                        self.tableWidget.setRowCount(fila + 1)
                        self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(producto_existente.codigo)))
                        self.tableWidget.setItem(fila, 1, QTableWidgetItem(producto_existente.nombre))
                        self.tableWidget.setItem(fila, 2, QTableWidgetItem(str(producto_existente.precio)))
                        self.tableWidget.setItem(fila, 3, QTableWidgetItem(str(unidades)))
                        self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*producto_existente.precio)))
                        self.tableWidget.setCellWidget(fila,5, boton_mas)
                        self.tableWidget.setCellWidget(fila,6, boton_menos)
                        self.tableWidget.setItem(fila, 6, QTableWidgetItem('Item para que se pueda remover el articulo'))
                        total =producto_existente.precio* unidades + float(self.total.text())
                        self.total.setText(str(total))

                        #Limpiamos los Qlineedit y spinbox
                        self.codigo_barras.setText('')
                        self.spinBox.setValue(1)
                        return 0
                titulo = 'Error'
                cuerpo = 'No existe un producto con ese codigo2!'
                mensaje(titulo,cuerpo)
            except AttributeError:
                titulo = 'Error'
                cuerpo = 'No existe un producto con ese codigo1!'
                mensaje(titulo,cuerpo)
    
    def boton_mas(self):
        fila = self.tableWidget.currentRow()
        unidades = int(self.tableWidget.item(fila,3).text())
        precio = float(self.tableWidget.item(fila,2).text())
        unidades += 1
        self.tableWidget.setItem(fila,3, QTableWidgetItem(str(unidades)))
        self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*precio)))
        total = float(self.total.text())
        total += precio
        self.total.setText(str(total))

    def boton_menos(self):
        fila = self.tableWidget.currentRow()
        unidades = int(self.tableWidget.item(fila,3).text())
        precio = float(self.tableWidget.item(fila,2).text())
        if unidades > 1:
            unidades -= 1
            self.tableWidget.setItem(fila,3, QTableWidgetItem(str(unidades)))
            self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*precio)))
            total = float(self.total.text())
            total -= precio
            self.total.setText(str(total))
        else:
            self.remover_articulo()
            print('entre')
    def remover_articulo(self):
        item = self.tableWidget.currentItem()
        if (item == None):
            print('que paso papu')
            return # no hacer nada si no hay un elemento seleccionado
        fila = item.row()
        totalArticulo = float(self.tableWidget.item(fila,4).text())
        total = float(self.total.text())
        total -= totalArticulo
        self.total.setText(str(total))
        self.tableWidget.removeRow(fila)


    def anular_venta(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.total.setText('0')


    def finalizar_venta(self):
        #Creamos un objeto venta al final de la lista ventas de caja
        if self.tableWidget.rowCount() == 0:
            return #el boton no hara nada si no hay ningun producto en la tabla
        
        inventario.lista_cajas[-1].crear_venta()
        for fila in range(self.tableWidget.rowCount()):
            codigo = self.tableWidget.item(fila,0).text()
            nombre = self.tableWidget.item(fila,1).text()
            precio = float(self.tableWidget.item(fila,2).text())
            cantidad = int(self.tableWidget.item(fila,3).text())
            inventario.lista_cajas[-1].ventas[-1].agregar_venta(codigo,nombre,precio,cantidad)#accedemos a la ultima venta de la caja y agregamos los productos a la venta
            inventario.actualizar_inventario_post_venta(codigo,cantidad)
        inventario.lista_cajas[-1].ventas[-1].insertar_venta()#guardamos la venta en la tabla ventas de la base de datos
        total = float(self.total.text())
        inventario.lista_cajas[-1].vender(total)#sumamos el total de la venta a la caja 
        inventario.lista_cajas[-1].Actualizar_Caja()#Guardamos los datos de la caja en caso de que el programa se cierre, asi mantendremos los datos
        self.cargar_inventarioL()#volvemos a cargar el inventario asi se ve reflejado en la tabla de inventario
        self.cargar_inventarioP()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.total.setText('0')

class VentanaBuscar(QMainWindow):
    def __init__(self,padre):
        super().__init__()
        uic.loadUi('ventanabuscar.ui',self)
        self.padre = padre
        self.lista_aux = []
        self.tablaBuscar.setColumnWidth(0, 156)
        self.tablaBuscar.setColumnWidth(1, 500)
        self.tablaBuscar.setColumnWidth(2, 156)
        self.tablaBuscar.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas
        self.buscar.textChanged.connect(self.filtrar)
        self.tablaBuscar.itemActivated.connect(self.elegir_producto)


    def elegir_producto(self):
        fila = self.tablaBuscar.currentRow()
        codigo = self.tablaBuscar.item(fila,0).text()
        self.padre.ventanaBusqueda.close()
        self.padre.codigo_barras.setText(codigo)
        self.padre.agregar_producto_codigo()
    def filtrar(self):
        self.tablaBuscar.clearContents()
        fila = 0
        self.tablaBuscar.setRowCount(fila)
        for item in inventario.lista_inventario:
            if self.buscar.text().lower() in item.nombre.lower():
                fila = self.tablaBuscar.rowCount()
                self.tablaBuscar.setRowCount(fila + 1)
                self.tablaBuscar.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaBuscar.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaBuscar.setItem(fila, 2, QTableWidgetItem(str(item.precio)))




class DialogEditarLibro(QDialog):
    def __init__(self,codigoActual,nombreActual,precioActual,cantidadActual,autorActual,generoActual,anioActual,numActual):
        super().__init__()
        uic.loadUi('QdialogLibro.ui',self)
        self.CodigoInput.setText(codigoActual)
        self.NombreInput.setText(nombreActual)
        self.PrecioInput.setText(precioActual)
        self.CantidadInput.setText(cantidadActual)
        self.AutorInput.setText(autorActual)
        self.GeneroInput.setText(generoActual)
        self.AnioInput.setText(anioActual)
        self.NumInput.setText(numActual)
        



    def get_datos(self):
        codigo = self.CodigoInput.text()
        Nombre = self.NombreInput.text()
        Precio = self.PrecioInput.text()
        Cantidad = self.CantidadInput.text()
        Autor = self.AutorInput.text()
        Genero = self.GeneroInput.text()
        Anio = self.AnioInput.text()
        Num = self.NumInput.text()

        return codigo,Nombre,Precio,Cantidad,Autor,Genero,Anio,Num
class DialogCrearPromo(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('Promos.ui',self)
        self.cantidadProductos()
        self.comboBox.currentTextChanged.connect(self.cantidadProductos)
        validador = QtGui.QIntValidator(0, 10000000)
        validador_float = QtGui.QDoubleValidator(0.00,999999.99,2)
        self.producto1_input.setValidator(validador)
        self.producto2_input.setValidator(validador)
        self.producto3_input.setValidator(validador)
        self.producto4_input.setValidator(validador)
        self.producto5_input.setValidator(validador)
        self.producto6_input.setValidator(validador)
        self.precioInput.setValidator(validador_float)

        self.producto1_input.editingFinished.connect(lambda: self.validador_codigo(1))
        self.producto2_input.editingFinished.connect(lambda: self.validador_codigo(2))
        self.producto3_input.editingFinished.connect(lambda: self.validador_codigo(3))
        self.producto4_input.editingFinished.connect(lambda: self.validador_codigo(4))
        self.producto5_input.editingFinished.connect(lambda: self.validador_codigo(5))
        self.producto6_input.editingFinished.connect(lambda: self.validador_codigo(6))


        
            

    def cantidadProductos(self):
        if self.comboBox.currentIndex() == 0:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(False)
            self.producto3_input.setEnabled(False)
            self.producto4_input.setEnabled(False)
            self.producto5_input.setEnabled(False)
            self.producto6_input.setEnabled(False)

        elif self.comboBox.currentIndex() == 1:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(True)
            self.producto3_input.setEnabled(False)
            self.producto4_input.setEnabled(False)
            self.producto5_input.setEnabled(False)
            self.producto6_input.setEnabled(False)

        elif self.comboBox.currentIndex() == 2:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(True)
            self.producto3_input.setEnabled(True)
            self.producto4_input.setEnabled(False)
            self.producto5_input.setEnabled(False)
            self.producto6_input.setEnabled(False)

        elif self.comboBox.currentIndex() == 3:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(True)
            self.producto3_input.setEnabled(True)
            self.producto4_input.setEnabled(True)
            self.producto5_input.setEnabled(False)
            self.producto6_input.setEnabled(False)
        
        elif self.comboBox.currentIndex() == 4:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(True)
            self.producto3_input.setEnabled(True)
            self.producto4_input.setEnabled(True)
            self.producto5_input.setEnabled(True)
            self.producto6_input.setEnabled(False)
        
        elif self.comboBox.currentIndex() == 5:
            self.producto1_input.setEnabled(True)
            self.producto2_input.setEnabled(True)
            self.producto3_input.setEnabled(True)
            self.producto4_input.setEnabled(True)
            self.producto5_input.setEnabled(True)
            self.producto6_input.setEnabled(True)


    def get_datos(self):
        codigo = self.codigoInput.text()
        nombre = self.nombreInput.text()
        precio = float(self.precioInput.text())
        if self.comboBox.currentIndex() == 0:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()
            
            return (codigo,nombre,precio),( producto1,cantidadProducto1)

        elif self.comboBox.currentIndex() == 1:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()

            producto2 = self.producto2_input.text()
            cantidadProducto2 = self.producto2_spinbox.value()
            
            return (codigo,nombre,precio), (producto1,cantidadProducto1), (producto2,cantidadProducto2)

        elif self.comboBox.currentIndex() == 2:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()

            producto2 = self.producto2_input.text()
            cantidadProducto2 = self.producto2_spinbox.value()

            producto3 = self.producto3_input.text()
            cantidadProducto3 = self.producto3_spinbox.value()
            
            return (codigo,nombre,precio), (producto1,cantidadProducto1), (producto2,cantidadProducto2), (producto3,cantidadProducto3)

        elif self.comboBox.currentIndex() == 3:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()

            producto2 = self.producto2_input.text()
            cantidadProducto2 = self.producto2_spinbox.value()

            producto3 = self.producto3_input.text()
            cantidadProducto3 = self.producto3_spinbox.value()

            producto4 = self.producto4_input.text()
            cantidadProducto4 = self.producto4_spinbox.value()
            
            return (codigo,nombre,precio), (producto1,cantidadProducto1), (producto2,cantidadProducto2), (producto3,cantidadProducto3), (producto4,cantidadProducto4)
        
        elif self.comboBox.currentIndex() == 4:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()

            producto2 = self.producto2_input.text()
            cantidadProducto2 = self.producto2_spinbox.value()

            producto3 = self.producto3_input.text()
            cantidadProducto3 = self.producto3_spinbox.value()

            producto4 = self.producto4_input.text()
            cantidadProducto4 = self.producto4_spinbox.value()

            producto5 = self.producto5_input.text()
            cantidadProducto5 = self.producto5_spinbox.value()
            
            return (codigo,nombre,precio), (producto1,cantidadProducto1), (producto2,cantidadProducto2), (producto3,cantidadProducto3), (producto4,cantidadProducto4), (producto5,cantidadProducto5)
        
        elif self.comboBox.currentIndex() == 5:
            producto1 = self.producto1_input.text()
            cantidadProducto1 = self.producto1_spinbox.value()

            producto2 = self.producto2_input.text()
            cantidadProducto2 = self.producto2_spinbox.value()

            producto3 = self.producto3_input.text()
            cantidadProducto3 = self.producto3_spinbox.value()

            producto4 = self.producto4_input.text()
            cantidadProducto4 = self.producto4_spinbox.value()

            producto5 = self.producto5_input.text()
            cantidadProducto5 = self.producto5_spinbox.value()

            producto6 = self.producto6_input.text()
            cantidadProducto6 = self.producto6_spinbox.value()
            
            return (codigo,nombre,precio), (producto1,cantidadProducto1), (producto2,cantidadProducto2), (producto3,cantidadProducto3), (producto4,cantidadProducto4), (producto5,cantidadProducto5),( producto6,cantidadProducto6)
    
    def validador_codigo(self,i):
        if i == 1:
            codigo = self.producto1_input.text()
        elif i == 2:
            codigo = self.producto2_input.text()
        elif i == 3:
            codigo = self.producto3_input.text()
        elif i ==4:
            codigo = self.producto4_input.text()
        elif i == 5:
            codigo = self.producto5_input.text()
        elif i == 6:
            codigo = self.producto6_input.text()
        else:
            codigo = ''
        if codigo =='':
            return

    
        for producto_existente in inventario.lista_inventario:
            if str(codigo) == str(producto_existente.codigo):
                return True
        mensaje('Error','No hay un producto/bebida con ese codigo')

    

class DialogEditarProducto(QDialog):
    def __init__(self,codigoActual,nombreActual,precioActual,cantidadActual):
        super().__init__()
        uic.loadUi('QdialogProducto.ui',self)
        self.CodigoInput.setText(codigoActual)
        self.NombreInput.setText(nombreActual)
        self.PrecioInput.setText(precioActual)
        self.CantidadInput.setText(cantidadActual)

    def get_datos(self):
        codigo = self.CodigoInput.text()
        Nombre = self.NombreInput.text()
        Precio = self.PrecioInput.text()
        Cantidad = self.CantidadInput.text()
        return codigo,Nombre,Precio,Cantidad

class DialogAperturaCaja(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('aperturaCaja.ui',self)
        turno = inventario.lista_cajas[-1].turno
        turno +=1
        self.TurnoLabel.setText(str(turno))

    def get_datos(self):
        turno = self.TurnoLabel.text()
        cajero = self.CajeroInput.text()
        return turno,cajero

class VentanaEditarPromo(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('EditarPromos.ui',self)
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()
        
        self.boton_actualizar.clicked.connect(self.actualizar_precio)

    def cargar_comboBox(self):
        self.comboBox.clear()
        self.cursor.execute("SELECT * FROM Promos")
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            texto = str(resultado[1]) +":"+str(resultado[2])
            self.comboBox.addItem(texto)
    
    def actualizar_precio(self):
        texto = self.comboBox.currentText()
        texto_partido = texto.split(':')
        codigo = texto_partido[1]
        print(codigo)
    def borrar_promo(self):
        pass

class VentanaCierre(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('cierre_caja.ui',self)
        validador = QtGui.QIntValidator(0, 10000000)
        self.dosmil.setValidator(validador)
        self.mil.setValidator(validador)
        self.quinientos.setValidator(validador)
        self.doscientos.setValidator(validador)
        self.cien.setValidator(validador)

        self.tarjetaInput.setValidator(validador)
        self.tranferenciasInput.setValidator(validador)
        self.retiroInput.setValidator(validador)
        self.egresosInput.setValidator(validador)

        self.dosmil.editingFinished.connect(self.efectivo)
        self.mil.editingFinished.connect(self.efectivo)
        self.quinientos.editingFinished.connect(self.efectivo)
        self.doscientos.editingFinished.connect(self.efectivo)
        self.cien.editingFinished.connect(self.efectivo)
        self.botonFinalizar.clicked.connect(self.finalizar)

    def efectivo(self):
        dossmil=int(self.dosmil.text())
        mill=int(self.mil.text())
        quinien=int(self.quinientos.text())
        doscie=int(self.doscientos.text())
        cienpe=int(self.cien.text())
        total1=str(dossmil*2000+mill*1000+quinien*500+doscie*200+cienpe*100)
        self.efectivoRendidoLabel.setText(total1)
    
    def finalizar(self):
        total = float(self.ingresosInput.text())
        turno = inventario.lista_cajas[-1].turno
        cajero = inventario.lista_cajas[-1].vendedor
        tarjetas = int(self.tarjetaInput.text())
        transferencias = int(self.tranferenciasInput.text())
        retiros = int(self.retiroInput.text())
        egresos = int(self.egresosInput.text())
        efectivoARendir = total - tarjetas - transferencias -egresos- retiros
        efectivoRendido = int(self.efectivoRendidoLabel.text()) 
        sobrante = efectivoRendido - efectivoARendir
        inventario.lista_cajas[-1].sobranteFaltante = sobrante 

        archivo = open('Reportes.csv', 'a', newline='')
        escritor_csv = csv.writer(archivo, delimiter=',', quotechar='"')

        # Escribir los datos
        escritor_csv.writerow([turno, cajero, total,tarjetas, transferencias, retiros,egresos, efectivoARendir, efectivoRendido,sobrante])
        # Cerrar archivo
        archivo.close()

        inventario.lista_cajas[-1].Actualizar_Caja()
        titulo = 'Cierre'
        cuerpo = 'Caja guardada correctamente'
        mensaje(titulo,cuerpo)
        
        self.close()


class VentanaReportVentas(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('reportVentas.ui',self)
        self.conn = sqlite3.connect('bottiglia.db')
        self.cursor = self.conn.cursor()
    
        self.botonCargar.clicked.connect(self.cargar_ventas)
        
    def cargar_comboBox(self):
        self.comboBox.clear()
        self.cursor.execute("SELECT * FROM Caja")
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            texto = "Turno :" + str(resultado[1]) +" "+"Cajero: " + str(resultado[2])
            self.comboBox.addItem(texto)
    def cargar_ventas(self):
        #Limpiamos la tabla en caso de que ya se haya hecho una consulta previamente
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        indice = self.comboBox.currentIndex()
        indice +=1
        self.cursor.execute("SELECT * FROM Ventas WHERE turno_id = ?", (indice,))
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            fila = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(fila + 1)
            self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(resultado[1])))
            self.tableWidget.setItem(fila, 1, QTableWidgetItem(str(resultado[2])))
            self.tableWidget.setItem(fila, 2, QTableWidgetItem(str(resultado[3])))
            self.tableWidget.setItem(fila, 3, QTableWidgetItem(str(resultado[4])))
            self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(resultado[5])))

def mensaje(titulo,cuerpo):
    mensaje = QMessageBox()

    mensaje.setWindowTitle(titulo)
    mensaje.setText(cuerpo)


    mensaje.setIcon(QMessageBox.Icon.NoIcon)
    mensaje.setStandardButtons(QMessageBox.StandardButton.Ok)
    resultado = mensaje.exec()
app = QApplication([])

ventana = Mi_Ventana()
with open('stylesheet.qss','r') as file:
    ventana.setStyleSheet(file.read())
    ventana.ventanaBusqueda.setStyleSheet(file.read())
ventana.show()

app.exec()