from flask import Flask, render_template, request, jsonify
from deepface import DeepFace
import base64
import io
from PIL import Image
from datetime import datetime
import yagmail
from tabulate import tabulate
import time

app = Flask(__name__)

# empty list to store dominant_emotion values
dominant_emotions_list = []

@app.route('/api/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    
    # remove 'data:image/jpeg;base64,' from the base64 string
    data = request.get_json()
    image_data = data['image'].split(',')[1]  
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    # saving the image temporarily
    image_path = "temp_image.jpeg"
    image.save(image_path)

    # analyzing using the Deepfake library
    face_analysis = DeepFace.analyze(img_path=image_path)
    dominant_emotion = face_analysis[0]['dominant_emotion']

    # Append the dominant_emotion to the list, along with the current timestamp
    object_to_send = {}
    object_to_send["time"] = datetime.now()
    object_to_send["dominant_emotion"] = dominant_emotion

    dominant_emotions_list.append(object_to_send)

    return jsonify({'dominant_emotion': dominant_emotion})


def send_email(emotions_list):
    
     # Use the App Password generated from your Google Account
    sender_email = ""
    receiver_email = ""
    password = "" 

    # Convert list of dictionaries into a table
    table = tabulate(emotions_list, headers="keys", tablefmt="grid")

    # Initialize yagmail SMTP connection
    yag = yagmail.SMTP(sender_email, password)
    yag.send(
        to=receiver_email,
        subject="Dominant Emotions List",
        contents=table
    )


# Email the report when the End Session button is clicked
# Clear the list once a report is sent

@app.route('/api/end_session', methods=['POST'])
def end_session():
    send_email(dominant_emotions_list)
    dominant_emotions_list.clear()
    return "Session ended successfully!"

if __name__ == '__main__':
    app.run(debug=True)
