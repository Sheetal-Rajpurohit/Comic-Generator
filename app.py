from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import google.generativeai as genai
import requests
import base64

app = Flask(__name__)
CORS(app)

# ======== DIRECT API KEYS ========

GEMINI_API_KEY = "YOUR-GEMINI-API-KEY"      # Replace with actual key
STABILITY_API_KEY = "YOUR-STABILITY-API-KEY" # Replace with actual key

# ==================================

# Configure APIs
genai.configure(api_key=GEMINI_API_KEY)
text_model = genai.GenerativeModel('gemini-2.0-flash-exp')

MUSIC_FILES = {
    "happy": "happy.mp3",
    "sad": "sad.mp3",
    "epic": "epic.mp3",
    "mysterious": "mysterious.mp3"
}

def generate_story(prompt):
    response = text_model.generate_content(
        f"Split this story into 4 concise comic captions (exactly 4, one per line) don't add the Okay, here are 4 concise comic captions for (prompt) part directly start the story points and dont add point numbers in story points: {prompt}"
    )
    return response.text.split("\n")[:4]

def determine_mood(story_parts):
    response = text_model.generate_content(
        f"Determine the mood (only respond with one word: happy/sad/epic/mysterious) of this story: {' '.join(story_parts)}"
    )
    return response.text.strip().lower()

def generate_image(prompt):
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = "https://api.stability.ai"
    
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {STABILITY_API_KEY}"
        },
        json={
            "text_prompts": [{"text": f" Split this story into 4 concise comic captions (exactly 4, one per line) don't add the Okay, here are 4 concise comic captions for (prompt) part directly start the story points and dont add point numbers in story points: {prompt}"}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Image generation failed")

    data = response.json()
    return data["artifacts"][0]["base64"]

@app.route('/generate-comic', methods=['POST'])
def generate_comic():
    data = request.get_json()
    try:
        story_parts = generate_story(data['prompt'])
        mood = determine_mood(story_parts)
        
        images = []
        for part in story_parts:
            base64_image = generate_image(part)
            img_data = f"data:image/png;base64,{base64_image}"
            images.append(img_data)
        
        return jsonify({
            "captions": story_parts,
            "images": images,
            "music": MUSIC_FILES.get(mood, "default.mp3")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/music/<path:filename>')
def serve_music(filename):
    return send_from_directory('static/music', filename)

if __name__ == '__main__':
    app.run(debug=True)