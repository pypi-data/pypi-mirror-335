from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Ensure the template directory exists
template_dir = Path(__file__).parent / 'templates'
static_dir = Path(__file__).parent / 'static'

if not template_dir.exists():
    logger.error(f"Template directory not found at {template_dir}")
    raise FileNotFoundError(f"Template directory not found at {template_dir}")

if not static_dir.exists():
    logger.error(f"Static directory not found at {static_dir}")
    raise FileNotFoundError(f"Static directory not found at {static_dir}")

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/blog-posts')
def get_blog_posts():
    try:
        # Sample blog posts for preview
        posts = [
            {
                'title': 'The Future of Digital Marketing',
                'date': datetime.now().isoformat(),
                'excerpt': 'Exploring the latest trends and technologies shaping the future of digital marketing...',
                'source': 'Blog',
                'url': '#'
            },
            {
                'title': 'SEO Best Practices 2024',
                'date': datetime.now().isoformat(),
                'excerpt': 'Learn the essential SEO strategies that will help your website rank higher in 2024...',
                'source': 'Blog',
                'url': '#'
            },
            {
                'title': 'Content Marketing Strategies',
                'date': datetime.now().isoformat(),
                'excerpt': 'Discover effective content marketing strategies to engage your audience and drive results...',
                'source': 'Blog',
                'url': '#'
            }
        ]
        return jsonify(posts)
    except Exception as e:
        logger.error(f"Error fetching blog posts: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        logger.info(f"Received contact form data: {data}")
        return jsonify({"message": "Message received successfully"})
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

def main():
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == '__main__':
    main() 