from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Global items data (10 items as requested)
ITEMS = [
    {"id": 1, "title": "Python Programming Guide", "description": "Learn Python programming from basics to advanced concepts"},
    {"id": 2, "title": "Web Development Tutorial", "description": "Complete guide to building modern web applications"},
    {"id": 3, "title": "Machine Learning Basics", "description": "Introduction to machine learning algorithms and techniques"},
    {"id": 4, "title": "Data Science Handbook", "description": "Essential tools and techniques for data analysis"},
    {"id": 5, "title": "JavaScript Fundamentals", "description": "Master JavaScript programming language"},
    {"id": 6, "title": "Database Design Principles", "description": "Learn how to design efficient database schemas"},
    {"id": 7, "title": "API Development Guide", "description": "Build RESTful APIs with best practices"},
    {"id": 8, "title": "Mobile App Development", "description": "Create mobile applications for iOS and Android"},
    {"id": 9, "title": "Cloud Computing Overview", "description": "Understanding cloud platforms and services"},
    {"id": 10, "title": "Cybersecurity Essentials", "description": "Protect your applications from security threats"}
]

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """
    Search endpoint that filters items based on keywords in their title.
    Accepts 'query' and 'keywords' parameters.
    """
    try:
        # Get parameters from request
        if request.method == 'GET':
            query = request.args.get('query', '')
            keywords = request.args.get('keywords', '')
        else:  # POST
            data = request.get_json() or {}
            query = data.get('query', '')
            keywords = data.get('keywords', '')
        
        # Combine query and keywords for search
        search_terms = f"{query} {keywords}".strip().lower()
        
        if not search_terms:
            return jsonify({"items": []})
        
        # Filter items where title contains any of the search terms
        search_words = search_terms.split()
        filtered_items = []
        
        for item in ITEMS:
            title_lower = item["title"].lower()
            # Check if any search word is in the title
            if any(word in title_lower for word in search_words):
                res = item
                res["checkout_url"] = f"https://checkout.stripe.com/c/pay/{item['id']}"
                filtered_items.append(res)
        
        return jsonify({"items": filtered_items})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    print("Starting Simple Search Server...")
    print("  GET/POST /api/search - Search items")
    app.run(debug=True, host='0.0.0.0', port=5000)
