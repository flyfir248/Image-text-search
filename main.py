from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import re
import requests

# ------------------------------
## google api
from googleapiclient.discovery import build
import urllib.request
import os

api_key = "----------------------------------"
cx = "-------------------------"

service = build("customsearch", "v1", developerKey=api_key)
# --------------------------------

endpoint = "http://dbpedia.org/sparql"
sparql = SPARQLWrapper(endpoint)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/searchimage', methods=['POST'])   # this works
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


@app.route('/abstract', methods=['POST'])
def abstract():
    input_text = request.form['input_text']

    input_text = '_'.join(input_text.split()).title()  # if wrong format is entered then a correct format is added

    input_text= input_text.replace(';', '. ')

    dbpedia_url = f"http://dbpedia.org/sparql"
    sparql_query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        SELECT ?abstract
        WHERE {{
            <http://dbpedia.org/resource/{input_text}> dbo:abstract ?abstract .
            FILTER langMatches(lang(?abstract),"en")
        }}
    """
    response = requests.get(dbpedia_url, params={'query': sparql_query})
    soup = BeautifulSoup(response.text, 'html.parser')
    abstracts = [str(a) for a in soup.find_all('literal')]
    #print(abstracts)
    sentence = abstracts[0].split('>')[1]
    val = sentence.split('<')[0]



    return render_template('abstracts.html', abstracts=val)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

