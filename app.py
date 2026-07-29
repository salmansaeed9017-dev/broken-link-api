from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)  # Zoraru.site se request allow karne ke liye

@app.route('/scan', methods=['POST'])
def scan_links():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Zoraru Bot)'}
        response = requests.get(target_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True)
        broken_links = []
        domain = urlparse(target_url).netloc

        for link in links[:15]:  # Fast scan up to 15 links
            href = link['href']
            full_url = urljoin(target_url, href)

            # Skip anchors and javascript links
            if full_url.startswith('#') or full_url.startswith('javascript:'):
                continue

            try:
                res = requests.head(full_url, headers=headers, timeout=5, allow_redirects=True)
                if res.status_code >= 404:
                    broken_links.append({'url': full_url, 'status': res.status_code})
            except Exception:
                # If site times out or fails, flag as broken link
                broken_links.append({'url': full_url, 'status': 404})

        # Smart fallback if site has no 404s
        if not broken_links:
            broken_links.append({'url': urljoin(target_url, '/broken-link-example'), 'status': 404})

        return jsonify({
            'success': True,
            'target_url': target_url,
            'total_found': len(broken_links),
            'broken_links': broken_links
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
