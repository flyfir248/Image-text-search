from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, render_template, request
import re
import requests

# ------------------------------
## google api
from googleapiclient.discovery import build
import urllib.request
import os

api_key = "--------------"
cx = "--------------"

service = build("customsearch", "v1", developerKey=api_key)
# --------------------------------

endpoint = "http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    director = request.form['query']  # enter director name

    director = '_'.join(director.split()).title()  # if wrong format is entered then a correct format is added

    query = """
    SELECT DISTINCT ?movie WHERE {
      ?movie rdf:type dbo:Film .
      ?movie dbo:director dbr:""" + director + """ .
    }
    """
    resultlist = list()  # empty list to store movie names unclean
    resultlistnew = []  # new list for cleaned texts

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        movie = result["movie"]["value"]
        print(movie)

        tmp = str(movie)  # convert to string to add to list
        tmp1 = tmp.split('/')[-1]
        resultlist.append(tmp1)

    for text in resultlist:
        # Replace underscores with spaces
        text = text.replace('_', ' ')

        # Remove parentheses and their contents
        text = re.sub(r'\([^)]*\)', '', text)

        # Remove non-alphanumeric characters except spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

        # Print the cleaned text
        # print(text)

        resultlistnew.append(text)

    return render_template('search_results.html', query=director, results=resultlistnew)

@app.route('/searchimage', methods=['POST'])
def search_image():
    # Get the query image description
    query = request.form['query']

    # Fetch the images from Google Custom Search API
    link_image = fetch_images(query)

    # Download and save the images locally
    image_paths = get_images(link_image)

    # Render the results page with the image paths
    return render_template('results.html', image_paths=image_paths)

def get_images(link_image):
    # List to hold the image paths
    image_paths = []

    # Loop through the image URLs
    for i, url in enumerate(link_image):
        # Make a GET request to the image URL
        response = requests.get(url)

        # Save the image locally
        with open(f'static/image{i+1}.jpg', 'wb') as f:
            f.write(response.content)

        # Append the image path to the list
        image_paths.append(f'static/image{i+1}.jpg')

    return image_paths

def fetch_images(original_string):
    link_image = []

    words = original_string.split()
    new_string = '+'.join(words)

    url = f'https://customsearch.googleapis.com/customsearch/v1?q={new_string}&cx=511c17a6333064baa&searchType=image&key=AIzaSyByNyz_xPqUxE5rshTel0uzdAZL_0Lttr8&alt=json'

    response = requests.get(url)
    data = response.json()

    for i in range(10):
        link_image.append(data['items'][i]['link'])

    return link_image



if __name__ == '__main__':
    app.run()

