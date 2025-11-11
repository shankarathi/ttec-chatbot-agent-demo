import os
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import vertexai

# --- NEW IMPORTS ---
import threading
import queue
import asyncio

app = Flask(__name__)
CORS(app)

# --- Configuration (No Changes) ---
PROJECT_ID = os.environ.get("PROJECT_ID", "shankar-sandbox-gcp")
REASONING_ENGINE_ID = os.environ.get("REASONING_ENGINE_ID", "3098775610793656320")
REGION = os.environ.get("REGION", "us-west1")
AGENT_ENGINE_NAME = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{REASONING_ENGINE_ID}"
vertexai.init(project=PROJECT_ID, location=REGION)
client = vertexai.Client(project=PROJECT_ID, location=REGION)
# --- End Config ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        agent = client.agent_engines.get(name=AGENT_ENGINE_NAME)
        q = queue.Queue()
        new_user_id = "user-local-test-ttec"

        async def run_agent_query():
            """
            Runs the async Vertex AI query and puts results into the queue.
            """
            try:
                async for event in agent.async_stream_query(
                    message=user_message,
                    user_id=new_user_id
                ):
                    if 'content' in event and 'parts' in event['content']:
                        for part in event['content']['parts']:
                            if 'text' in part:
                                q.put(part['text'])
                                
            except Exception as e:
                # This is where your error message is coming from
                q.put(f"Sorry, I encountered an error: {e}")
            finally:
                q.put(None) # Signal the end

        # --- THIS FUNCTION IS THE ONLY CHANGE ---
        def start_async_loop():
            """
            Manually creates, sets, and runs the event loop in this thread.
            """
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_agent_query())
        # --- END OF CHANGE ---

        # Start the thread that will run the async code
        threading.Thread(target=start_async_loop).start()

        def generate_sync_chunks():
            """
            This sync generator pulls from the queue and yields to Flask.
            """
            while True:
                chunk = q.get()
                if chunk is None:
                    break
                yield chunk

        # Return the sync generator. Flask handles this perfectly.
        return Response(generate_sync_chunks(), mimetype='text/plain')

    except Exception as e:
        return jsonify({'error': f"Error calling Vertex AI Agent Engine: {e}"}), 500

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 8080)), debug=True, host='0.0.0.0')
