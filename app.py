from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

from dialogue.manager import DialogueManager
from dialogue.modes import DialogueMode

from fastapi.responses import HTMLResponse

app = FastAPI(
    title="StudyBot API",
    description="Course-specific study assistant",
    version="0.1.0",
)

manager = DialogueManager()

# ---- Request / Response ----
class StudyRequest(BaseModel):
    mode: DialogueMode   # explain / quiz / review
    question: str


class StudyResponse(BaseModel):
    answer: str


# ---- Routes ----
@app.post("/study", response_model=StudyResponse)
def study(req: StudyRequest):
    result = manager.handle(
        mode=req.mode,
        question=req.question
    )
    return StudyResponse(answer=result)


@app.get("/")
def root():
    return {"status": "ok", "bot": "studybot"}


@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Queen's StudyBot</title>
        <meta charset="utf-8" />
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        
        <style>
            /* Queen's University official color palette */
            :root { --queens-blue: #002452; --queens-gold: #feb70d; --queens-red: #b90e31; }
            
            body { font-family: 'Segoe UI', sans-serif; background: #f4f4f9; display: flex; justify-content: center; padding: 20px; }
            .container { width: 100%; max-width: 800px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 8px solid var(--queens-blue); }
            h1 { color: var(--queens-blue); text-align: center; }
            
            .input-group { margin-bottom: 20px; }
            label { font-weight: bold; display: block; margin-bottom: 8px; color: #333; }
            
            select, textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; }
            textarea { height: 100px; resize: vertical; }
            
            /* Action bar for primary and secondary utility buttons */
            .action-bar { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
            button { background: var(--queens-blue); color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
            button:hover { background: #003a80; }
            .secondary-btn { background: #6c757d; font-size: 12px; padding: 5px 10px; }
            
            /* Loading spinner animation */
            .loader { display: none; text-align: center; margin: 20px 0; color: var(--queens-blue); font-style: italic; }
            .spinner { border: 4px solid #f3f3f3; border-top: 4px solid var(--queens-blue); border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 10px; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

            /* Results display area */
            .answer-card { margin-top: 20px; padding: 25px; background: #fafafa; border-radius: 8px; border-left: 5px solid var(--queens-gold); display: none; position: relative; }
            .copy-btn { position: absolute; top: 10px; right: 10px; background: var(--queens-gold); color: var(--queens-blue); border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 11px; font-weight: bold; }
            .answer-content { line-height: 1.7; color: #2c3e50; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cha Gheill! StudyBot</h1>
            
            <div class="input-group">
                <label>Study Mode</label>
                <select id="mode">
                    <option value="explain">💡 Explain Concept (Simple Steps)</option>
                    <option value="quiz">📝 Generate Quiz (Test My Knowledge)</option>
                    <option value="review">🎯 Quick Review (Key Points & Exam Prep)</option>
                </select>
            </div>

            <div class="input-group">
                <label>Topic / Question</label>
                <textarea id="question" placeholder="e.g., Explain the Central Limit Theorem..."></textarea>
            </div>

            <div class="action-bar">
                <button onclick="clearAll()" class="secondary-btn">Clear Screen</button>
                <button id="askBtn" onclick="ask()">Ask Assistant</button>
            </div>

            <div id="loader" class="loader">
                <div class="spinner"></div> DeepSeek is analyzing the material...
            </div>

            <div id="answerCard" class="answer-card">
                <button class="copy-btn" onclick="copyAnswer()">Copy to Clipboard</button>
                <div id="answer" class="answer-content"></div>
            </div>
        </div>

        <script>
            /**
             * Primary function to send user question to the FastAPI backend
             */
            async function ask() {
                const mode = document.getElementById("mode").value;
                const question = document.getElementById("question").value;
                const btn = document.getElementById("askBtn");
                const loader = document.getElementById("loader");
                const answerCard = document.getElementById("answerCard");
                const answerDiv = document.getElementById("answer");

                if (!question.trim()) return alert("Please enter a topic first!");

                // UI Reset: Disable interactions and show loading state
                btn.disabled = true;
                loader.style.display = "block";
                answerCard.style.display = "none";

                try {
                    const res = await fetch("/study", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ mode: mode, question: question })
                    });
                    
                    const data = await res.json();
                    
                    // Step 1: Convert Markdown text into HTML elements
                    answerDiv.innerHTML = marked.parse(data.answer);
                    answerCard.style.display = "block";
                    
                    // Step 2: Tell MathJax to scan the new HTML for math formulas and render them
                    if (window.MathJax) {
                        MathJax.typesetPromise();
                    }
                } catch (e) {
                    answerDiv.innerHTML = "<p style='color:red'>Connection Error. Is the server running?</p>";
                    answerCard.style.display = "block";
                } finally {
                    // Re-enable interactions
                    btn.disabled = false;
                    loader.style.display = "none";
                }
            }

            /**
             * Utility: Copy the text content of the AI response to system clipboard
             */
            function copyAnswer() {
                const text = document.getElementById("answer").innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert("Study notes copied to clipboard!");
                });
            }

            /**
             * Utility: Clear the input and hide previous results
             */
            function clearAll() {
                document.getElementById("question").value = "";
                document.getElementById("answerCard").style.display = "none";
            }
        </script>
    </body>
    </html>
    """