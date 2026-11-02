# kamala.pro — Tiradas, monedas y escalas

Timestamp: 2026-10-30 | Version: 2.0.0
Author & Credits: https://www.alawise.es/1-s

## Cartas

En `/apps/cards/` y en el artículo de Cards se puede elegir:

- Baraja española de 40 cartas, sin ochos ni nueves, o de 48, con ambos.
- Naipes americanos: 52 cartas, sin comodines.
- Tarot de Marsella: 78 cartas, con 22 arcanos mayores y 56 menores.

Las caras son representaciones esquemáticas propias de Kamala, con su palo,
nombre y valor. No son reproducciones de las ilustraciones de una edición
histórica. En Marsella, Justicia ocupa VIII y Fuerza XI; Le Mat queda sin número.

La matriz admite filas y columnas enteras de 1 a 78, siempre que el producto
no supere las cartas restantes. El reparto avanza por filas. Las matrices
anchas se desplazan horizontalmente dentro de su propio panel.

La cruz reparte cinco cartas en este orden exacto:

| Número | Posición |
| --- | --- |
| 1 | Centro |
| 2 | Arriba |
| 3 | Abajo |
| 4 | Izquierda |
| 5 | Derecha |

Cada carta sale sin reposición. Cambiar baraja, tamaño o disposición inicia
una sesión nueva y limpia su historial. Reset deck repone la baraja.

## Monedas y retrato

Las monedas muestran el retrato proporcionado en la cara y una cruz maltesa
de ocho puntas en la otra.

Coin portrait permite elegir una imagen local JPEG, PNG o WebP de hasta
8 MiB y 25 megapíxeles. La imagen se muestra mediante una URL temporal del
navegador; no se envía al servidor ni se guarda de forma persistente. Clear
local photo la libera. La foto pública está en `/assets/coin-portrait.png`;
su ruta se configura en `dat_mon.portrait`.
dentro de `src/chance-core.mjs`.

El flujo del selector local de archivos no pudo completarse en el navegador
de pruebas: la automatización agotó su tiempo de espera. No se afirma que
esa selección haya sido verificada de extremo a extremo.

## I Ching

Está disponible como modo de Coins, en `/apps/yijing/` y dentro del artículo
I Ching / Yijing. Se utiliza el método de tres monedas:

| Total | Línea inicial | Línea resultante |
| --- | --- | --- |
| 6 | Yin cambiante, partida | Yang, continua |
| 7 | Yang estable, continua | Igual |
| 8 | Yin estable, partida | Igual |
| 9 | Yang cambiante, continua | Yin, partida |

Cara vale 3 y cruz maltesa vale 2. Se construyen seis líneas de abajo arriba.
Cada línea conserva sus tres resultados y la etiqueta de la fuente utilizada.
La interfaz muestra las figuras inicial y resultante, sus números en el orden
Rey Wen y las líneas cambiantes numeradas desde abajo.

Cast line avanza una línea. Cast all six lines crea las seis desde una sesión
vacía. Una acción solicita una muestra del servicio compartido; la generación
completa comparte esa muestra entre las 18 monedas, añadiendo aleatoriedad
criptográfica del navegador en cada resultado. Las probabilidades de obtener
6, 7, 8 o 9 son 1/8, 3/8, 3/8 y 1/8. No son las del método de tallos de milenrama.

## Runas

Hay dos alfabetos: futhark joven de 16 signos y futhark antiguo de 24.
El de 24 es históricamente anterior. Se ofrecen etiquetas en finés (suomi),
nombres convencionales y transliteración latina. Los signos, nombres y
transliteraciones siguen siendo visibles al seleccionar las glosas finesas.

Las glosas son traducciones modernas de referencia, no nombres ugrofineses
antiguos reconstruidos. Los alfabetos son germánicos. Varios nombres y
significados son discutidos; Perthro queda marcado como incierto.
La extracción se hace sin reposición y no añade una runa en blanco.

## Hand scale y Human scale

Hand scale agrupa objetos manipulados: cartas, monedas, dados, runas, péndulo,
posos, Yijing, herramientas de radiestesia, contemplación de cristal y vela,
y escritura o pintura sobre un soporte.

Human scale conserva cuerpo y percepción: lectura de la mano, kinestesia,
respiración, escucha, contemplación, sueños lúcidos y relatos de clarividencia.
Materia, Tierra y sistema solar conservan sus ámbitos. Las cinco escalas
aparecen en los menús compartidos y en las páginas correspondientes.

## Instalación y comprobaciones

Copiar el contenido de `html/` del ZIP y seguir `INSTALAR.md` para migrar el
menú y los metadatos del contacto sin sustituir su formulario. No se instala
un servicio adicional ni se modifica la configuración de correo.

Se comprobaron los cuatro tamaños de baraja, su agotamiento sin repetición,
la cruz, los límites de matriz, ambos alfabetos, los ocho resultados posibles
de tres monedas y la correspondencia de los 64 hexagramas. Las páginas
pasaron las comprobaciones de metadatos, navegación, recursos y enlaces.
En navegador se comprobaron la cruz de Marsella, una matriz de 4 × 13 con
52 cartas únicas y desplazamiento dentro del panel, los 16 y 24 signos sin
repetición, el cambio de glosa a transliteración, los modos de monedas e
I Ching, la generación de seis líneas y el avance línea a línea. La fuente
utilizada en esa revisión fue Browser only; las cámaras de Excalibur quedan
pendientes de comprobar tras la subida.

Referencias: [Universidad de Copenhague — runología](https://nors.ku.dk/english/research/runes/),
[Riksantikvarieämbetet — transliteración](https://www.raa.se/kulturarv/runor-och-runstenar/att-lasa-runor-och-runinskrifter/),
[BnF — baraja de Marsella](https://www.bnf.fr/fr/un-tarot-qui-rebat-les-cartes-collections),
[Chinese Text Project — Libro de los Cambios](https://ctext.org/book-of-changes),
[Orden de Malta — cruz de ocho puntas](https://www.orderofmalta.int/history/the-eight-pointed-cross/).
