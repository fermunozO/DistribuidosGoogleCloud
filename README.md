# Laboratorio 2 Sistemas Distribuidos

 Integrantes: ✒️
 -Fernanda Muñoz
 -Matias Paredes

# Descripción del problema 📌
El problema que se quiere resolver es de disponibilizar un servicio de entorno analítico ocupando distintas herramientas de procesamiento de datos escalables (Base de datos con BigQuery, motor de procesamiento con Spark , interfaz de prueba de código con Jupiter Notebook bajo la arquitectura de Terraform). Dada la necesidad de procesar un conjunto de datos densos, se requiere implementar un sistema distirbuido para procesar eficientemente los datos.

# Preparación del ambiente 🚀

## Tecnologías a utilizar 

* Terraform
* Python 3
* R
* Google cloud Platform
	* Big Query
    * Servicios de VM
* Jupyter notebook
* Spark


## Pre-requisitos 📋

* Cuenta vinculada a google la cual debe estar asociada a google cloud platform
* Tarjeta de credito para activar los servicios de VM
* Tener terraform vinculado al path en nuesto entorno local
* Una clave ssh existente

## Instalación 🔧

### Configuración de VM 📄

En primer lugar, se debe crear un proyecto en google cloud para poder consumir sus servicios.
Además, se debe configurar el archivo main.tf para poder levantar el entorno de desarroll. En este
punto se deben considerar los siguentes valores para utilizarlos dentro del archivo de configuración main.tf

* proyect_id
* credenciales del proyecto
* nombre de la clave pública ssh

El proyect_id se puede obtener directamente al crear un nuevo proyecto en google cloud

![Alt Text](https://storage.googleapis.com/gcp-community/tutorials/getting-started-on-gcp-with-terraform/gcp_project_id.png)

Luego de esto, se debe inicializar el archivo main.tf con los siguientes requerimientos:

```
provider "google" {
 credentials = "${file("credenciales.json")}"
 project     = "proyect_id"
 region      = "us-west1"
}
```
Las configuraciones de la instancia de la VM van dentro del grupo de recurso, tales como
el nombre, el tipo de máquina, la interfaz de red asi como la imagen del SO a utilizar

```
resource "google_compute_instance" "default" {
 ...
}
```
Del mismo modo, la clave publica debe ser agregada dentro del grupo de recursos de la VM, donde
el INSERT_USERNAME es el nombre asociado a la clave pública
```
resource "google_compute_instance" "default" {
 ...
metadata {
   sshKeys = "INSERT_USERNAME:${file("~/.ssh/id_rsa.pub")}"
 }
}
```
Asi mismo se deben habilitar puertos
```
resource "google_compute_firewall" "default" {
 name    = "flask-app-firewall"
 network = "default"

 allow {
   protocol = "tcp"
   ports    = ["5000"]
 }
}
```
y una variable para extraer la ip externa de la instancia
```
output "ip" {
 value = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
}
```

Una vez configurado esto, se prodece a ejecutar los comandos de terraform para aplicar los 
cambios y crear la instancia de la VM en google cloud

```
$ terraform init
$ terraform plan
$ terraform apply
```

### Instalación de Jupyter Notebook 📄

Una vez creada la VM, se debe acceder a ella a traves de ssh
```
ssh INSERT_USERNAME@IP_EXTERNAL
```
En este punto se debe instalar jupyter siguiendo los siguientes comandos en la terminal ssh
```
wget http://repo.continuum.io/archive/Anaconda3-4.0.0-Linux-x86_64.sh
bash Anaconda3-4.0.0-Linux-x86_64.sh

```
y siga las instrucciones en pantalla. Los valores predeterminados por lo general funcionan bien, pero responda sí a la última pregunta acerca de cómo anteponer la ubicación de instalación a PATH:

```
Do you wish the installer to prepend the 
Anaconda3 install location to PATH 
in your /home/haroldsoh/.bashrc ? 
[yes|no][no] >>> yes
```

### Configurar el servidor VM 📄

Ahora necesita compruebar si tiene un archivo de configuración de Jupyter:
```
ls ~/.jupyter/jupyter_notebook_config.py
```
si no existe, debe crear uno
```
jupyter notebook --generate-config
```
y agregue las siguientes lineas. Asegurese de colocar el mismo puerto que antepuso en el
archivo de configuracion main.tf
```
c = get_config()
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = <Port Number>
```
deberia quedar de la siguiente manera

![Alt Text](https://cdn-images-1.medium.com/max/1000/1*SwFnrGUO0gWSdO6z8oly_A.png)

### Iniciando Jupyter notebook 📄

Para iniciar Jupyter, ingrese el siguiente comando en la terminal ssh
```
jupyter-notebook --no-browser --port=5000
```

Ahora, para iniciar jupyter notebook, escriba lo siguiente en su navegador:
```
http://<External Static IP Address>:<Port Number>
```
donde, la dirección IP externa es la dirección IP de la VM y el número de puerto es el que permitimos el acceso al firewall

![Alt Text](https://cdn-images-1.medium.com/max/1750/1*7ELRH-iVecVLtFo66jduxQ.png)

### Anexar un dataset de Google Big Query 📄

Para agregar un dataset de Big Query solo basta con agregar un nuevo recurso al archivo main.tf
```
resource "google_bigquery_dataset" "default" {
  dataset_id                  = "my-dataset-name"
  friendly_name               = "test"
  description                 = "my-description"
  location                    = "EU"
  default_table_expiration_ms = 3600000

  labels = {
    env = "default"
  }
}
```
Y para agregar una tabla al dataset, se agrega lo siguiente. Se debe tener en consideración el 
archivo "schema.json" el cual provee la plantilla para definir los valores de la tabla.
```
resource "google_bigquery_table" "default" {
  dataset_id = "${google_bigquery_dataset.default.dataset_id}"
  table_id   = "my-table-name"

  time_partitioning {
    type = "DAY"
  }

  labels = {
    env = "default"
  }

  schema = "${file("schema.json")}"
}
```

### Consumir datos de Google Big Query utilizando Python 3 📄

Para consumir datos de algun schema en Big Query en primer lugar se requiere una clave
de cuenta de servicios para Big Query. Esta se puede obtener dentro de las opciones en
GoogleCloudPlatform -> API&Services -> Credentials  -> new service account key.

![Alt Text](https://jingsblogcom.files.wordpress.com/2018/11/screen-shot-2018-11-26-at-17-54-50.png)

Haga clic en "Crear", luego obtendrá la clave para esta cuenta de servicio en un archivo json. Coloque este archivo json en una carpeta que creó para su proyecto.

#### Instale las bibliotecas cliente de la API de BigQuery de Google para Python en su computadora 📄

Instale las bibliotecas de cliente de BigQuery API de Google para Python en la VM. Las bibliotecas de python de Google BigQuery api client incluyen las funciones que necesita para conectar Jupyter a Big Query.

En la terminal ssh de la VM -> escribe el siguiente comando

```
$ pip install google-cloud-bigquery

```

Ahora debe establecer la variable de entorno llamada "GOOGLE_APPLICATION_CREDENTIALS" para apuntar a jupyter con la clave de su cuenta de servicio que acaba de crear. Esta variable le permite a Google saber dónde encontrar sus credenciales de autenticación. Ejecuta esto antes de comenzar tu Jupyter Notebook cada vez.

```
export GOOGLE_APPLICATION_CREDENTIALS="/Users/~...~/<file-name>.json"

🚀 📋 🔧 ⚙️ 🔩 ⌨️ 📦 🛠️ 🖇️ 📖 📌 ✒️ 📄 🎁 📢 🍺 🤓
