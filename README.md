# Herramienta para la creación de CM y validación de ofertas.

## 1. Introducción
La herramienta se construye con el objetivo de estructurar el proceso de creación de Convenios Marcos (CM) y automatizar el proceso posterior de recepción y validación de ofertas. Esta necesidad nace a partir de la experiencia colaborando en multiples CM, en donde se detecta que no existe un formato estandarizado para generar los distintos productos que se desarrollan durante la formulación de un CM. Entre estos están: árbol de categorías, planilla de evaluación (o formulario backoffice), planillas excels o códigos para realizar la validación y evaluación de ofertas. La falta de un formato estandarizado genera ineficiencia al dificultar el traspaso de información entre estos insumos y generar carga laboral al equipo CM que pudiese ser evitada mediante automatización (p.ej. al pasar manualmente los productos del árbol de categoría a la planilla de evaluación o homologar nombres de producto manualmente para poder cruzar información entre insumos). Para poder automatizar un proceso es necesario estructurarlo.

La herramienta se construye a partir de un modelo de datos que permite estructurar toda la información necesaria para evaluar un CM, el cual es presentado en la sección 2. La herramienta cuenta con una plataforma web desarrollada en [Django](https://es.wikipedia.org/wiki/Django_(framework)) que permite a cualquier usuario (sin conocimiento en programación) interactuar con el modelo de datos. La plataforma además disponibiliza algoritmos que automatizan los procesos de *(i)* creación de la planilla de evaluación, *(ii)* simulación de ofertas y *(iii)* validación de ofertas. La plataforma es descrita en la sección 3: se presenta un manual de instalación y un manual de uso.

### 2.1. Diagrama simplificado
La siguiente figura muestra una versión simplificada del modelo: 
<img src="/images/erd_simple.png" width="250px">
 * Un Convenio (Bid) tienen categorías (Category) y "atributos del convenio" (BidAttribute). Un ejemplo de atributo del convenio puede ser el transporte o la dificultad de armado del CM Mobiliario 2020.
* Las categorías tienen 0 o más atributos (Attribute), los cuales pueden ser de tipo nominal o ratio. Los atributos nominales toman valores discretos (p.ej. "Lenovo", "Intel Core i5") y los atributos ratio valores numericos seguidos de una unidad de medida (p.ej. "4 gigabytes", "$100,000 CLP").
* Los productos (Products) pertenecen a una categoría y heredan sus atributos. Los atributos consolidan un valor en un producto (AttributeValue). Por ejemplo, el atributo "Marca" puede tomar el valor "Samsung" en un producto, o el atributo "Contenido" puede tomar el valor "1 kilogramos", etc.

### 2.2. Diagrama completo
<img src="/images/erd.png" width="250px">





## 3. Plataforma web
