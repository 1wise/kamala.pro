# Cartas, peticiones y tradiciones · 2.0.3

Timestamp: 2026-10-30 | Version: 2.0.3
Author and Credits: https://www.alawise.es/1-s

Descomprimir el paquete fuera de la carpeta pública y ejecutar desde su carpeta:

```bash
sudo python3 tools/install_v2.py --public-only
```

Actualiza las páginas, sus menús y los recursos del formulario. Conserva
las aplicaciones bior, los datos de contacto, la clave activa y los módulos
privados de correo. Guarda los archivos sustituidos en /var/backups/kamala/.
Abrir https://kamala.pro/ sin www y recargar una vez con Ctrl+Shift+R.

## Cambios comprobados en el código

| Método | Construcción de la petición JavaScript |
| --- | --- |
| Occidental natal | Cálculo estándar del SDK; nunca llama a setVarga |
| Jyotisha Rāśi / D1 | Cálculo estándar, ayanamsa elegida y diagrama indio; nunca llama a setVarga |
| Jyotisha divisional | setVarga(n); requiere que getData incluya ese número antes de enviar |

La integración anterior llamaba a setVarga incluso para una carta occidental.
Ahora cada método tiene sus propios valores iniciales y sus opciones de
zodíaco, coordenadas y diagrama. D1 tiene una entrada propia; las 19 divisiones
listadas se muestran en el método divisional.

La respuesta HTTP 500 leída del proveedor identificó NumberFormatException
al analizar 2000:01:01. La referencia facilitada permite YYYY/MM/DD; el código
usa ahora ese formato. Las peticiones natal occidental y Jyotisha Rāśi con el formato de barras
devolvieron HTTP 200, una imagen de carta y XML de cálculo. Se usaron fecha, hora y coordenadas
sintéticas, sin datos de nacimiento personales. Las pruebas locales verifican
también el formato enviado y la selección de cada método.

El SDK observado guarda aID=varga y param=n al ejecutar setVarga(n), pero
omite param en getData(). El formulario detecta ese caso y detiene la petición
con un mensaje explícito. No añade un parámetro no corroborado al contrato.
La activación real de esas divisiones necesita un SDK o contrato del proveedor
que transmita el número solicitado.

## Familias y documentación

El menú tiene entradas propias para Occidental, Jyotisha, China, Maya, Nahua,
Diné, Dreamspell y Mesopotamia. Conserva el glosario completo. Los capítulos
culturales no se presentan como nuevos motores de cálculo conectados.

La documentación pública actual distingue la API JavaScript de Pro y la API
REST/CMS. El código público JavaScript no se reutiliza como credencial REST.
La colección REST publicada utiliza Basic o Bearer, junto a un encabezado key.

| Contrato | Ejemplo de entrada |
| --- | --- |
| JavaScript | setDate, setTime, setLatitude, setLongitude y constantes del SDK |
| REST /chart | JSON con chart.chartData, calcRequestProps y params |
| REST /returns | Petición específica de retornos |
| REST /progressions | Petición específica de progresiones |
| REST /transits/natal y /transits/transits | Peticiones específicas de tránsitos |

Los ejemplos públicos consultados no identifican peticiones específicas para
cartas chinas o mayas. Hace falta su contrato oficial para conectarlas sin
aplicarles parámetros de otra tradición. Las descripciones comerciales de
funciones y los contratos de integración se conservan diferenciados.

Referencias oficiales:

- https://astroapp.com/en/features/api
- https://documenter.getpostman.com/view/1590333/2s8YzUw1vr
- https://github.com/divination/AstroApp-REST-APIs/tree/CodeGen-JAVA
