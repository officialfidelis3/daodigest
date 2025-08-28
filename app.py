import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from snapshot_api import fetch_dao_proposals
from ai_service import generate_proposal_summary

# Configure logging for development and production
log_level = logging.DEBUG if os.environ.get('FLASK_ENV') == 'development' else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Custom Jinja2 filter for datetime formatting
def datetime_filter(timestamp):
    """Convert Unix timestamp to readable date"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%b %d, %Y')
    except (ValueError, TypeError):
        return "Unknown date"

app.jinja_env.filters['datetime'] = datetime_filter

# Render deployment configuration
if __name__ != '__main__':
    # Production configuration for Render
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route('/')
def index():
    """Homepage with DAO name input form"""
    return render_template('index.html')

@app.route('/proposals', methods=['POST'])
def proposals():
    """Fetch and display proposals for a given DAO"""
    dao_name = request.form.get('dao_name', '').strip()
    
    if not dao_name:
        flash('Please enter a DAO name', 'error')
        return redirect(url_for('index'))
    
    try:
        # Fetch proposals from Snapshot API
        proposals_data = fetch_dao_proposals(dao_name)
        
        if not proposals_data or not proposals_data.get('proposals'):
            flash(f'No proposals found for DAO: {dao_name}', 'warning')
            return render_template('proposals.html', dao_name=dao_name, proposals=[])
        
        proposals = proposals_data['proposals']
        
        # Generate AI summaries for each proposal with robust error handling
        for proposal in proposals:
            try:
                if proposal.get('body') and len(proposal['body'].strip()) > 20:
                    summary = generate_proposal_summary(
                        proposal['title'], 
                        proposal['body']
                    )
                    proposal['ai_summary'] = summary
                else:
                    proposal['ai_summary'] = f"Summary: {proposal['title']}. This governance proposal has limited description available."
            except Exception as e:
                logging.warning(f"Summary generation failed for proposal {proposal.get('id', 'unknown')}: {str(e)[:50]}")
                # Always provide a useful fallback
                description = proposal.get('body', '').strip()
                if description and len(description) > 30:
                    fallback = f"Summary: {proposal['title']}. {description[:120]}..."
                else:
                    fallback = f"Summary: {proposal['title']}. This is a governance proposal for the DAO."
                proposal['ai_summary'] = fallback
        
        return render_template('proposals.html', dao_name=dao_name, proposals=proposals)
        
    except Exception as e:
        logging.error(f"Error fetching proposals for {dao_name}: {e}")
        flash(f'Error fetching proposals for {dao_name}: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/proposals')
def api_proposals():
    """JSON API endpoint for proposals"""
    dao_name = request.args.get('dao', '').strip()
    
    if not dao_name:
        return jsonify({'error': 'DAO name parameter is required'}), 400
    
    try:
        # Fetch proposals from Snapshot API
        proposals_data = fetch_dao_proposals(dao_name)
        
        if not proposals_data or not proposals_data.get('proposals'):
            return jsonify({
                'dao_name': dao_name,
                'proposals': [],
                'message': f'No proposals found for DAO: {dao_name}'
            })
        
        proposals = proposals_data['proposals']
        
        # Generate AI summaries for each proposal with robust error handling
        for proposal in proposals:
            try:
                if proposal.get('body') and len(proposal['body'].strip()) > 20:
                    summary = generate_proposal_summary(
                        proposal['title'], 
                        proposal['body']
                    )
                    proposal['ai_summary'] = summary
                else:
                    proposal['ai_summary'] = f"Summary: {proposal['title']}. This governance proposal has limited description available."
            except Exception as e:
                logging.warning(f"API summary generation failed for proposal {proposal.get('id', 'unknown')}: {str(e)[:50]}")
                # Always provide a useful fallback
                description = proposal.get('body', '').strip()
                if description and len(description) > 30:
                    fallback = f"Summary: {proposal['title']}. {description[:120]}..."
                else:
                    fallback = f"Summary: {proposal['title']}. This is a governance proposal for the DAO."
                proposal['ai_summary'] = fallback
        
        return jsonify({
            'dao_name': dao_name,
            'proposals': proposals,
            'count': len(proposals)
        })
        
    except Exception as e:
        logging.error(f"API error fetching proposals for {dao_name}: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    # For web requests, redirect to home with error message
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    else:
        flash('An internal error occurred. Please try again.', 'error')
        return render_template('index.html'), 500

if __name__ == '__main__':
    # Use PORT environment variable for deployment platforms like Render
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
