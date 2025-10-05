from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection settings
MONGODB_URI = os.environ.get('MONGODB_URI')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'tlb_kitchen_website')

# Lazy initialization of MongoDB client
_client = None
_db = None

def get_db():
    """Get database connection with lazy initialization"""
    global _client, _db
    
    if _db is None:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI environment variable is not set. Please create a .env file with your MongoDB connection string.")
        
        if MONGODB_URI == 'mongodb+srv://<username>:<password>@cluster.mongodb.net/':
            raise ValueError("Please update MONGODB_URI in your .env file with your actual MongoDB connection string.")
        
        try:
            _client = MongoClient(MONGODB_URI)
            # Test the connection
            _client.admin.command('ping')
            _db = _client[DATABASE_NAME]
            print(f"Successfully connected to MongoDB database: {DATABASE_NAME}")
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    return _db

def parse_json(data):
    """Convert MongoDB documents to JSON"""
    return json.loads(json_util.dumps(data))

@app.route('/')
def home():
    return jsonify({
        "message": "TLB Kitchen Custom Orders API",
        "status": "running",
        "endpoints": [
            "/api/categories",
            "/api/find",
            "/api/findOne",
            "/api/aggregate"
        ]
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories from custom-orders collection"""
    try:
        db = get_db()
        collection = db['custom-orders']
        result = collection.find_one({"spec_id": "categories"})
        
        if result:
            return jsonify({
                "document": parse_json(result)
            })
        else:
            return jsonify({"document": None}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/findOne', methods=['POST'])
def find_one():
    """Find a single document based on filter"""
    try:
        db = get_db()
        data = request.get_json()
        collection_name = data.get('collection', 'custom-orders')
        filter_query = data.get('filter', {})
        
        collection = db[collection_name]
        result = collection.find_one(filter_query)
        
        if result:
            return jsonify({
                "document": parse_json(result)
            })
        else:
            return jsonify({"document": None}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/find', methods=['POST'])
def find():
    """Find multiple documents based on filter"""
    try:
        db = get_db()
        data = request.get_json()
        collection_name = data.get('collection', 'custom-orders')
        filter_query = data.get('filter', {})
        limit = data.get('limit', 0)
        skip = data.get('skip', 0)
        sort = data.get('sort')
        
        collection = db[collection_name]
        cursor = collection.find(filter_query)
        
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        results = list(cursor)
        
        return jsonify({
            "documents": parse_json(results)
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregate', methods=['POST'])
def aggregate():
    """Perform aggregation pipeline (for search functionality)"""
    try:
        db = get_db()
        data = request.get_json()
        collection_name = data.get('collection', 'custom-orders')
        pipeline = data.get('pipeline', [])
        
        collection = db[collection_name]
        
        # Check if this is a search query
        if pipeline and len(pipeline) > 0 and '$search' in pipeline[0]:
            # Extract search parameters
            search_stage = pipeline[0]['$search']
            
            if 'autocomplete' in search_stage:
                query = search_stage['autocomplete']['query']
                path = search_stage['autocomplete']['path']
                
                # Use regex search as a fallback for MongoDB Atlas Search
                # This works with standard MongoDB without Atlas Search index
                filter_query = {
                    path: {"$regex": query, "$options": "i"}
                }
                
                results = list(collection.find(filter_query).limit(24))
            elif 'text' in search_stage:
                query = search_stage['text']['query']
                path = search_stage['text']['path']
                
                filter_query = {
                    path: {"$regex": query, "$options": "i"}
                }
                
                results = list(collection.find(filter_query).limit(24))
            else:
                # Fallback: try to run the pipeline as-is
                results = list(collection.aggregate(pipeline))
        else:
            # Run the pipeline as-is
            results = list(collection.aggregate(pipeline))
        
        return jsonify({
            "documents": parse_json(results)
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/count', methods=['POST'])
def count():
    """Count documents based on filter"""
    try:
        db = get_db()
        data = request.get_json()
        collection_name = data.get('collection', 'custom-orders')
        filter_query = data.get('filter', {})
        
        collection = db[collection_name]
        count = collection.count_documents(filter_query)
        
        return jsonify({
            "count": count
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint for Render
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Ping the database to check connection
        db = get_db()
        _client.admin.command('ping')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
