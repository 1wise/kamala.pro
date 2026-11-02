# kamala.pro — Artes Mánticos · versión 2.1.1

Timestamp: 2026-11-02 | Version: 2.1.1
Author and Credits: https://www.alawise.es/1-s

## Aplicar en Excalibur

Descomprimir el ZIP fuera de la carpeta pública y ejecutar desde esa carpeta:

    sudo python3 tools/install_v2.py

El destino predeterminado es /var/www/kamala.pro/html. Para otra instalación:

    sudo python3 tools/install_v2.py --root /ruta/del/sitio/html

El instalador conserva las aplicaciones de /bior/, app.js, el contenido del
formulario instalado, contact/send.php, astroapp-config.json y la configuración
privada de correo. Actualiza la envoltura de contacto para compartir navegación,
estilos y metadatos. Guarda los archivos sustituidos bajo
/var/backups/kamala/v2-FECHA/. El ZIP también permite copiar html/ manualmente;
en ese caso ejecutar después tools/update_contact_page.py y
tools/configure_head.py.

## AstroApp: etiqueta literal dentro de head

El instalador lee el api_key ya configurado en Excalibur y escribe la etiqueta
documentada con https://astroapp.com/astro/astroapi?key=... en el head del
espacio de cartas de /astrology/. Retira las cargas globales anteriores de
la portada y de las demás páginas. La clave también viaja en la petición
del SDK. No se incluye ninguna clave real en este paquete.

El formulario distingue natal occidental, Jyotisha Rāśi / D1 y divisiones.
Cada método tiene sus opciones y diagrama. El SDK actual omite el número
al serializar una división; la aplicación bloquea esa petición incompleta.
Las peticiones natal occidental y Rāśi, con fechas YYYY/MM/DD, devolvieron
HTTP 200, imagen y XML en la comprobación remota. El menú separa culturas
y conserva el glosario completo. Véase ASTROAPP.md para el contrato y límites.

Tras cambiar la clave en el futuro:

    sudo python3 tools/configure_head.py /var/www/kamala.pro/html

Solo imprime el número de páginas configuradas. Nunca imprime la clave.
La prueba del 30 de octubre de 2026 devolvía el SDK para el origen
https://kamala.pro/ y rechazaba https://www.kamala.pro/. La clave activa se
ha cambiado al host www.kamala.pro; configurar en Nginx la redirección del
dominio sin www hacia www antes de servir el espacio de cartas.
El laboratorio de claves y Potpourri mantienen sus documentos sin el SDK
de terceros. El cargador local permite configurar un host después de instalar
los HTML; la etiqueta literal generada es la vía principal de Excalibur.

## Potpourri: envío privado por correo

html/potpourri/send.php utiliza el mismo contact_to y transporte de
/var/www/kamala.pro/private/send/config.php. El instalador actualiza
private/send/send.php conservando esa configuración. Se necesitan las
dependencias de correo existentes y PHP con GD y fileinfo.

Hasta 3 fotos JPEG/PNG/WebP, 5 MiB por foto, 12 MiB total y 25 megapíxeles.
El servidor verifica la imagen y la vuelve a codificar como JPEG para retirar
metadatos. Envía adjuntos al destinatario configurado y elimina los archivos
temporales en todos los caminos de salida. La correspondencia y sus adjuntos
siguen en el buzón para contestar; no se ofrece una galería pública.
No se envía ningún correo durante la instalación.

Añadir o comprobar en el bloque server HTTPS de Nginx:

    client_max_body_size 16m;

Comprobar en el pool PHP-FPM de Kamala:

    php_admin_value[upload_max_filesize] = 5M
    php_admin_value[post_max_size] = 16M
    php_admin_value[max_file_uploads] = 3
    php_admin_value[memory_limit] = 256M

Si falta GD en Fedora: sudo dnf install php-gd. Después de adaptar los límites:
sudo nginx -t y sudo systemctl reload nginx php-fpm. Las plantillas completas de
fedora44/ sirven como referencia; conservar el TLS y las rutas particulares
de la instalación.

La publicación estática de Sites muestra el formulario y sus instrucciones.
El envío funciona en Excalibur, que ejecuta PHP y tiene el correo configurado.

## Contenido y aplicaciones

- Dados marfil con puntos índigo y borde biselado. Los valores aparecen como
  puntos, sin cifras en las caras ni en el historial.
- AstroApp: la respuesta de cálculo y la carga de imagen tienen estados
  separados. Los fallos transitorios de imagen tienen dos reintentos
  automáticos, botón Retry chart image y enlace directo. La recarga de imagen
  conserva el cálculo y no reenvía los datos.
- Archivo package-lock.json corregido: get-caller-file conserva su versión
  publicada 2.0.5. La versión del proyecto solo se cambia en las entradas raíz.

- Las 46 familias propuestas tienen páginas propias, contexto, fuentes,
  definiciones, método de registro y guía de fotos.
- Glosario completo, búsqueda sin distinguir tildes, equivalentes en castellano,
  filtro por escala y referencias entre familias.
- Moneda con retrato centrado en relieve de bronce y reverso de cruz maltesa con el mismo relieve, borde y acabado de bronce.
- Tarot de Marsella: 78 imágenes propias, galería completa en
  /apps/cards/tarot/ y ampliación desde las tiradas. Incluye 22 arcanos mayores,
  16 figuras y 40 cartas numerales con cantidades exactas de palos.
- Baraja española completa de 48 cartas, con opción de 40 en la aplicación,
  y naipes americanos de 52: figuras propias, cartas numerales e índices.
  Las tres galerías están reunidas en /apps/cards/decks/.
- Vela y bola de cristal en /apps/candle/ y /apps/crystal/, con acceso desde
  /contemplation/ y las técnicas correspondientes. El modo Demo está rotulado.
  El modo Live requiere el captador del apartado siguiente.
- Biorritmos: generador y compositor juntos, conservando sus programas PHP.
- Todas las técnicas enlazan con Potpourri y su guía.
- Chance comparte el muestreador de cámaras y navegador con el laboratorio.
  El modo alternativo muestra explícitamente las fuentes utilizadas.
- GET: api_act=configure rellena opciones; api_act=draw ejecuta una tirada
  de Chance o el experimento de bytes. Pares SSH, secretos, hexadecimal y otras
  codificaciones, UUID, TOTP, QR y arte ASCII siguen disponibles en el laboratorio.
  Su generación requiere botón.
  /api/ conserva la nomenclatura y ejemplos de cada opción.
- Metadatos y menús se generan en el HTML de todas las rutas.

## Comprobaciones de esta entrega

La versión 2.1.1 comprueba las 133 páginas públicas, sus enlaces y metadatos,
el mapa de las 178 imágenes de cartas, las cantidades de palos, las galerías y las posiciones
de las tiradas. También conserva el contrato de los cuatro generadores y los
hashes CSP del HTML portátil. La validación criptográfica detallada de SSH,
codificaciones, TOTP y QR corresponde a la entrega 2.0.5.

El empaquetador verifica la integridad de los ZIP y crea sumas SHA-256.
La vista previa HTTP permite revisar la composición, pero bloquea las acciones
criptográficas; para ejecutarlas se necesita HTTPS o el archivo HTML local.
La instalación real, el correo y AstroApp dependen de la configuración de
Excalibur.

## Activar la vela y la bola con tráfico real

Desde la carpeta descomprimida de esta entrega, el componente contemplation/
contiene el captador y su documentación. Tras instalar las páginas:

    python3 contemplation/install.py --root /var/www/kamala.pro/html --dry-run
    sudo python3 contemplation/install.py --root /var/www/kamala.pro/html --install
    sudo systemctl enable --now kamala-contemplation.service

Comprobar:

    curl -fsS https://www.kamala.pro/telemetry/contemplation.json

El captador usa enp6s0 y los avisos nuevos del kernel asociados a esa interfaz.
Publica cantidades agregadas, sin direcciones, puertos ni mensajes completos.
La instalación no cambia reglas ni activa registros de firewall. El apartado
Firewall activity de contemplation/README.md explica la configuración opcional
de avisos y los límites del recuento. El servicio se ejecuta como kamala-flow.
Si ya estaba instalado, reiniciarlo tras actualizar sus archivos:

    sudo systemctl restart kamala-contemplation.service

Sites publica la interfaz y la demostración; el captador se activa en Excalibur.
