from flask import Flask, request, jsonify
import re
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
import string

# Download required resources
nltk.download('stopwords')
nltk.download('punkt')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)  # Fix proxy settings

stop_words = set(stopwords.words('english')) - {"not", "be", "is", "are", "was", "were"}  # Preserve key negations

# Define redundant words properly
redundant_words = {"some", "unnecessary", "example"}  # Add actual words here

def shorten_headline(headline):
    words = nltk.word_tokenize(headline.lower())
    filtered_words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words]
    filtered_words = [word for word in filtered_words if word and word not in stop_words and word not in redundant_words]
    
    # Preserve key terms related to legal matters
    important_terms = {"rape", "charge", "judge", "court", "accused", "minor offence", "assault", "abuse"}
    preserved_words = [word for word in words if word in important_terms or word in filtered_words]
    
    # Remove duplicate words while maintaining order
    unique_words = list(dict.fromkeys(preserved_words))
    
    if unique_words:
        unique_words[0] = unique_words[0].capitalize()
    
    return " ".join(unique_words)

@app.route('/shorten', methods=['POST'])
def process_news_headlines():
    data = request.get_json()
    if not data or 'headlines' not in data:
        return jsonify({"error": "Invalid request. Please provide 'headlines' as a list."}), 400
    
    headlines = data['headlines']
    shortened_headlines = [shorten_headline(headline) for headline in headlines]
    return jsonify({"shortened_headlines": shortened_headlines})

if __name__ == "__main__":
    app.run(debug=True)
