# Kamala.pro en Fedora 44

Timestamp: 2026-10-28 | Version: 1.0.0  
Author and Credits: https://www.alawise.es/1-s

Raíz pública: `/var/www/kamala.pro/html`. Dominios: `kamala.pro` y
`www.kamala.pro`. El archivo de Nginx sirve inicialmente HTTP; Certbot añade
HTTPS después de comprobar el DNS.

## 1. Paquetes y directorios

```bash
sudo dnf install nginx php-fpm php-cli policycoreutils-python-utils unzip
sudo install -d -m 0755 /var/www/kamala.pro/html
sudo install -d -o nginx -g nginx -m 0700 /var/lib/php/kamala /var/lib/php/kamala/session /var/lib/php/kamala/tmp
```

Extraer los archivos de la web en la raíz pública. Conservar o copiar allí la
carpeta original `bior/`, incluidos sus archivos PHP y SolarSimulator: el ZIP
estático de la web no contiene el código de esas aplicaciones.

Si biorritmos utiliza la extensión GD para generar imágenes:

```bash
sudo dnf install php-gd
```

## 2. Configuración

Desde la carpeta que contiene estos archivos:

```bash
sudo install -m 0644 kamala.pro.conf /etc/nginx/conf.d/kamala.pro.conf
sudo install -m 0644 kamala-fpm.conf /etc/php-fpm.d/kamala.conf
```

Debe existir un solo vhost para estos nombres. Si ya hay un bloque de Kamala en
otro archivo de Nginx, sustituir ese bloque por este. Los demás sitios y pools
pueden seguir usando su propia configuración.

La portada prioriza `index.html`. Las páginas interiores se resuelven mediante
sus carpetas e índices reales. Las consultas de PHP conservan sus parámetros.

## 3. Permisos y SELinux

Los archivos públicos deben ser legibles y sus directorios transitables para
Nginx. Para aplicar permisos de lectura al contenido de este sitio:

```bash
sudo find /var/www/kamala.pro/html -type d -exec chmod 0755 {} +
sudo find /var/www/kamala.pro/html -type f -exec chmod 0644 {} +
sudo restorecon -RFv /var/www/kamala.pro
sudo semanage fcontext -a -t httpd_sys_rw_content_t '/var/lib/php/kamala(/.*)?'
sudo restorecon -RFv /var/lib/php/kamala
```

Si esa regla exacta ya está registrada, usar `semanage fcontext -m` en lugar de
`-a` para actualizarla. El contenido público usa la etiqueta de lectura de
`/var/www`; solo las sesiones y temporales privados necesitan escritura.

La imagen y el visor de `go.1-s.es` los carga el navegador. Esta configuración
no necesita un proxy HTTP ni habilitar `httpd_can_network_connect` para ello.
No se fija una política SAMEORIGIN que impida los iframes entre los dos nombres.

## 4. Comprobar y activar

Ejecutar cada comprobación y corregir cualquier error antes de continuar:

```bash
sudo php-fpm -t
sudo nginx -t
sudo systemctl enable --now php-fpm nginx
sudo systemctl reload php-fpm nginx
curl -I -H 'Host: kamala.pro' http://127.0.0.1/
curl -I -H 'Host: kamala.pro' http://127.0.0.1/traditions/
```

Si se usa firewalld, añadir los servicios a la zona que contiene la interfaz
pública; sustituir `ZONA_PUBLICA` por el nombre que muestre el primer comando:

```bash
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=ZONA_PUBLICA --permanent --add-service=http --add-service=https
sudo firewall-cmd --zone=ZONA_PUBLICA --add-service=http --add-service=https
```

## 5. HTTPS

Los registros A y, si existen, AAAA de ambos nombres deben llevar a este
servidor. El puerto 80 debe ser accesible desde Internet para la validación.
Después:

```bash
sudo dnf install certbot python3-certbot-nginx
sudo certbot --nginx -d kamala.pro -d www.kamala.pro --redirect
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl enable --now certbot-renew.timer
sudo certbot renew --dry-run
```

Certbot modifica el vhost y añade la redirección a HTTPS. Después de ese paso,
conservar la versión que incluye el certificado al hacer cambios posteriores.

## Comprobación pendiente en el servidor

Los archivos se han preparado con las directivas documentadas por Nginx,
PHP-FPM y Fedora. Este entorno no dispone de los binarios `nginx` y `php-fpm`;
las comprobaciones de sintaxis y funcionamiento deben ejecutarse en Fedora.

Referencias:

- https://fedoraproject.org/wiki/Nginx
- https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files
- https://nginx.org/en/docs/http/ngx_http_fastcgi_module.html#fastcgi_pass
- https://www.php.net/manual/en/install.fpm.configuration.php
- https://packages.fedoraproject.org/pkgs/certbot/python3-certbot-nginx/
