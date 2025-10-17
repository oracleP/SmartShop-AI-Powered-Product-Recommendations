from flask import Flask, request, render_template
import os
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------- Flask App Setup ----------------------
app = Flask(__name__)
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"

# ---------------------- Database Setup ----------------------


# ---------------------- Project Paths ----------------------

# ---------------------- Load CSV Files ----------------------

trending_products = pd.read_csv("models/trending_products.csv")
train_data = pd.read_csv("models/clean_data.csv")

# ---------------------- Database Models ----------------------

# ---------------------- Utility Functions ----------------------
def truncate(text, length):
    """Truncate text to a certain length."""
    return text[:length] + "..." if len(text) > length else text

def content_based_recommendations(train_data, item_name, top_n=10):
    """Return top N similar items based on Tags column using TF-IDF."""
    if item_name not in train_data['Name'].values:
        return pd.DataFrame()  # item not found

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(train_data['Tags'])
    cosine_similarities_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)
    item_index = train_data[train_data['Name'] == item_name].index[0]

    similar_items = list(enumerate(cosine_similarities_content[item_index]))
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)
    top_similar_items = similar_items[1:top_n+1]

    recommended_item_indices = [x[0] for x in top_similar_items]
    return train_data.iloc[recommended_item_indices][['Name', 'ReviewCount', 'Brand', 'ImageURL', 'Rating']]

# ---------------------- Random Images & Prices ----------------------
random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]
random_prices = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]

# ---------------------- Routes ----------------------
@app.route("/")
@app.route("/index")
def index():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    return render_template(
        "index.html",
        trending_products=trending_products.head(8),
        truncate=truncate,
        random_product_image_urls=random_product_image_urls,
        random_price=random.choice(random_prices)
    )

@app.route("/main")
def main():
    return render_template("main.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_signup = Signup(username=username, email=email, password=password)
        db.session.add(new_signup)
        db.session.commit()

        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        return render_template(
            'index.html',
            trending_products=trending_products.head(8),
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_price=random.choice(random_prices),
            signup_message='User signed up successfully!'
        )

@app.route("/signin", methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']

        new_signin = Signin(username=username, password=password)
        db.session.add(new_signin)
        db.session.commit()

        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        return render_template(
            'index.html',
            trending_products=trending_products.head(8),
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_price=random.choice(random_prices),
            signup_message='User signed in successfully!'
        )

@app.route("/recommendations", methods=['POST', 'GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('prod')
        nbr = int(request.form.get('nbr', 10))  # default 10
        content_based_rec = content_based_recommendations(train_data, prod, top_n=nbr)

        if content_based_rec.empty:
            message = "No recommendations available for this product."
            return render_template('main.html', message=message)

        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(content_based_rec))]
        return render_template(
            'main.html',
            content_based_rec=content_based_rec,
            truncate=truncate,
            random_product_image_urls=random_product_image_urls,
            random_price=random.choice(random_prices)
        )

# ---------------------- Run App ----------------------
if __name__ == "__main__":
    app.run(debug=True)
