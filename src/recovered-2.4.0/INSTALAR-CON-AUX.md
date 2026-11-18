# Kamala 2.4.0 · instalación completa en Bastion con AUX

Timestamp: 2026-11-15 | Version: 2.4.0
Author & Credits: https://www.alawise.es/1-s

El directorio `html/` contiene la web completa, lista para un alojamiento vacío:
páginas, imágenes, módulos, estilos, laboratorio, notas del Zhouyi en chino
clásico e inglés, vista del péndulo desde arriba y los dos relojes incrustados
en `/time/`. No necesita una instalación anterior de Kamala.

La herramienta de publicación es **AUX 7.0.0-beta.19-deploy.4**. Ejecuta AUX en
el ordenador de trabajo o en Excalibur; Bastion recibe los archivos públicos
por FTPS. La web de Kamala usa su propia carpeta Multisite y su propio perfil,
independientes de los portales AUX/PXE.

## 1. Decidir dominio y origen de los servicios

`kamala-bastion.json` deja `site.public_url` vacío para introducir el dominio
real reservado en Bastion. `ftp_root: /www/kamala` es una propuesta: comprobar
la carpeta Multisite y la raíz visible por la cuenta FTP en OVH.

`site.backend_url` apunta inicialmente a `https://www.kamala.pro`, el origen
actual. Formularios, AstroApp, telemetría y captura permanecen en Excalibur.
Los relojes siguen en `time.1-s.es` y `time1.1-s.es`.

Si se traslada `www.kamala.pro` a Bastion, configurar primero un hostname HTTPS
estable para Excalibur. Actualmente `kamala.pro` redirige a `www.kamala.pro`:
usar el dominio sin www como origen no resuelve por sí solo la separación.
El publicador comprueba esa redirección antes de enviar archivos.

Una copia con otro dominio puede conservar `www.kamala.pro` como origen actual.
El perfil exige hosts diferentes para la web y sus servicios.

## 2. Extraer y configurar

Extraer los dos paquetes en el directorio personal, conservando las carpetas
`aux-suite-7.0.0-beta.19-deploy.4` y `kamala-bastion-2.4.0`:

```bash
tar -xzf aux-suite-7.0.0-beta.19-deploy.4.tar.gz
unzip kamala-bastion-2.4.0.zip

dir_aux="$HOME/aux-suite-7.0.0-beta.19-deploy.4"
cfg_kam="$HOME/kamala-bastion-2.4.0/kamala-bastion.json"
sec_kam="$HOME/.config/aux/kamala-credentials.json"

python3 "$dir_aux/aux-config" --config "$cfg_kam" --secrets "$sec_kam" --interactive
```

En **Sitio web y origen de servicios**, completar `site.public_url` y revisar
`site.backend_url`. En **FTP / FTPS y publicación**, introducir `ftp_host`,
`ftp_user`, `ftp_port`, `ftp_root`, `ftp_tls` y `ftp_password`.

El menú **Modelos y claves API** sigue disponible. Publicar esta web no requiere
consultas a OpenAI o Gemini. Las contraseñas y claves se guardan fuera de la web
en el archivo privado indicado con `--secrets`; la entrada de claves es oculta.
No ejecutar el configurador con sudo: las credenciales pertenecen al usuario
que realizará la transferencia.

## 3. Preparar, generar y verificar localmente

```bash
python3 "$dir_aux/aux-config" --config "$cfg_kam" --secrets "$sec_kam" doctor
python3 "$dir_aux/aux-release" plan --config "$cfg_kam" --secrets "$sec_kam"
python3 "$dir_aux/aux-release" prepare --config "$cfg_kam" --secrets "$sec_kam" --apply
python3 "$dir_aux/aux-release" bundle --config "$cfg_kam" --secrets "$sec_kam" --apply
```

`prepare` copia la web completa a un staging propio, genera `.htaccess`, adapta
los endpoints de lectura a Excalibur, actualiza los metadatos del dominio y
verifica el árbol mediante SHA-256. `bundle` produce además un ZIP público para
subida manual. Estado, configuración y credenciales quedan fuera de ese ZIP.

Si cambian las fuentes o los ajustes que afectan a las páginas, seleccionar
otra `release.release_id` y repetir `prepare`. Se puede cambiar FTP/FTPS sin
regenerar el contenido. Un staging modificado después de la verificación no
se publica.

## 4. Acceso de los feeds públicos de Excalibur

Los tres feeds JSON de observación necesitan permitir la lectura desde el
dominio de Bastion. `prepare` genera `excalibur-cors.conf` junto al estado de
la release, fuera del directorio público.

Añadir sus dos directivas `add_header` dentro de las ubicaciones Nginx
existentes que sirven estos archivos en Excalibur:

- `/telemetry-pendulum/state.json`
- `/telemetry-crystallization/state.json`
- `/telemetry/contemplation.json`

Validar la configuración Nginx y recargarla según el procedimiento habitual.
El endpoint PHP de entropía ya publica su cabecera CORS. La verificación remota
de AUX comprueba las cabeceras CORS y el JSON recibido de los cuatro endpoints.
Los datos del daemon y sus servicios systemd no se instalan en Bastion.

Los enlaces de contacto, Potpourri y astrología se atienden en Excalibur a
través de las redirecciones de `.htaccess`. No se copian sus credenciales,
archivos privados ni configuración administrativa al alojamiento compartido.

## 5. Publicar y comprobar

Crear la carpeta Multisite real, asociar los dominios y habilitar su certificado
SSL en OVH. Con dominio, origen y FTP revisados:

```bash
python3 "$dir_aux/aux-release" publish --config "$cfg_kam" --secrets "$sec_kam" --apply
python3 "$dir_aux/aux-release" verify --config "$cfg_kam" --secrets "$sec_kam" --apply
python3 "$dir_aux/aux-release" status --config "$cfg_kam"
```

También puede abrirse el menú de fases con `aux-release --interactive` y los
mismos argumentos `--config` y `--secrets`.

El envío reutiliza el transporte FTPS de AUX: archivos temporales por hash,
reanudación de transferencias parciales, comprobación de tamaño y publicación
de las portadas al final. No elimina archivos remotos. La verificación remota
requiere que DNS y TLS apunten ya al destino correcto.

## Comprobación de esta entrega

- Web construida desde `1wise/kamala.pro` y las actualizaciones de este proyecto.
- Recursos locales de las páginas comprobados, incluidas imágenes y módulos.
- Pruebas de AUX para el flujo anterior y el perfil independiente de sitios.
- Notas, relojes y navegación revisados en la copia de prueba.
- No se ha realizado una subida real a Bastion ni un cambio DNS.

`PROVENANCE.json` identifica las fuentes y actualizaciones utilizadas.
`SHA256SUMS` permite comprobar la integridad del paquete descargado.

Referencias del alojamiento:

- https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/multisites-configure-multisite
- https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/ftp-connection
