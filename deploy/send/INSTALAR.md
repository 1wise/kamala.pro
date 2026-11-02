# Send para Kamala / Fedora 44

Timestamp: 2026-10-28  
Version: 1.0.0  
Author and Credits: https://www.alawise.es/1-s

Servicio PHP compartido para el contacto y los biorritmos. Se instala en Excalibur; este paquete no cambia el servidor automáticamente. Requiere PHP 8.2 o posterior. La portada y los cálculos no cambian.

## Qué configurar

El original `bior/sense_mail.php` ya usa PHPMailer con SMTP autenticado: `ssl0.ovh.net`, puerto 465, TLS implícito, usuario/remitente `kamala@1wise.es`. No usa la función PHP `mail()`. El paquete no copia las contraseñas del código antiguo.

La nueva configuración estará en **`/var/www/kamala.pro/private/send/config.php`**, fuera de la raíz pública `/var/www/kamala.pro/html`:

| Campo | Valor / finalidad |
| --- | --- |
| `transport` | `smtp` por defecto; `sendmail` solo si Postfix local ya funciona |
| `smtp_host` | `ssl0.ovh.net` para la cuenta OVH europea actual |
| `smtp_port` | `465` |
| `smtp_tls` | `ssl` para TLS implícito; `tls` para STARTTLS si el proveedor lo requiere |
| `smtp_user` | `kamala@1wise.es` |
| `smtp_pass` | Introducir directamente en Excalibur la contraseña vigente del buzón |
| `from_addr` | Remitente autorizado por la cuenta SMTP |
| `contact_to` | Dirección que recibirá el formulario; pendiente de elegir |
| `bior_bcc` | Conserva `henri@sirkia.es`; dejar vacío si ya no se quiere copia |
| `per_ip_hour` | 5 intentos por cliente y hora, compartidos entre aplicaciones |
| `total_hour` | 100 intentos totales por hora |

Los destinatarios de biorritmos siguen saliendo de las llamadas originales, hasta cinco direcciones separadas por comas. Contacto tiene un destinatario fijo en el servidor. El visitante queda en Reply-To, nunca en From. No hay un endpoint público genérico que acepte adjuntos o destinatarios de contacto arbitrarios.

## Instalación

Descomprimir este paquete y ejecutar desde su carpeta. Guardar antes una copia de `html/app.js`, `html/contact/index.html` y `html/bior/sense_mail.php` fuera de `html/` para volver atrás. No sustituir los originales `bior.php`, `compose.php` ni sus imágenes.

```bash
sudo dnf install php-cli php-fpm php-mbstring composer
sudo install -d -o root -g nginx -m 0750 /var/www/kamala.pro/private
sudo install -d -o root -g nginx -m 0750 /var/www/kamala.pro/private/send
sudo install -o root -g nginx -m 0640 private/send.php private/check.php private/composer.json /var/www/kamala.pro/private/send/
```

Primera instalación solamente: copiar la plantilla sin sobrescribir una configuración que ya exista.

```bash
sudo install -o root -g nginx -m 0640 private/config.example.php /var/www/kamala.pro/private/send/config.php
sudoedit /var/www/kamala.pro/private/send/config.php
```

Rellenar `smtp_pass` y `contact_to`. No publicar este archivo ni subirlo con la contraseña a Drive/Git. Si cambias la raíz del vhost, adapta también el `require_once` absoluto de los dos adaptadores públicos.

Instalar PHPMailer actualizado en la carpeta privada con Composer. Ejecutarlo como administrador de despliegue; no es necesario conceder escritura a PHP-FPM sobre código o configuración. Si trabajas como root, Composer solicitará confirmación. Conservar el `composer.lock` generado para futuras instalaciones reproducibles.

```bash
cd /var/www/kamala.pro/private/send
sudo composer update --no-dev --prefer-dist --optimize-autoloader
sudo composer audit --no-dev
sudo chown -R root:nginx /var/www/kamala.pro/private/send
sudo find /var/www/kamala.pro/private/send -type d -exec chmod 0750 {} +
sudo find /var/www/kamala.pro/private/send -type f -exec chmod 0640 {} +
```

Volver a la carpeta descomprimida. Crear el estado privado escribible y copiar los adaptadores:

```bash
sudo install -d -o nginx -g nginx -m 0700 /var/lib/php/kamala/send
sudo touch /var/lib/php/kamala/send/rate.json
sudo chown nginx:nginx /var/lib/php/kamala/send/rate.json
sudo chmod 0600 /var/lib/php/kamala/send/rate.json
sudo install -o root -g root -m 0644 public/app.js /var/www/kamala.pro/html/app.js
sudo install -o root -g root -m 0644 public/contact/index.html public/contact/send.php /var/www/kamala.pro/html/contact/
sudo install -o root -g root -m 0644 public/bior/sense_mail.php /var/www/kamala.pro/html/bior/sense_mail.php
sudo restorecon -RFv /var/www/kamala.pro
```

El estado y las sesiones necesitan el contexto SELinux escribible que ya usamos para Kamala:

```bash
sudo semanage fcontext -l -C
```

Si **no existe** la regla `/var/lib/php/kamala(/.*)?`, añadirla:

```bash
sudo semanage fcontext -a -t httpd_sys_rw_content_t '/var/lib/php/kamala(/.*)?'
```

Si ya existe con otro tipo, corregirla con `-m`. Después:

```bash
sudo restorecon -RFv /var/lib/php/kamala
sudo setsebool -P httpd_can_sendmail on
sudo php-fpm -t
sudo nginx -t
sudo systemctl reload php-fpm nginx
sudo -u nginx php /var/www/kamala.pro/private/send/check.php
```

El nombre `httpd_can_sendmail` pertenece a SELinux; no instala Apache. Permite el transporte de correo desde procesos web confinados. Si hay una denegación, revisar `sudo ausearch -m AVC -ts recent` antes de ampliar permisos. No desactivar SELinux ni la verificación TLS.

## Comprobación

El preflight no envía mensajes ni verifica la contraseña contra OVH. Revisa configuración, dependencia y escritura del contador. Una comprobación CLI tampoco prueba el contexto SELinux de PHP-FPM.

1. Abrir `https://kamala.pro/contact/`, recargar sin caché y enviar un mensaje de prueba después de completar el formulario. El token utiliza una cookie Secure y requiere HTTPS.
2. Confirmar recepción y que Responder usa el correo escrito por el visitante.
3. Generar una gráfica y enviarla con el mecanismo original de biorritmos. Confirmar PNG adjunto y dentro del mensaje, y la copia oculta si está activada.
4. Revisar `sudo journalctl -u php-fpm -u nginx --since '10 minutes ago'` si falla. No activar SMTPDebug en producción.

La respuesta «accepted for delivery» significa que el transporte aceptó el mensaje; no garantiza llegada a la bandeja de entrada. No se han enviado correos reales durante la preparación del paquete. Los límites cuentan intentos, incluidos fallos de transporte; se reinician cada hora UTC. Detrás de un proxy, configurar primero real_ip de Nginx con las IP fiables del proxy, o varios visitantes compartirán la misma cuota.

Validación de preparación: sintaxis PHP 8.3 y JavaScript; pruebas de transporte simulado, adjuntos, rutas y cabeceras; pruebas HTTP del token CSRF, sesión, validación, envío simulado y límites; prueba JavaScript de éxito y recuperación de errores. Falta comprobar el envío real y SELinux en Fedora 44. Las pruebas repetibles del núcleo se ejecutan con `php tests/run.php` desde la carpeta del paquete y no necesitan conexión ni envían mensajes.

## Compatibilidad y mantenimiento

`sense_mail()` mantiene sus seis argumentos posicionales. Ahora usa rutas relativas a su propio directorio, valida que el PNG esté dentro de `consultas`, evita variables globales y conserva adjunto e imagen inline. El formulario de contacto cambia de borrador local a envío real. `public/app.js` conserva los menús, monedas y selectores del export 1.3.0.

Estos archivos son una capa para el servidor PHP de Excalibur. No se despliegan en el alojamiento estático de Sites, que no ejecuta PHP. Si vuelves a exportar el sitio estático, conserva o vuelve a aplicar los archivos de `public/` de este paquete. No subas `private/` dentro de `html/`.

Las gráficas siguen siendo generadas por la aplicación antigua: sus dependencias GD/cURL, permisos de `consultas` y otros servicios no los configura este paquete. `compose.php` conserva sus parámetros GET y necesita una revisión adicional de su llamada a ImageMagick antes de admitir entradas de terceros sin confianza. El adaptador de correo no corrige esa ejecución de comandos.

## ¿Necesito configurar PHP mail()?

**No para SMTP.** PHPMailer conecta directamente a OVH con autenticación y TLS; Postfix no participa. No hay que poner host/usuario/contraseña SMTP en `php.ini`: las directivas SMTP de PHP `mail()` son para Windows.

Si prefieres centralizar en el Postfix que ya tiene Excalibur, elegir `transport = sendmail` utiliza `/usr/sbin/sendmail` mediante PHPMailer. Postfix deberá tener ya su salida/relay y autenticación configurados; este paquete no modifica esa configuración. Para código que use específicamente `mail()` en Linux, el ajuste relevante sería `sendmail_path`, pero este módulo no lo usa.

## Credenciales antiguas

El original contiene una contraseña SMTP y los otros PHP incluyen credenciales de servicios externos. Rotarlas y retirarlas del código desplegado y de las copias que se compartan. Este paquete no incorpora esos secretos. La configuración externa protege las nuevas copias; no elimina los secretos de los originales ni de su historial.

## Fuentes

- [Configuración de correo PHP](https://www.php.net/manual/en/mail.configuration.php)
- [PHPMailer y transportes](https://github.com/PHPMailer/PHPMailer)
- [Configuración SMTP MX Plan OVH](https://docs.ovhcloud.com/en/guides/web-cloud/email-and-collaborative-solutions/mx-plan/email-generalities)
