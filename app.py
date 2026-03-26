# ----- Library -----
from flask import Flask, render_template, request
import pickle
import numpy as np
import re
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)

model = load_model('translation_model.keras')
with open('en_tokenizer.pk', 'rb') as f:
    en_tokenizer = pickle.load(f)
with open('fr_tokenizer.pkl', 'rb') as f:
    fr_tokenizer = pickle.load(f)

max_len = 20

# ----- Preprocessing ------
def preprocess_sentence(word):
    word = word.lower().strip()
    # Adding spaces around punctuation
    word = re.sub(r"([?.!,])", r" \1 ", word)
    word = re.sub(r"\s+", " ", word)

    # Removing characters except a-z and basic punctuation
    word = re.sub(r"[^a-z?.!,]+", " ", word)
    return word.strip()

# ------ Translation Logic -----
def translate_logic(sentence):
    cleaned = preprocess_sentence(sentence)
    seq = en_tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=max_len, padding='post')
    prediction = model.predict(padded)
    
    translated_sentence = []
    # prediction[0] because we only sent one sentence
    for word_index in np.argmax(prediction[0], axis=-1):
        word = fr_tokenizer.index_word.get(word_index, '')
        if word == '<end>' or word == '':
            break
        if word != '<start>':
            translated_sentence.append(word)
    return " ".join(translated_sentence)


# ----- Routes -----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_route():
    user_text = request.form.get('text')
    if user_text:
        result = translate_logic(user_text)
    else:
        result = ""
    return render_template('index.html', translation=result, original=user_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)