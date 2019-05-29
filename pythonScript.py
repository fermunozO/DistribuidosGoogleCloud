from google.cloud import bigquery
import names
import random
import findspark
findspark.init()
from pyspark.sql import SparkSession
import json
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.sql import Row
from pyspark import SQLContext

generos = ['male','female']

def export_items_to_bigquery(rows_to_insert):
    # Instanciar el cliente
    bigquery_client = bigquery.Client()

    # Preparar la referencia al dataset y a la tabla que tenemos en Big Query
    dataset_ref = bigquery_client.dataset('Dataset_1')
    table_ref = dataset_ref.table('Personas')
     
    # LLamamos a la API para obtener la tabla que referenciamos
    table = bigquery_client.get_table(table_ref) 
    
    # Procedemos a ingresar en la tabla nuestras filas que creamos 
    errors = bigquery_client.insert_rows(table, rows_to_insert)  # API request
    assert errors == []
    
def creaDatosAleatorios(cantidad,listado):
    for i in range(0,cantidad):
        generoAleatorio = random.choice(generos)
        nombreAleatorio = names.get_full_name(gender=generoAleatorio)
        edadAleatoria = random.randint(18,90)
        pesoAleatorio = random.uniform(1.40, 2.10)
        estaturaAleatoria = random.uniform(35, 90)
        tupla = (nombreAleatorio,edadAleatoria,generoAleatorio,estaturaAleatoria,pesoAleatorio)
        listado.append(tupla)
    return listado

def import_items_from_bigquery():
    # Iniciacion del cliente
    bigquery_client = bigquery.Client()
    
    # Query de BigQuery
    QUERY = """ SELECT * FROM `x-pivot-241800.Dataset_1.Personas` LIMIT 100 """
    
    # Arranca la Query y se obtienen los datos
    query_job = bigquery_client.query(QUERY) # API REQUEST
    
    return query_job.to_dataframe()


# _____ MAIN ______

spark = SparkSession.builder.appName('ANALYTICS').getOrCreate()
listadoTuplas = []
#rows = creaDatosAleatorios(100,listadoTuplas)
#export_items_to_bigquery(rows)
#df = spark.createDataFrame(df)
data = import_items_from_bigquery()
tuples = [tuple(x) for x in data.values]

sc = SparkContext.getOrCreate(SparkConf().setMaster("local[*]"))
sqlContext = SQLContext(sc)
rdd = sc.parallelize(tuples)
people = rdd.map(lambda x: Row(nombre=x[0], edad=int(x[1]),genero=x[2],estatura=float(x[3]),peso=float(x[4])))
schemaPeople = sqlContext.createDataFrame(people)
schemaPeople.select('nombre','edad','genero').show()

schemaPeople.describe('edad').show()