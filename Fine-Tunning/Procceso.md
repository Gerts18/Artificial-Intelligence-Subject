# Fine-tunning de una LLM para crear un tutor de programacion 
El **fine‑tuning** es un proceso donde se modifican los parámetros internos de un modelo ya entrenado para adaptarlo a un cierto tema. 
En este caso se busca que imite a un tutor de programacion para que cualquiera que lo consulte le ayude a aprender. 

El primer paso es recolectar dato de ejemplo de instrucciones para que el modelo las use como ejemplo de como responder cuando el usuario hace una pregunta. 

En este caso se usaron 300 ejemplos diferentes con Instruccion y Respuesta para que el modelo pueda comprender como actuar. Aqui se decidio que el lenguaje a enseñar seria el de Python, por lo cual cada ejmplo tiene un breve fragmento de codigo y explicacion usando Python como ejemplo.

El modelo sobre el cual se hizo esta capa extra de entrenamiento fue **deepseek-r1** y el framework que se utilizo fue **LoRA** (Low‑Rank Adaptation) que es una técnica moderna que permite entrenar modelos grandes usando muy poca memoria.

El proceso se llevo a cabo en google collab, ya que el equipo que se tenia no contaba con la capacidad suficiente para hacer este tipo de entrenamientos. Collab proporciona un entorno de ejecucion de codigo en linea con recursos limitados gratuitos pero que en este caso fueron suficientes para realizar varios entrenamientos y pruebas para obtener el resultado esperado. 

Los pasos que se llevaron a cabo:

- Instalacion de paquetes necesarios
![imagen ejemplo](Fine-Tunning\images\1.png)

- Comprobando que estemos usando una GPU para hacer un entrenamiento mas rapido
![imagen ejemplo](Fine-Tunning\images\2.png)

- Importamos librerias necesarias 
![imagen ejemplo](Fine-Tunning\images\3.png)

- Cargamos el dataset con los ejemplos necesarios 
![imagen ejemplo](Fine-Tunning\images\4.png)

- Importamos el modelo sobre le cual le vamos a aplicar la capa de entrenamiento personalizado
![imagen ejemplo](Fine-Tunning\images\5.png)

- Configuramos Lora 
![imagen ejemplo](Fine-Tunning\images\6.png)

- Preprocesamos el Dataset para que quede limpio y bien estructurado
![imagen ejemplo](Fine-Tunning\images\7.png)

- Ejecutamos el entrenamiento, aqui despues de varios resultados, se dejo con 6 epocas y un learning rate de 1e-4 ya que al no tener tanto datos de entrenamiento queremos evitar el overfitting
![imagen ejemplo](Fine-Tunning\images\8.png)

- Una vez obtenida la capa que entrenamos, obtenemos un adaper que podemos probar para ver si el modelo responde como esperamos
![imagen ejemplo](Fine-Tunning\images\9.png)

- Ya que vimos que responde como buscamos, fusionamos nuestro adapter con el modelo para obtener un modelo completo con el fine-tunning esperado
![imagen ejemplo](Fine-Tunning\images\10.png)

- Instalamos los paquetes necesarios para poder transformar nuestro modelo fusionado a tipo GGUF para poderlo usar con ollama 
![imagen ejemplo](Fine-Tunning\images\11.png)

- Exportamos el modelo a drive para poder descargarlo y usarlo de manera local
![imagen ejemplo](Fine-Tunning\images\12.png)

- Ahora usamos un Modelfile para hacer unas configuraciones mas y poder exportarlo a ollama para poder usarlo. Vease que aqui especificamos un prompt de Sistema para que el modelo sepa a lo que esta enfocado.
![imagen ejemplo](Fine-Tunning\images\13.png)

- Listo, ya tenemos nuestro modelo funcioando 
![imagen ejemplo](Fine-Tunning\images\14.png)

