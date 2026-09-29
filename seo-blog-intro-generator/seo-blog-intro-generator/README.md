# SEO Blog Intro Generator

A simple CAPACITI full-stack project that generates SEO-friendly blog hooks, article outlines, introductions and SEO tips.

## Tech stack

- HTML5
- CSS3
- Vanilla JavaScript
- Python
- Flask
- OpenRouter API

The OpenRouter key stays on the Python backend. It is never placed in the browser JavaScript.

## 1. Open the project

Open a terminal in the project folder.

### Windows PowerShell

```powershell
cd "seo-blog-intro-generator"
```

## 2. Create a Python virtual environment

```powershell
cd backend
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Install dependencies

With the virtual environment active:

```powershell
python -m pip install -r requirements.txt
```

## 4. Configure OpenRouter

Copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

Then put your own OpenRouter API key into `.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-your-real-key
OPENROUTER_MODEL=openrouter/free
APP_URL=http://127.0.0.1:5000
APP_NAME=SEO Blog Intro Generator
```

Do not commit `.env` to Git.

## 5. Start the application

From the `backend` folder:

```powershell
python app.py
```

You should see Flask running on:

```text
http://127.0.0.1:5000
```

Open that address in your browser.

## 6. Test it

Try:

Target keyword:

```text
small business automation
```

Article topic:

```text
How automation can help small businesses save time and reduce repetitive work
```

Choose a tone and click **Generate content**.

## API endpoint

The frontend sends:

```http
POST /api/generate
Content-Type: application/json
```

Example:

```json
{
  "keyword": "small business automation",
  "topic": "How automation can help small businesses save time",
  "tone": "Professional"
}
```

The backend calls OpenRouter and returns:

```json
{
  "hook": "...",
  "headers": ["...", "...", "..."],
  "introduction": "...",
  "tips": ["...", "...", "..."]
}
```

## Changing the AI model

Change `OPENROUTER_MODEL` in `.env`.

For example:

```env
OPENROUTER_MODEL=openrouter/free
```

or another model slug available in your OpenRouter account.

## Security

Never put this in `frontend/script.js`:

```javascript
const API_KEY = "sk-or-v1-...";
```

The browser should call your Flask endpoint instead. Flask keeps the secret key server-side.

## Project flow

```text
Browser
   |
   | POST /api/generate
   v
Flask / Python
   |
   | OpenRouter API
   v
AI model
   |
   | JSON result
   v
Flask
   |
   v
Browser UI
```
