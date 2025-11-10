# Actividad con modelos OLLAMA
Pasar el temario de Inteligencia Artificial a varios modelos de IA descargados atraves de ollama, con el fin de crear un algoritmo de recomendación para cursar la materia. 

# Modelos, resultados y sus análisis 

- gemma3 
Este modelo solo responde en ingles, no se adapta al idioma en el cual le pasas el prompt. Se extiende bastante en las respuestas y al final siempre pide retroalimenteción para seguir con la conversación. 
Cuando se le pregunto los tres prererquisitos más fundamentales menciono saber *Teoria de Grafos* que incluye saber sobre algoritmos de busqueda en grafos y para encontrar el camino mas corto, siendo interesante que hizo incapie en el algoritmo A* el cual es el que efectivamente vimos al inicio del curso y practicamos bastante. 

Me di cuenta que se adelantaba a las preguntas, por ejemplo, para la tercer pregunta que habla sobre el lenguaje de programación más recomendado, ya me lo habia mencionado en la respuesta de la segunda pregunta, recomendando python. 

La lista de recomendaciones que dio al final fue un resumen de sus respuestas a mis preguntas anteriormente, pero mencionando temas bastante especificos o necesarios. 

Nota: A pesar de que este modelo no tenia acceso a internet, y el prompt especificaba buscar en fuentes externas, considero que dio buenas respuestas.

- mistral
La primer respuesta la dio en ingles pero despues ya empezo a responder en español. Sus respuestas han sido muy generales y cortas, al no tener tampoco la funcionalidad de busqued web se limita a lo que sabe y no da retroalimentacion. 
Aqui al preguntarle sobre el lenguaje de programación más recomendado, no se limito a mencionar python, si no que menciono varios como R y Matlab que si son bastante buenos para el tema y otros como Java y C++ que tambien tienen librerias para trabajar con redes neuronales. 

Su lista de recomendaciones fue igulamente un resumen de las preguntas que le dije anteriormente de forma muy general, casi no dio ninguna recomendación buena más que usar recursos en linea como tutoriales o documentos para aprender inteligencia artifical y ademas algo muy interesante es que recomendo participar activamente en clase y practicar la comunicación escrita y oral, dos recomendaciones generales para rendir bien en la mayoria de materias.

- llama 3.2
El unico modelo que desde la primer respuesta ma hablo en español. A comparación de los anteriores modelos, este respondia de forma rapida, siendo que mi hardware se veia limitado por 8 GB de RAM, este es el modelo con el que me senti mas comodo. 
Sus respuestas son más estructuradas y completas que el el modelo *mistral* pero menos que el modelo *gemma3*, esto se nota porque da respuestas mas completas pero solo relacionadas a la pregunta que se le hace y no trata de extenderse a otros temas como lo hacia *gemma* que ya estaba mencionando el mejor lenguaje de programación mucho antes de preguntarselo. 

Aparte de python, es el unico modelo que recomendo aprender el lenguaje de programación llamado *Julia*, en lo demás hizo las mismas recomendaciones que los demás modelos en cuanto a frameworks, como lo son *Tensorflow* y *Pytorch* asi como las  librerias *Numpy* y *Pandas*.

Su lista de recomendaciones fue más que nada intrucciones para sacar buenos apuntes. 

# Conclusiones generales
Todos los modelos recomendaron lo mismo como bases fundamentales para la materia, que de forma general seria: Saber *programación basica* en cualquier lenguaje y *Matematicas aplicadas* más especificamente algebra lineal y matematicas discretas. 

En la parte de recomendar un proyecto profesional, todos los modelos estuvieron de acuerdo en que un proyecto que involucre usar algun modelo o algoritmo para resolver un problema del mundo real como por ejemplo la documentación de archivos es la mejor practica. Aunque cada uno mencionaba modelos o aproximaciones distintas, como por ejemplo usar *Vision por Computadora* fue mencionado por mistral y gemma3, mientras que llama 3.2 fue el unico que hablo de implementar *Procesamiento de Lenguaje Natural.*

Me di cuenta que cree un prompt para que los modelos me dieran respuestas basadas en busquedas en la web, pero de los modelos que escogí ninguno tenia esa funcionalidad, por lo cual me respondieron en base al conocimiento con el cual fueron entrenados, y a decir verdad, las repsuestas fueron muy buenas y parecidas hasta cierto punto. 

