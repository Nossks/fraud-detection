from flask import Flask, render_template, request, jsonify
import sys
import os
import traceback

# 1. Setup Path to find 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Import the Pipeline
# We try both names just in case you renamed the file
try:
    from src.pipeline.prediction import Prediction
except ImportError:
    try:
        from src.pipeline.prediction_pipeline import Prediction
    except ImportError:
        print("❌ CRITICAL ERROR: Could not find 'src/pipeline/prediction.py'")
        sys.exit(1)

from src.logger import logging

app = Flask(__name__)

# Global Pipeline Variable
pipeline = None

def initialize_pipeline():
    """Lazy loads the pipeline to ensure it's ready."""
    global pipeline
    if pipeline is None:
        print("⚡ FLASK: Initializing Prediction Pipeline...")
        try:
            pipeline = Prediction()
            print("✅ FLASK: Pipeline Ready.")
        except Exception as e:
            print("❌ FLASK INIT ERROR:")
            traceback.print_exc()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    # Ensure pipeline is loaded
    if pipeline is None:
        initialize_pipeline()
        
    try:
        user_input = request.form["msg"]
        
        # 1. Run Pipeline
        # Returns: (AIMessage_Object, dict_metrics)
        bot_reply_object, metrics = pipeline.predict(user_input)
        
        # --- THE FIX ---
        # LangChain returns an Object. Frontend needs a String.
        # We extract .content from the object.
        if hasattr(bot_reply_object, 'content'):
            bot_text = bot_reply_object.content
        else:
            # Fallback if it's already a string
            bot_text = str(bot_reply_object)

        # 2. Structure Data for Frontend
        response_data = {
            "response": bot_text, 
            "metrics": metrics 
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print("❌ FLASK RUNTIME ERROR:")
        traceback.print_exc()
        return jsonify({"response": "Internal Server Error. Check terminal logs.", "metrics": {}})

if __name__ == "__main__":
    # Initialize once on startup
    initialize_pipeline()
    print("Open in Browser: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)