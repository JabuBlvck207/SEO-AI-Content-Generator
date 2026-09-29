import json
import os
import re

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
APP_URL = os.getenv("APP_URL", "http://127.0.0.1:5000")
APP_NAME = os.getenv("APP_NAME", "SEO Blog Intro Generator")


def clean_text(value, max_length):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value[:max_length]


def build_prompt(keyword, topic, tone):
    return f"""
You are an SEO content strategist and professional blog writer.

Create an SEO-friendly blog introduction package for:
Target keyword: {keyword}
Article topic: {topic}
Tone: {tone}

Return ONLY valid JSON. Do not use markdown fences.

Use exactly this structure:
{{
  "hook": "One engaging 1-2 sentence hook.",
  "headers": [
    "Suggested H2 heading 1",
    "Suggested H2 heading 2",
    "Suggested H2 heading 3",
    "Suggested H2 heading 4",
    "Suggested H2 heading 5"
  ],
  "introduction": "One polished introductory paragraph of about 100-150 words.",
  "tips": [
    "Practical SEO/content tip 1",
    "Practical SEO/content tip 2",
    "Practical SEO/content tip 3"
  ]
}}

Requirements:
- Naturally use the target keyword in the introduction.
- Do not keyword-stuff.
- Make the hook useful and specific rather than clickbait.
- Headers should follow a logical article flow.
- Keep the introduction readable for a general audience.
- Do not invent statistics, studies, quotations, or sources.
- Avoid claims that require current web research.
"""


def _extract_json_fragment(text):
    text = str(text or "").strip()
    if not text:
        return ""

    start = min((text.find("{"), text.find("[")), default=-1)
    if start == -1:
        return text

    stack = []
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char in "[{":
            stack.append(char)
        elif char in "}]":
            if not stack:
                return text[start:index + 1]
            last = stack.pop()
            if (last == "{" and char != "}") or (last == "[" and char != "]"):
                return text[start:index + 1]
            if not stack:
                return text[start:index + 1]

    return text[start:] if start != -1 else text


def parse_model_json(content):
    if content is None:
        raise ValueError("The model returned no content.")

    content = str(content).strip()
    if not content:
        raise ValueError("The model returned an empty response.")

    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)
    content = content.strip()

    candidates = [content]
    candidates.append(_extract_json_fragment(content))

    # Some models add extra explanation before or after the JSON object.
    candidates.append(re.sub(r",(\s*[}\]])", r"\1", content))

    for candidate in candidates:
        if not candidate or not candidate.strip():
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        cleaned = re.sub(r",(\s*[}\]])", r"\1", candidate)
        if cleaned != candidate:
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

    raise ValueError("The model returned a malformed JSON response. Please try again.")


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.post("/api/generate")
def generate():
    if not OPENROUTER_API_KEY:
        return jsonify({
            "error": "OpenRouter API key is not configured. Add OPENROUTER_API_KEY to backend/.env."
        }), 500

    data = request.get_json(silent=True) or {}

    keyword = clean_text(data.get("keyword"), 120)
    topic = clean_text(data.get("topic"), 250)
    tone = clean_text(data.get("tone"), 40) or "Professional"

    if len(keyword) < 2:
        return jsonify({"error": "Please enter a target keyword."}), 400

    if len(topic) < 5:
        return jsonify({"error": "Please enter an article topic."}), 400

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You produce accurate, useful SEO writing and follow JSON output instructions exactly."
            },
            {
                "role": "user",
                "content": build_prompt(keyword, topic, tone)
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1200
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": APP_NAME
    }

    last_error = None
    for attempt in range(2):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            result = response.json()

            content = result["choices"][0]["message"]["content"]
            generated = parse_model_json(content)

            required = ["hook", "headers", "introduction", "tips"]
            if not all(key in generated for key in required):
                raise ValueError("The AI response did not contain all required fields.")

            return jsonify(generated)
        except requests.HTTPError:
            try:
                detail = response.json().get("error", {}).get("message", response.text)
            except Exception:
                detail = response.text
            return jsonify({"error": f"OpenRouter request failed: {detail}"}), 502
        except (requests.RequestException, KeyError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt == 0:
                payload["messages"][1]["content"] = build_prompt(keyword, topic, tone) + "\n\nImportant: reply with only valid JSON, with no markdown code fences, no extra narration, and no trailing commas."
                continue
            break

    return jsonify({"error": f"Could not generate content: {last_error}"}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
