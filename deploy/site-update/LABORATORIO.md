# kamala.pro — Laboratorio de entropía y posibilidades

Timestamp: 2026-10-31 | Version: 2.0.5
Author & Credits: https://www.alawise.es/1-s

El laboratorio está en `/apps/entropy/` como expositor funcional: pares SSH,
secretos, representaciones de bytes, UUID, TOTP, QR y arte ASCII. La prueba
con cámaras continúa en Earth → Entropy streams. Todos los generadores y
experimentos de Chance usan el módulo compartido `src/entropy-core.mjs`.

## Par de claves SSH

1. Elegir la fuente común: automática, CAM1–CAM4 o Browser only.
2. Mantener marcada **Require a camera sample** si se quiere detener la
   generación cuando no llegue una imagen. Browser only desactiva ese requisito.
3. Elegir Ed25519 o RSA de 3072/4096 bits, añadir un comentario público y
   pulsar **Generate key pair**.
4. Descargar la clave pública en OpenSSH, SPKI PEM o JWK. El QR se actualiza
   con el formato público seleccionado y se puede descargar como PNG o SVG.
5. Elegir OpenSSH o PKCS#8 para la clave privada. La protección por frase está
   activada de inicio; usar al menos 12 caracteres y guardar la frase aparte.
   La clave privada se descarga como archivo y no aparece en la página ni en
   el QR.

La huella identifica el par. La clave pública se instala en el servicio SSH;
la clave privada permanece en el dispositivo desde el que se inicia la
conexión. La página muestra comandos de ejemplo para `~/.ssh`, permisos,
`ssh-copy-id` y `ssh -i`; no instala claves ni se conecta a servidores.
Generar otro par reemplaza el que permanece en memoria. Descarga la clave
privada antes de empezar el siguiente.

| Salida | Contenido |
| --- | --- |
| Clave pública OpenSSH `.pub` | Clave apta para `authorized_keys` y servicios SSH |
| Clave pública SPKI PEM o JWK | Representaciones públicas para aplicaciones compatibles |
| Clave privada OpenSSH o PKCS#8 PEM | Archivo descargable, protegido por frase de inicio |
| QR SSH PNG/SVG | Solo la clave pública en el formato seleccionado |

## Secretos, hexadecimal y otras codificaciones

La segunda sección genera 16, 32, 64 o 128 bytes. Permite representarlos como
hexadecimal, Base64, Base64url o Base32 sin cambiar los bytes al alternar entre
codificaciones. UUID v4 genera un identificador con 122 bits aleatorios; el
cambio hacia o desde UUID requiere una generación nueva.

Cada resultado permite copiar, descargar texto y mostrar su QR expresamente.
Este QR contiene el valor secreto completo y lo transfiere al dispositivo que
lo escanea.

## TOTP

La tercera sección crea un secreto Base32, el QR de configuración y el código
actual de seis dígitos. Usa HMAC-SHA1 y periodos de 30 segundos. El servicio de
destino debe aceptar y configurar el mismo secreto para que esos códigos sean
válidos. El texto y el QR de configuración son privados.

## Random seed ASCII art

**Generate seed ASCII art** solicita una muestra nueva e independiente de la
que se usó para el par SSH. El resultado es un patrón ASCII de 32 × 16
caracteres, con botones para copiarlo o descargarlo como texto. No se muestra
ni se reutiliza la semilla privada de ninguna clave SSH.

## Fuente y privacidad

Cada acción solicita una muestra fresca al muestreador compartido. El
navegador añade sus bytes criptográficos locales. La interfaz etiqueta la
fuente utilizada y, si se exige una cámara, detiene la acción cuando no hay
imagen disponible. Las cámaras son públicas y pueden repetir imágenes; no se
les atribuye una tasa física de entropía medida y no sustituyen la aleatoriedad
criptográfica local.

El navegador genera las claves localmente. La generación Ed25519 usa el
módulo TweetNaCl; RSA usa node-forge con un proveedor explícito de bytes.
Las descargas privadas se pueden cifrar con frase; nunca se envían al
muestreador. El QR SSH contiene la salida pública seleccionada. Los QR de
secretos y TOTP contienen sus respectivos valores y están rotulados.
Limpiar la sesión borra los valores visibles y libera referencias, pero no
borra archivos ya descargados ni contenidos del portapapeles.

El HTML portátil de `html/assets/keys-lab.html` incluye los cuatro generadores,
estilos, bibliotecas y avisos de licencia. Con red consulta el mismo
muestreador público en `https://www.kamala.pro/api/entropy.php`; sin red,
seleccionar Browser only. El documento no carga el SDK de AstroApp ni
bibliotecas desde CDN. Los enlaces portátiles de versiones anteriores siguen
disponibles como copias compatibles de la aplicación completa.

## Enlaces GET

`/api/` documenta el contrato `api_ver=1`, `api_act=configure` y
`vw_mod=entropy`. Una URL puede preseleccionar `src_cam`, `key_typ`, `out_fmt`,
`cnt_itm` y `fil_id`. Solo prepara los controles: cada generación requiere
pulsar un botón. No incluir claves privadas, frases, secretos generados ni
datos sensibles en una URL, porque puede quedar en el historial y en registros.

Referencias: [TweetNaCl](https://github.com/dchest/tweetnacl-js),
[node-forge](https://github.com/digitalbazaar/forge),
[OpenSSH](https://man.openbsd.org/ssh-keygen) y
[node-qrcode](https://github.com/soldair/node-qrcode).
