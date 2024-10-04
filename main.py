import tempfile
import os
from flask import Flask, request, redirect, send_file, render_template
from tensorflow.keras.models import load_model
from io import BytesIO
from skimage import io
import base64
import glob
import numpy as np
from PIL import Image
from skimage.transform import resize
import base64
import numpy as np

model = load_model('modelo.h5')
app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        img_data = request.form.get('myImage').replace("data:image/png;base64,", "")
        shape = request.form.get('shape')
        integrante = request.form.get('integrante')  # Nuevo campo
        print("Dibujando un", shape, "por", integrante)

        # Crear el directorio si no existe
        directory = os.path.join(str(shape), integrante)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Guardar la imagen en la ruta con las dos etiquetas
        with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix='.png', dir=directory) as fh:
            fh.write(base64.b64decode(img_data))
        print("Imagen subida")
    except Exception as err:
        print("Error ocurrido")
        print(err)

    return redirect("/", code=302)


@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    images = []
    labels_shape = []
    labels_integrante = []
    shapes = {"flor": "flor", "casa": "casa", "auto": "auto"}
    integrantes = ["integrante1", "integrante2", "integrante3"]

    for shape in shapes.keys():
        for integrante in integrantes:
            folder_path = os.path.join(shape, integrante)
            filelist = glob.glob(f'{folder_path}/*.png')
            if filelist:
                images_read = io.concatenate_images(io.imread_collection(filelist))
                images_read = images_read[:, :, :, 3]  # Usa solo el canal alfa si es necesario
                labels_shape.extend([shape] * images_read.shape[0])
                labels_integrante.extend([integrante] * images_read.shape[0])
                images.append(images_read)

    images = np.vstack(images)
    labels_shape = np.array(labels_shape)
    labels_integrante = np.array(labels_integrante)
    np.save('X.npy', images)
    np.save('y_shape.npy', labels_shape)
    np.save('y_integrante.npy', labels_integrante)
    return "Dataset preparado con éxito"




@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')

@app.route('/y.npy', methods=['GET'])
def download_y():
    return send_file('./y.npy')
# 0 circulo , 1 triangulo, 2 cuadrado

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        img_binary = base64.b64decode(img_data)

        # Convert binary data to PIL image
        image = Image.open(BytesIO(img_binary))

        # Keep the image in RGBA format
        img_rgba = np.array(image)

        # Resize the image
        img_resized = np.array(resize(img_rgba, (28, 28)))

        # Extract the alpha channel and convert the image data to 8-bit integer format
        img_resized = (img_resized[:, :, 3] * 255).astype(np.uint8)

        # Normalize the image data
        img_resized = img_resized.astype('float32') / 255.0

        # Reshape the array
        img_array = img_resized.reshape(1, 28, 28)

        # Add an extra dimension if needed
        if img_array.ndim == 3:
            img_array = img_array[..., None]

        # Realizar la predicción
        prediction_shape, prediction_integrante = model.predict(img_array)

        # Etiquetas para las predicciones
        etiquetas_shape = {0: 'flor', 1: 'auto', 2: 'casa'}
        etiquetas_integrante = {0: 'integrante1', 1: 'integrante2', 2: 'integrante3'}

        # Obtener los valores de la predicción
        valor_shape = np.argmax(prediction_shape)
        valor_integrante = np.argmax(prediction_integrante)

        # Definir los resultados
        kind = etiquetas_shape.get(valor_shape, "Desconocido")
        integrante = etiquetas_integrante.get(valor_integrante, "Desconocido")

        # Retornar la predicción al frontend
        return render_template('predict.html', value=f"Dibujo: {kind}, Integrante: {integrante}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('predict.html', value="Error en la predicción")

if __name__ == "__main__":
    shapes = ['flor', 'casa', 'auto']  # Cambiado a los nombres de las formas
    integrantes = ['integrante1', 'integrante2', 'integrante3']
    
    # Crear las carpetas de forma y sus subcarpetas de integrantes
    for shape in shapes:
        if not os.path.exists(shape):
            os.mkdir(shape)
        for integrante in integrantes:
            path = os.path.join(shape, integrante)
            if not os.path.exists(path):
                os.mkdir(path)
    
    app.run()
