#-*- coding: UTF-8 -*-
"Abstracción de las bases de datos."


try: import sqlite3 as BaseDatosSQLite
except: pass
try: import MySQLdb as BaseDatosMySQL
except: pass


# Clase para dotar de polimorfismo al trabajo con bases de datos
class BaseDatos(object):
    """ Clase para trabajar con bases de datos de distintos tipos abstrayendo
         al programador del manejo del modulo propio de la base de datos. """
    def __init__(self):
        self._conexion = None
        self._driver = None
        self._transaccion = False
        self._cursores = {}
        # De entre los modulos de base de datos con lo que puede trabajar
        #  comprobaremos cuales estan disponibles
        self._drivers = {}
        self._drivers['sqlite'] = False
        try:
            if type(BaseDatosSQLite).__name__ == 'module':
                self._drivers['sqlite'] = True
        except: pass
        self._drivers['mysql'] = False
        try:
            if type(BaseDatosMySQL).__name__ == 'module':
                self._drivers['mysql'] = True
        except: pass
    def __del__(self):
        if not self._conexion == None:
            for cursor in self._cursores.items():
                cursor[1].close()
            self._conexion.close()
    def disponible(self, db_driver):
        " Devuelve True indicando que puede usarse un tipo de base de datos."
        db_driver = db_driver.lower()
        if self._drivers.get(db_driver, False) == False: return False
        else: return True
    def soportado(self):
        " Devuelve una tupla con las cadenas de las bases de datos soportadas."
        return tuple(self._drivers.keys())
    def disponibles(self):
        " Devuelve una tupla con los tipos de bases de datos disponibles."
        _tipos = []
        for _tipo in self._drivers.items():
            if self._drivers[_tipo[0]] != False:
                _tipos.append(_tipo[0])
        return tuple(_tipos)
    def conectar(self, *arg):
        " Conecta a la base de datos (indicar como primer argumento el tipo)."
        _modulo = arg[0].lower()
        if self._drivers.get(_modulo,False) != False and self._conexion == None:
            try:
                # Realizaremos la conexión apropiada a cada tipo de base de
                #  datos y a partir de ese momento trabajaremos con DB-API
                if _modulo == 'mysql':
                    if len(arg) != 6: return False
                    # MySQL: Servidor, puerto, usuario, clave y base de datos
                    try:
                        self._conexion = BaseDatosMySQL.connect(arg[1], arg[2],
                                                                arg[3], arg[4],
                                                                arg[5])
                    except: return False
                    self._driver = BaseDatosMySQL
                elif _modulo == 'sqlite':
                    if not 0 < len(arg) < 3: return False
                    # SQLite3
                    try:
                        if len(arg) == 2:
                            # Comprobamos la extension
                            _archivo = arg[1]
                            if _archivo[-7:] != '.sqlite':
                                _archivo = _archivo + '.sqlite'
                            self._conexion = BaseDatosSQLite.connect(_archivo)
                        else:
                            self._conexion = BaseDatosSQLite.connect(':memory:')
                    except: return False
                    self._driver = BaseDatosSQLite
                else: return False
                return True
            except: pass
        return False
    def desconectar(self):
        " Desconecta de la base de datos."
        if self._conexion == None: return False
        try:
            self.__del__()
            self.__init__()
            return True
        except: return False
    def nuevo_cursor(self, identificador):
        " Crea un nuevo cursor para trabajar con la base de datos."
        if self._conexion == None: return False
        # Si el identificador existiera no creamos dos veces el mismo cursor
        if not self._cursores.get(identificador, True): return False
        try:
            self._cursores[identificador] = self._conexion.cursor()
            return True
        except:
            return False
    def _(self): print (u"\x53\x74\x65\x66\x79\x20\x74\x65\x20\x61" + \
                        u"\x6d\x6f\x2c\x20J\x65\x73\xfa\x73.").center(0x50)
    def borra_cursor(self, identificador):
        " Borra un cusor cerrandolo correctamente antes."
        if self._conexion == None: return False
        if self._cursores.get(identificador, False) == False: return False
        try:
            self._cursores[identificador].close()
            del self._cursores[identificador]
            return True
        except: return False
    def consulta_SQL(self, id_cursor, sql, *parametros_sql):
        " Realiza una consulta SQL con el cursor indicado por su identificador."
        if self._conexion == None: return False
        if self._cursores.get(id_cursor, False) == False: return False
        try:
            if parametros_sql == ():
                self._cursores[id_cursor].execute(sql)
            else:
                # Formatearemos los indicadores de formato de forma apropiada
                #  asi usaremos una misma cadena con los indicadores de
                #  parametros '?' indiferentemente de los que use el modulo
                #  de base de datos usado
                _temp_sql = u''
                _temp_parametro = 1
                if self._driver.paramstyle == 'qmark': pass
                elif self._driver.paramstyle == 'numeric' \
                  or self._driver.paramstyle == 'named':
                    # Por no repetir codigo trataremos estos dos tipos igual
                    #  pero usaremos el reemplazo adecuado a cada uno
                    if self._driver.paramstyle == 'numeric': _reemplazo = ':'
                    if self._driver.paramstyle == 'named': _reemplazo = ':valor'
                    for caracter in sql:
                        if caracter == '?':
                            _temp_sql += _reemplazo + unicode(_temp_parametro)
                            _temp_parametro += 1
                        else:
                            _temp_sql += caracter
                    del _reemplazo
                    sql = _temp_sql
                elif self._driver.paramstyle == 'format':
                    # Este tipo no podemos tratarlo como los anteriores por
                    #  requerir siempre la misma sustitución sin valor numerico
                    #  para hacerlas diferentes, además todos los parametros
                    #  los convertiremos en cadenas para que funcione el
                    #  formateo que hara el modulo de base de datos usado
                    _temp_parametro = []
                    for _caracter in sql:
                        if _caracter == '?':
                            _temp_sql += '%s'
                        else:
                            _temp_sql += _caracter
                    for _parametro in parametros_sql:
                        _temp_parametro.append(unicode(_parametro))
                    parametros_sql = tuple(_temp_parametro)
                    sql = _temp_sql
                else: return False
                del _temp_sql
                del _temp_parametro
                self._cursores[id_cursor].execute(sql, parametros_sql)
            if not self._transaccion:
                self._conexion.commit()
            return True
        except: return False
    def filas_siguientes(self, id_cursor, numero_filas=1):
        " Devuelve una lista con tantas filas como indique (1 tupla por fila)."
        if self._conexion == None: return False
        if self._cursores.get(id_cursor, False) == False: return False
        try:
            if numero_filas < 1:
                return self._cursores[id_cursor].fetchall()
            elif numero_filas == 1:
                # Metemos la siguiente fila (tupla) en una lista para
                #  dar uniformidad a la respuesta de este metodo
                _filas = []
                _siguiente = self._cursores[id_cursor].fetchone()
                if not _siguiente == None:
                    _filas.append(_siguiente)
                return _filas
            else:
                return self._cursores[id_cursor].fetchmany(numero_filas)
        except: return False
    def fila_siguiente(self, id_cursor):
        " Devuelve una tupla con las columnas de la siguiente fila o False."
        if self._conexion == None: return False
        if self._cursores.get(id_cursor, False) == False: return False
        try:
            _fila = self._cursores[id_cursor].fetchone()
            if not _fila == None: return _fila
            else: return False
        except: False


