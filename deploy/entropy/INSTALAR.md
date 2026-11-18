# Kamala 1.7.0 — portada y aplicaciones de azar

Timestamp: 2026-10-29 | Version: 1.7.0
Author and Credits: https://www.alawise.es/1-s

Restaura la portada anterior: imagen completa del observatorio, Sol, meteo,
alineación planetaria y atlas. Se elimina únicamente el acceso externo a
`go.1-s.es` del menú; el visor original sigue en portada. Conserva las cuatro
pantallas de cámara y añade **Chance apps** al menú superior e inferior.

## Subir la actualización

Descomprime el ZIP y copia **el contenido de `html/`** sobre
`/var/www/kamala.pro/html/`, conservando las rutas. No borres el contenido
anterior. El ZIP incluye las páginas estáticas y `api/entropy.php`.
No contiene `bior/`, `contact/`, `app.js` ni la configuración privada del correo.

Desde la carpeta descomprimida, actualiza únicamente el menú del contacto:

```sh
sudo python3 tools/update_contact_nav.py
```

El script conserva el formulario y sus scripts, y guarda una copia del HTML
original fuera del directorio público, en `/var/backups/kamala/`.
No subas `tools/` al directorio público. Si el menú del contacto está personalizado,
puedes añadir manualmente `/stream/` y `/apps/`.

## Aplicaciones

- `/apps/entropy/`: bytes hexadecimales.
- `/apps/dice/`: dados de seis caras, de uno a doce.
- `/apps/coins/`: monedas, de una a doce.
- `/apps/cards/`: baraja de 52 cartas, sin reposición.
- `/apps/runes/`: 24 símbolos del Futhark antiguo, sin reposición.

La selección automática toma una cámara distinta al azar en cada petición;
no abre las cuatro a la vez ni garantiza alternancia. También se puede seleccionar
una cámara concreta o usar solo el navegador. Cartas y runas se reinician
con el botón de reset o al abandonar la página.

## Comprobar el muestreo en Excalibur

El PHP usa únicamente las cuatro URLs de `https://kam.2to1.me/stream/camN`.
No necesita claves ni configurar correo. Requiere PHP 8.2+ con cURL y acceso
HTTPS saliente desde PHP-FPM. El Nginx ya preparado ejecuta los archivos `.php`
existentes; no se añade una nueva ruta proxy.

Comprueba la extensión:

```sh
php -r 'echo extension_loaded("curl") ? "curl OK\n" : "curl missing\n";'
```

Si falta, localiza el paquete de Fedora que proporciona la extensión y
instálalo con DNF; reinicia `php-fpm` después:

```sh
dnf provides '*/curl.so'
sudo systemctl restart php-fpm
```

Prueba una única petición (no se necesita enviar mensajes ni datos personales):

```sh
curl --fail 'https://kamala.pro/api/entropy.php?src=cam4'
```

Una respuesta con `mode: "stream+system"`, `source: "cam4"` y
`sample_bytes` mayor que cero confirma una muestra de esa cámara.
`system-only` indica que el PHP funciona, pero no obtuvo imagen: comprueba
la extensión cURL, la conexión HTTPS y los permisos de red de PHP-FPM/SELinux.
No desactives SELinux ni la verificación TLS.

La captura dura como máximo dos segundos y guarda como máximo 128 KiB;
solo una captura global puede estar activa y hay un segundo de espera entre
inicios. Una petición durante otra puede responder 429 o 503: el navegador usa
su generador local y lo indica. El archivo de bloqueo se crea en el directorio
temporal de PHP, que debe ser escribible por el pool. No se guardan imágenes,
resultados ni datos del visitante.

En el visor estático privado de Sites no se ejecuta PHP: las aplicaciones
funcionan con el modo local explícitamente indicado. La captura real debe
comprobarse en Excalibur después de subir los archivos.

## Qué significa el resultado

El servidor mezcla la muestra JPEG con 64 bytes nuevos del sistema y aplica
SHA-512. El navegador mezcla una semilla propia con esa respuesta y utiliza
palabras aleatorias nuevas en cada elección. El muestreo por rechazo evita
el sesgo de aplicar un módulo directamente.

Las cámaras pueden tener retraso o repetir imágenes. Todavía no se ha medido
su tasa de entropía física ni se atribuye valor predictivo a los resultados.
La interfaz siempre indica qué fuentes pudo usar.

Referencias técnicas: [PHP cURL](https://www.php.net/manual/en/curl.constants.php),
[PHP random_bytes](https://www.php.net/manual/en/function.random-bytes.php),
[Web Crypto getRandomValues](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues).
