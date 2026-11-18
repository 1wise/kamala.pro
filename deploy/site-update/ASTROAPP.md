# AstroApp JavaScript · 2.0.3

Timestamp: 2026-10-30 | Version: 2.0.3
Author and Credits: https://www.alawise.es/1-s

El SDK se carga solo en el head del espacio /astrology/. El instalador lee
astroapp-config.json del servidor y conserva la clave activa. El código no
viaja en Git ni en los paquetes. La etiqueta usa referrerpolicy=origin.

## Métodos de carta

Occidental natal y Jyotisha Rāśi / D1 conservan el cálculo estándar del SDK.
Solo una carta divisional llama a setVarga(n). El formulario aplica las
opciones de cada familia y distingue el cálculo de su diagrama.

El formato de fecha enviado es YYYY/MM/DD. El servidor devolvió
NumberFormatException con YYYY:MM:DD. Tras cambiarlo, dos peticiones
sintéticas —natal occidental y Jyotisha Rāśi— devolvieron HTTP 200, imagen
y XML de cálculo. No se enviaron datos de nacimiento personales.

El SDK observado guarda aID=varga y param=n, pero omite param al serializar
getData(). La aplicación bloquea esa petición incompleta y explica el motivo.
La conexión de divisiones requiere un SDK o contrato que transmita el número.

Los métodos de casas, ayanamsa, coordenadas, idioma y estilo usan las constantes
del propio SDK. Sus identificadores no se copian del contrato REST. La API
REST tiene otros esquemas y autenticación; véase deploy/astroapp/CHARTS.md.

## Tradiciones y contenido

El menú distingue Occidental, Jyotisha, China, Maya, Nahua, Diné, Dreamspell
y Mesopotamia. El glosario conserva nombres y definiciones. Las peticiones
para China y Maya siguen pendientes de su especificación oficial concreta.

## Origen de la clave

La comprobación del 30 de octubre de 2026 devuelve el SDK con Referer
https://kamala.pro/ y rechaza los orígenes https://www.kamala.pro/ y la ruta
completa https://kamala.pro/astrology/. La política origin envía el origen
sin la ruta. Usar el dominio sin www o su redirección canónica en Nginx.

Las pruebas locales usan claves ficticias. Las comprobaciones remotas usaron
el código ya publicado por el sitio sin guardarlo ni incluirlo en artefactos.
