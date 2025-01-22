from flask import Flask, request, jsonify, send_file
from automateAd import AdAutomation
from recs import Similar_Users
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"


@app.route('/automate_ad', methods=['POST'])
def automate_ad():
    data = request.get_json()
    
    # Check if user_id is provided in the request
    if 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400
    
    user_id = data['user_id']
    device_type = data.get('device_type', 'mobile')
    
    try:
        # Initialize AdAutomation
        ad_automation = AdAutomation()
        
        # Get ad recommendations
        ad_rec = Similar_Users().recommend_ads(user_id, device_type)
        
        # Generate ad text
        ad_text = ad_automation.automate_ad(ad_rec, user_id)
        
        # Generate audio file
        audio_file_path = ad_automation.text_to_speech(ad_text, user_id)
        
        return send_file(
            audio_file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f'ad_{user_id}.mp3'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500






if __name__ == '__main__':
    app.run(debug=True)