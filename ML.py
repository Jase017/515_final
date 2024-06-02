import pyrebase
import joblib
import numpy as np

# 加载模型
model = joblib.load('model_filename.pkl')

def preprocess(data):
    # 假设数据已经预处理，这里直接提取特征值
    features = [data['Heart Rate']]
    return features

def predict(data):
    processed_data = preprocess(data)
    prediction = model.predict([processed_data])
    return prediction

def stream_handler(message):
    print("Message received:", message)
    # 监听根路径事件
    if message['event'] == 'put' and message['path'] == '/':
        data = message['data']
        if data:  # 确保数据不为空
            prediction = predict(data)
            print('Prediction:', prediction)
            upload_prediction(prediction)

def upload_prediction(prediction):
    db = firebase.database()
    result_ref = db.child('predictions')  # 简化后的上传路径
    result_ref.set({'prediction': prediction[0]})
    print('Prediction uploaded:', prediction[0])

def main():
    global firebase
    config = {
        "apiKey": "AIzaSyCc5UcrsiyYfwE2gnfK_yHRYg1dtl7cF8",
        "authDomain": "pawsitude-2bab7.firebaseapp.com",
        "databaseURL": "https://pawsitude-2bab7-default-rtdb.firebaseio.com",
        "storageBucket": "pawsitude-2bab7.appspot.com"
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    my_stream = db.child("heart_rate_data").stream(stream_handler)

if __name__ == '__main__':
    main()
