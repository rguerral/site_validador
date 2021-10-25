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

<img src="/images/create_bid.png" width="750px">