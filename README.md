# Herramienta para la creación de CM y validación de ofertas.

## 1. Introducción
La herramienta se construye con el objetivo de estructurar el proceso de creación de Convenios Marcos (CM) y automatizar el proceso posterior de recepción y validación de ofertas. Esta necesidad nace a partir de la experiencia colaborando en multiples CM, en donde se detecta que no existe un formato estandarizado para generar los distintos productos que se desarrollan durante la formulación de un CM. Entre estos están: árbol de categorías, planilla de evaluación (o formulario backoffice), planillas excels o códigos para realizar la validación y evaluación de ofertas. La falta de un formato estandarizado genera ineficiencia al dificultar el traspaso de información entre estos insumos y generar carga laboral al equipo CM que pudiese ser evitada mediante automatización (p.ej. al pasar manualmente los productos del árbol de categoría a la planilla de evaluación o homologar nombres de producto manualmente para poder cruzar información entre insumos). Para poder automatizar un proceso es necesario estructurarlo.

La herramienta se construye a partir de un modelo de datos que permite estructurar toda la información necesaria para evaluar un CM, el cual es presentado en la sección 2. La herramienta cuenta con una plataforma web desarrollada en [Django](https://es.wikipedia.org/wiki/Django_(framework)) que permite a cualquier usuario (sin conocimiento en programación) interactuar con el modelo de datos. La plataforma además disponibiliza algoritmos que automatizan los procesos de *(i)* creación de la planilla de evaluación, *(ii)* simulación de ofertas y *(iii)* validación de ofertas. La plataforma es descrita en la sección 3: se presenta un manual de instalación y un manual de uso.

## 2. Modelo de datos
Se diseña el modelo de datos con el objetivo de contener toda la información necesaria para validar y evaluar un convenio marco. Si la información se ingresa siguiendo el modelo se pueden automatizar partes del proceso.

### 2.1. Diagrama simplificado
La siguiente figura muestra una versión simplificada del modelo:

<center><img src="/images/erd_simple.png" width="250px"></center>

 * Un Convenio (Bid) tienen categorías (Category) y "atributos del convenio" (BidAttribute). Un ejemplo de atributo del convenio puede ser el transporte o la dificultad de armado del CM Mobiliario 2020.
* Las categorías tienen 0 o más atributos (Attribute), los cuales pueden ser de tipo nominal o ratio. Los atributos nominales toman valores discretos (p.ej. "Lenovo", "Intel Core i5") y los atributos ratio valores numericos seguidos de una unidad de medida (p.ej. "4 gigabytes", "$100,000 CLP").
* Los productos (Products) pertenecen a una categoría y heredan sus atributos. Los atributos consolidan un valor en un producto (AttributeValue). Por ejemplo, el atributo "Marca" puede tomar el valor "Samsung" en un producto, o el atributo "Contenido" puede tomar el valor "1 kilogramos", etc.

### 2.2. Diagrama completo

<center><img src="/images/erd.png" width="750px"></center>

## 3. Plataforma web

### 3.1. Instalación

#### 3.1.1. Instalar python
Puedes descargar python desde el [sitio oficial](https://www.python.org/downloads/). Si tienes complicaciones sugiero seguir [esta guía](
https://tutorial.djangogirls.org/es/python_installation/). Sugiero descargar la versión 3.6 que es la versión en la que se programó. Si tienes una verisón superior no debería haber problema.

#### 3.1.2. Crear un ambiente virtual y activalo
Un ambiente virtual ayuda a mantener ordenado tus proyectos Python. Es una buena practica muy sencilla de usar.  Crea el ambiente "site_validador" escribiendo el siguiente comando en la consola (si no sabes como hacer esto te recomiendo [esta guía](https://tutorial.djangogirls.org/es/django_installation/#entorno-virtual):
```
python3 -m venv site_validador
```
#### 3.1.3. Instala django y los paquetes necesarios
Con el ambiente virtual activado, navega en la consola hasta la carpeta del repositorio y ejecuta el siguiente comando. Esto instalará todos los paquetes necesarios para levantar la plataforma.
```
pip install -r requirements.txt
```
Recomiendo [esta guía](https://tutorial.djangogirls.org/es/django_installation/#instalar-paquetes-con-un-fichero-de-requisitos-requirements) para más detalles de como hacerlo.

#### 3.1.4. Levanta el sitio localmente
Debes navegar a la carpeta del repositorio y ejecutar el comando
```
python manage.py runserver
```
Si todo está en orden deberias ver un mensaje que dice:
```
Django version 3.1.7, using settings 'site_validador.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
No cierres la consola ya que el sitio está corriendo en ella.

#### 3.1.5. Visita la plataforma
Abre tu navegador web favorito y visita la dirección http://127.0.0.1:8000/ , deberias ver un mensaje de bienvenida. Ya puedes usar el validador

### 3.2. Manual de uso
Al visitar http://127.0.0.1:8000 deberías ver la siguiente pantalla de bienvenida.

<img src="/images/index.png" width="750px">

Al hacer click en entrar veras el menú de Convenios Marco, deberías poder ver el convenio de Mobiliario, que fue creado a modo de ejemplo siguiendo las mismas reglas del CM Mobiliario 2020. 

<img src="/images/bids.png" width="750px">

La creación de este convenio se usara como ejemplo en el presente manual.

#### 3.2.1. Crear un convenio
La pantalla de crear un convenio preguntará los siguientes campos:
* Nombre: nombre del convenio
* Niveles de categoría: profundidad del árbol de categorías. Lo clásico en ChileCompra es 3 (Categoría Nivel 1, Categoría Nivel 2, Tipo de Producto).
* Zonas: Si el convenio se oferta por zonas se deben agregar acá separadas por enter. Si se oferta a nivel nacional se puede agregar una sola zona "NACIONAL" o dejar el campo en blanco.
* Número de alternativas de producto: Cuantas alternativas de productos podrá ingresar un proveedor para cada ficha de producto.

El ejemplo de CM Mobiliario se configuró de la siguiente manera:

<img src="/images/create_bid.png" width="750px">

#### 3.2.2. Vista de un convenio
La vista de un convenio da acceso a 3 menús: 
* Atributos del convenio: para administrar condiciones del convenio como transporte o dificultad de armado
* Catálogo: para administrar el árbol de categorías, atributos y productos
* Algoritmos: da acceso a los algoritmos que permiten automatizar tareas.
<img src="/images/bid.png" width="750px">

#### 3.2.3. Atributos del convenio
En el ejemplo del CM Mobiliario hay 3 atributos modelados: Transporte rural, Transporte urbano y Dificultad de Armado. Los atributos se pueden editar y eliminar.
<img src="/images/bidattributes.png" width="750px">

#### 3.2.4 Crear atributo del convenio
Se preguntan los siguientes campos:
* Nombre del atributo.
* ¿Se oferta a nivel nacional o por zona?: Si el atributo es ofertado a nivel nacional (ej: dificultad de armado) o a nivel de macrozona (ej: transporte).
* Unidad: Moneda en la que se ofertará el atributo.

A modo de ejemplo, se presenta la pantalla para el atributo transporte rural:
<img src="/images/create_bidattribute.png" width="750px">

#### 3.2.5 Vista atributo del convenio
La vista atributo del convenio muestra una tabla con los distintos niveles a los que ofertarán los proveedores. A modo de ejemplo se presentan pantallazos de los atributos dificultad de armado (que se oferta a nivel nacional) y transporte rural (que se oferta por zona).
<img src="/images/bidattribute_global.png" width="750px">
<img src="/images/bidattribute_zone.png" width="750px">

#### 3.2.5 Crear nivel de atributo de convenio
Al hacer click en agregar nivel se despliega un formulario en el que se debe agregar el nombre del nivel y las restricciones de precio que este tiene. Se presenta el nivel "dificultad baja" del atributo dificultad de armado a modo de ejemplo.
<img src="/images/create_bidattributelevel.png" width="750px">

#### 3.2.6. Catálogo
Al entrar al menú catálogo veras el árbol de categorías. Puedes agregar categorías nivel 1 haciendo click en "Agregar categoría nivel 1" e ingresando el nombre de la categoría. Si definiste el convenio con "Niveles de categoría" > 1, podras profundizar en el árbol agregando categorías hijas. Para esto debes hacer click en el botón "+" de la columna Agregar. Las categorías que están más abajo en el árbol (categoría hoja) son configurables haciendo click en ellas. En el ejemplodel CM Mobiliario se fijo "Niveles de categoría = 1", por lo que el árbol no tiene profundidad.
<img src="/images/categories.png" width="750px">

#### 3.2.7. Categoría
Cuando ingresas a una categoría hoja veras dos secciones "Atributos" y "Productos". En cada una te estas secciones veras un botón para agregar nuevos objetos. Asi se ve la categoría "SILLA DE ESCRITORIO" configurada.
<img src="/images/category.png" width="750px">
Como podras notar, las tablas tienen varios conceptos,los cuales serán explicados en las siguientes secciones. Es importante destacar por ahora que **el flujo de trabajo se pensó para crear los atributos primero y luego los productos**. Crear un atributo borrará los productos previamente creados en la categoría.

#### 3.2.8. Crear atributo
El formulario de creación de un atributo consiste en:
* Nombre atributo
* Restricciones a nivel nacional o por zona: Si las restricciones del atributo serán fijadas a nivel nacional o por zona. A modo de ejemplo tomemos el caso del atributo Precio: si se desea que los productos tengan un precio minimo y maximo identico para todo Chile, entonces se debe ingresar el valor "Nacional". En el caso contrario, si se desea variar el precio minimo y maximo para cada zona definida, entonces se debe seleccionar "Zona".
* ¿Valor fijo?: Indica si el valor del atributo será fijado por chilecompra ("SI") o si debe ser completado por el proveedor ("NO").
* Tipo atributo: Se debe seleccionar si el atributo es nominal o ratio. Recordar que los atributos nominales son aquellos que toman valores discretos mientras que los atributos ratio son aquellos que toman valores conformados por un valor númerico más una unidad de medida. Dependiendo de lo que se seleccione en este campo apareceran más campos.
* ¿Acepta otros valores?: Se debe configurar solo si *¿Valor fijo? = NO* y *Tipo atributo = NOMINAL*. Si se selecciona que "NO", entonces el proveedor podra ingresar solo valores del listado definido para ese producto. Por ejemplo, el atributo "¿Tiene Ruedas?" es configurado para no aceptar nuevos valores ya que se busca que el proveedor ingrese un valor dentro de los definidos: "Si" o "No". Por otro lado, veamos el ejemplo del atributo "Marca". Porbablemente para "Marca" queramos fijar este campo como "Si", ya que buscamos que el proveedor ingrese una marca del listado predefinido, pero si su producto es de una marca que no aparece en el listado, darle la libertad de poder agregarla.
* Unidad: Se debe configurar cuando el atributo es ratio. Corresponde a la unidad de medida del atributo, p.ej. "CENTIMETRO", "PESO CHILENO", "KILOGRAMO", etc.
* ¿Solo valores enteros?: Se debe configurar solo si *¿Valor fijo? = NO* y *Tipo atributo = RATIO*. Indica si el valor numerico ingresado por el proveedor puede tomar solo valores enteros ("SI") o si permite ingresar decimales ("NO").

A modo de ejemplo se muestra la configuración de dos atributos para el TP "Silla de Escritorio".
<img src="/images/attribute1.png" width="750px">
<img src="/images/attribute2.png" width="750px">

#### 3.2.8. Crear producto
Al crear un producto se abre un menú que muestra los atributos definidos para la categoría y campos para configurar sus valores. Hay cuatro tipos de atributos:
* Nominales fijos: Se debe ingresar el valor fijo del atributo
* Ratio fijos: Se debe ingresar el valor fijo del atributo
* Nominales variables: Se deben ingresar los posibles valores separados por enter
* Ratio variables: Se debe ingresar los valores numericos minimo y maximo que puede tomar el atributo.
Además se muestra un campo llamado "Modelo". Se puede pensar en este campo como un nombre corto para el producto, por ejemplo: Gama Baja.

A modo de ejemplo, esta es la configuración para la Gama 1 del TP Silla de Escritorio.
<img src="/images/create_product.png" width="750px">

#### 3.2.9. Algoritmos
Hay 4 menús en esta vista. Cada uno genera un productos descargables. En la carpeta *ejemplos output* está el ejemplo de cada uno para el CM Mobiliario.

<img src="/images/algorithms.png" width="750px">

* Descargar JSON: Permite descargar todo el modelo de datos del convenio en un formato JSON estructurado.
* Descargar planilla excel: Descarga la planilla excel para la recepción de ofertas. Cada hoja de la planilla corresponde a un atributo del convenio o un TP. Las celdas tienen restricciones para evitar que el proveedor cometa errores. 
* Simular ofertas: Permite simular planillas de ofertas completadas por un proveedor. Se pueden simular los errores que comunmente cometen los proveedores mediante probabilidades, tal como se muestra en las instrucciones:

<img src="/images/simulate.png" width="750px">

* Validar ofertas: El menú desplegable permite cargar multiples planillas de ofertas completadas (ya sea simuladas o reales). Estas serán procesadas para validar que se cumplan las reglas ingresadas en la plataforma para el convenio. Al ser procesadas, la plataforma entrega un archivo excel que consolida todas las ofertas en una sola hoja, con una columna que informa el estado ("OK" o "ERROR") de una oferta.
