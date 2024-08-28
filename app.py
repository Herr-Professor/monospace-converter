from flask import Flask, request, render_template_string, send_from_directory
import requests
from bs4 import BeautifulSoup
import markdown
import os

app = Flask(__name__, static_folder='.')

def fetch_content(url):
    response = requests.get(url)
    return response.text

def parse_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else "Untitled"
    
    main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    markdown_content = ""
    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'img', 'pre', 'code']):
        if element.name.startswith('h'):
            markdown_content += f"{'#' * int(element.name[1:])} {element.text.strip()}\n\n"
        elif element.name == 'p':
            markdown_content += f"{element.text.strip()}\n\n"
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                markdown_content += f"- {li.text.strip()}\n"
            markdown_content += "\n"
        elif element.name == 'img':
            markdown_content += f"![{element.get('alt', '')}]({element.get('src', '')})\n\n"
        elif element.name == 'pre':
            markdown_content += f"```\n{element.text.strip()}\n```\n\n"
        elif element.name == 'code':
            markdown_content += f"`{element.text.strip()}`"
    
    return title, markdown_content

def generate_html(title, content, url):
    html_content = markdown.markdown(content)
    
    with open('template.html', 'r') as f:
        template = f.read()
    
    return template.replace('$title$', title).replace('$body$', html_content).replace('$source_url$', url)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form['url']
    html = fetch_content(url)
    title, content = parse_content(html)
    result_html = generate_html(title, content, url)
    return result_html

if __name__ == "__main__":
    app.run(debug=True)
