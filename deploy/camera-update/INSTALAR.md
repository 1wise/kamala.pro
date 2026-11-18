# Kamala — pantallas de cámara 1.6.0

Timestamp: 2026-10-29  
Version: 1.6.0  
Author and Credits: https://www.alawise.es/1-s

Actualización acumulativa para la instalación existente en Excalibur. Retira el acceso Status y el marco de go.1-s.es. La portada muestra cuatro accesos de cámara, seguidos por los visores del Sol, meteo y alineación planetaria y el atlas cultural.

| Página de Kamala | Señal utilizada |
| --- | --- |
| `/stream/cam1/` | `https://kam.2to1.me/stream/cam1` |
| `/stream/cam2/` | `https://kam.2to1.me/stream/cam2` |
| `/stream/cam3/` | `https://kam.2to1.me/stream/cam3` |
| `/stream/cam4/` | `https://kam.2to1.me/stream/cam4` — microscopio |

Cada página abre una sola señal MJPEG y ofrece cambio de cámara, detener/reanudar y pantalla completa. Si el navegador impide la pantalla completa nativa, el botón amplía el visor a la ventana; Escape permite volver. Los cuatro accesos de portada no cargan las señales. El retardo y la disponibilidad dependen del servicio de origen.

## Subir los archivos

1. Descomprimir el ZIP en una carpeta de trabajo.
2. Copiar **el contenido de `html/`** a `/var/www/kamala.pro/html/`, manteniendo las rutas y reemplazando los archivos coincidentes.
3. Conservar todos los demás archivos del servidor. No usar una sincronización que borre el destino.

No se incluyen `app.js`, `contact/index.html`, las aplicaciones de `bior/` ni la configuración de correo. Se mantienen el Send instalado y los ajustes propios del formulario. Las señales siguen en kam.2to1.me: no hace falta cambiar Nginx, DNS ni los servicios de cámara.

## Cambiar solo el menú de contacto

Como contacto conserva su archivo actual, ejecutar desde la carpeta descomprimida:

```bash
sudo python3 tools/update_contact_nav.py /var/www/kamala.pro/html/contact/index.html
```

El script sustituye únicamente el antiguo enlace Status por Cameras. Guarda antes una copia completa del archivo en `/var/backups/kamala/`, fuera de la web. No modifica el formulario, sus scripts o su envío de correo. Si el enlace ya fue cambiado, no escribe nada; si encuentra un enlace personalizado que no coincide, lo comunica y deja el archivo intacto.

No subir `tools/` dentro de la raíz pública. No ejecutar el script contra otros sitios.

## Comprobación

Recargar sin caché y abrir `/stream/`. Entrar en cada cámara, comprobar detener/reanudar y cambiar de cámara. El microscopio corresponde a la cuarta. Las imágenes se muestran completas con bandas negras cuando la pantalla y el vídeo tienen distintas proporciones.

Si una señal no está disponible aparece Reconnect; el enlace Source abre directamente el origen. El portal original kam.2to1.me y go.1-s.es no se modifican con este paquete. El sitio pasa a 66 páginas y conserva las 26 técnicas y el atlas de 13 entradas.
