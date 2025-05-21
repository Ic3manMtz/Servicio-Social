# Cosas por hacer para el procesamiento de videos

+ Creación de una aplicación de escritorio para procesar los videos.

    + Convertir video a frames
    + Selección de un modelo para el análisis
        - YOLOv8x (el más preciso de la familia YOLO, aunque más lento).
        - Faster R-CNN con ResNet-101 (excelente para detección de personas).
        - Mask R-CNN si necesitas segmentación de personas (útil para grupos densos).
    + Detección de personas y de grupos de personas
        - Usar las coordenadas de las bounding boxes de personas detectadas.
        - Calcular la proximidad entre ellas (ej: distancia entre centros).
        - Aplicar un algoritmo de clustering para definir grupos.
    + Análisis de resultados y generación de reportes
    + Reconstrucción del video procesado
    