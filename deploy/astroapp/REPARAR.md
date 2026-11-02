# Reparar la carga de AstroApp · 2.0.2

Timestamp: 2026-10-30 | Version: 2.0.2
Author and Credits: https://www.alawise.es/1-s

Descomprimir el paquete pequeño fuera de la carpeta pública. Desde su carpeta:

```bash
sudo python3 repair_astroapp_loading.py
```

El destino es /var/www/kamala.pro/html. Para otra instalación:

```bash
sudo python3 repair_astroapp_loading.py --root /ruta/del/sitio/html
```

Se guardan copias en /var/backups/kamala/astroapp-2.0.2-FECHA/. La reparación
retira el SDK y su cargador de las páginas sin formulario de cartas. Mantiene
una sola etiqueta en el head de /astrology/, leyendo la clave existente.
Actualiza astroapp-head.js y astroapp.js. Conserva el contenido, biorritmos,
correo y astroapp-config.json. No envía formularios ni correos.

Abrir https://kamala.pro/ sin www y recargar una vez con Ctrl+Shift+R.
La reparación de los archivos no requiere reiniciar Nginx ni PHP-FPM.

## Origen comprobado

Con la clave que publica actualmente el sitio, AstroApp devolvió el SDK para
Referer https://kamala.pro/. Devolvió Invalid AstroApp Key para
https://www.kamala.pro/ y para el Referer completo de /astrology/.
El código usa referrerpolicy=origin, que mantiene el origen sin la ruta.
El alias www no redirige actualmente al dominio sin www.

Para redirigirlo desde el servidor, añadir dentro del bloque server HTTPS
existente que atiende a www.kamala.pro, conservando sus certificados:

```nginx
if ($host = www.kamala.pro) {
    return 308 https://kamala.pro$request_uri;
}
```

Validar y recargar después de esa modificación opcional de Nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

El paquete no cambia automáticamente la configuración TLS o Nginx.
El SDK y sus métodos se han comprobado; una petición sintética de cálculo
respondió HTTP 500, por lo que no se afirma haber validado una carta completa.
