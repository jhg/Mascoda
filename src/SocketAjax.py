#-*- coding: UTF-8 -*-
"""Cliente Ajax para conectar Mascoda usando un servidor HTTP o HTTPS.
    Esta es una alternativa para montar una infrastructura de red Mascoda
    sin necesidad de instalar un servidor Mascoda sino usando un servidor HTTP
    o HTTPS y sirviendo los datos como se haria para el uso de Ajax."""


import urllib
import urllib2
import cookielib


class SocketAjax(object):
    """ Clase para la comunicación con un servidor HTTP como si fuera Ajax """
    def __init__(self, url, usuario='', clave='', cabeceras={}):
        if url[:4] != u'http':
            self._url = 'http://' + url
        else:
            self._url = url
        self.usuario = unicode(usuario)
        self.clave = unicode(clave)
        self._cabeceras = cabeceras
        self.recibido = u''
        self.actividad = False
        self.error = False
        # Identificación de navegador web de Mascoda para paginas HTTP
        self._cabeceras["User-Agent"] = "Mascoda/0.0.0"
        # Usamos un manejador de urllib2 para trabajar con cookies
        self.cookies = cookielib.CookieJar()
        _cookies = urllib2.HTTPCookieProcessor(self.cookies)
        _manejador_cookies = urllib2.build_opener(_cookies)
        urllib2.install_opener(_manejador_cookies)
    def enviar(self, get={}, post={}):
        """ Envia una petición con las variables de los diccionarios pasados """
        self.actividad = False
        self.error = False
        if self.usuario != '' and self.clave != '':
            post[self.usuario] = self.clave
            get[self.usuario] = self.clave
        # Preparamos los datos a enviar
        if len(get) > 0:
            _cadena_get = u'?' + urllib.urlencode(get)
        else:
            _cadena_get = ''
        if len(post) > 0:
            _cadena_post = urllib.urlencode(post)
        else:
            _cadena_post = ''
        # Conectamos
        try:
            _peticion = urllib2.Request(self._url+_cadena_get,
                # ¡NOTA!: Al enviar datos por POST urllib2 da error
                #data=_cadena_post,
                headers=self._cabeceras)
            _conexion = urllib2.urlopen(_peticion)
            _respuesta = _conexion.read()
            if _respuesta != self.recibido and _respuesta != u'':
                self.recibido = _respuesta
                self.actividad = True
            _conexion.close()
        except:
            self.error = True
        


