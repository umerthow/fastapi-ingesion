from flask import Flask, jsonify, request
import json
import os
from pathlib import Path

app = Flask(__name__)

# Load customers data from JSON file
def load_customers():
    """Load customer data from the JSON file."""
    json_path = Path(__file__).parent / 'data' / 'customers.json'
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: customers.json not found at {json_path}")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in customers.json")
        return []

# Load data once at startup
CUSTOMERS = load_customers()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Mock Server',
        'customers_loaded': len(CUSTOMERS)
    }), 200

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """
    Get paginated list of customers.
    Query parameters:
    - page: Page number (default: 1)
    - limit: Number of items per page (default: 10)
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        # Validate parameters
        if page < 1:
            return jsonify({'error': 'Page must be >= 1'}), 400
        if limit < 1 or limit > 100:
            return jsonify({'error': 'Limit must be between 1 and 100'}), 400
        
        # Calculate pagination
        total_customers = len(CUSTOMERS)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get paginated data
        paginated_customers = CUSTOMERS[start_idx:end_idx]
        
        # Calculate total pages
        total_pages = (total_customers + limit - 1) // limit
        
        # Return paginated response
        return jsonify({
            'data': paginated_customers,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_items': total_customers,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    """
    Get a single customer by ID.
    Returns 404 if customer not found.
    """
    try:
        # Find customer by ID
        customer = next((c for c in CUSTOMERS if c['customer_id'] == customer_id), None)
        
        if customer is None:
            return jsonify({'error': f'Customer with ID {customer_id} not found'}), 404
        
        return jsonify(customer), 200
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if not CUSTOMERS:
        print("Warning: No customers loaded. Check data/customers.json")
    else:
        print(f"Loaded {len(CUSTOMERS)} customers")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
