from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Zaroru.site Engine Online!"

@app.route('/scan', methods=['POST'])
def scan_website():
    data = request.json
    website_url = data.get('url')
    
    if not website_url:
        return jsonify({'error': 'URL is required'}), 400

    broken_links = []
    try:
        response = requests.get(website_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        for link in links[:15]:
            url = link['href']
            full_url = urljoin(website_url, url)
            
            if full_url.startswith('http'):
                try:
                    check = requests.head(full_url, timeout=4, allow_redirects=True)
                    if check.status_code >= 400:
                        broken_links.append({
                            'link': full_url,
                            'anchor_text': link.text.strip() or "Click Here",
                            'status': check.status_code
                        })
                except:
                    broken_links.append({
                        'link': full_url,
                        'anchor_text': link.text.strip() or "Click Here",
                        'status': 'Failed'
                    })
                    
        return jsonify({
            'success': True,
            'total_scanned': len(links),
            'broken_links': broken_links
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
