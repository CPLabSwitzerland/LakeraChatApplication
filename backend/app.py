from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, stream_with_context, Response, session
from llm.llm_tinyllama import LLM
from lakera.lakera import screen_with_lakera
from utils.logger_setup import getlogger
import uuid
import time
import os

# Load environment variables
load_dotenv()

# Initialize logger for the Flask app
logger = getlogger("app")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# --- In-memory session-specific chat histories ---
CHAT_SESSIONS = {}  # { session_id: [ {role, content}, ... ] }

# Initialize LLM
llm = LLM()


# -------------------------------------------------
# Assign a unique session_id to each user automatically
# -------------------------------------------------
@app.before_request
def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())


def get_user_messages():
    sid = session["session_id"]
    if sid not in CHAT_SESSIONS:
        CHAT_SESSIONS[sid] = []
    return CHAT_SESSIONS[sid]


# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/")
def index():
    """Main page route."""
    user_messages = get_user_messages()
    return render_template("app.html", messages=user_messages)


@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    """Clear the chat history for THIS USER ONLY."""
    sid = session["session_id"]
    CHAT_SESSIONS[sid] = []

    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logger.info(f"User with {user_ip} cleared their own chat history")

    return jsonify({"status": "cleared"})


@app.route("/send_message", methods=["POST"])
def send_message():
    """
    Send user message through Lakera input screening,
    then to the LLM, then Lakera output screening.
    Streaming output preserved. User session isolation added.
    """
    user_messages = get_user_messages()
    data = request.json
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"status": "empty"})

    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_messages.append({"role": "user", "content": prompt})
    logger.info(f"User message from {user_ip}: {prompt}")

    # --- Lakera user input screening ---
    logger.info("User message screening by Lakera")
    try:
        lakera_result = screen_with_lakera(prompt)
        flagged = lakera_result.get("flagged", False)
        if flagged:
            logger.warning("Lakera flagged this user message as harmful!")
            blocked_message = (
                "Lakera Guard identified a threat. No user was harmed by this LLM. "
                "Your message has been flagged and was not processed."
            )
            user_messages.append({"role": "assistant", "content": blocked_message})

            def generate_blocked():
                yield blocked_message

            return Response(stream_with_context(generate_blocked()), mimetype="text/plain")

    except Exception as e:
        logger.error(f"Lakera screening failed: {e}")
        flagged = False  # allow LLM if Lakera fails

    # --- LLM streaming + Lakera output check ---
    def generate():
        response_text = ""
        for chunk in llm.stream(prompt):
            response_text += chunk

        # --- Lakera output screening ---
        logger.info("[lakera] Checking LLM output...")
        try:
            output_result = screen_with_lakera(prompt, output_text=response_text)

            if output_result.get("flagged", False):
                logger.warning("Lakera flagged the LLM output!")
                blocked_message = "Lakera Guard blocked harmful LLM output. No user was harmed."

                user_messages.append({"role": "assistant", "content": blocked_message})
                # Log final assistant response
                logger.info(f"Assistant response (blocked): {blocked_message}")
                yield blocked_message

            else:
                # Approved output: mimic streaming
                user_messages.append({"role": "assistant", "content": response_text})
                logger.info("Lakera approved LLM answer.")
                # Log final assistant response
                logger.info(f"Assistant response: {response_text}")

                chunk_size = max(4, len(response_text)//10)
                for i in range(0, len(response_text), chunk_size):
                    yield response_text[i:i+chunk_size]
                    time.sleep(0.1)  # 100ms delay to imitate real streaming

        except Exception as e:
            logger.error(f"Lakera output screening failed: {e}")
            user_messages.append({"role": "assistant", "content": response_text})
            yield response_text

    return Response(stream_with_context(generate()), mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
