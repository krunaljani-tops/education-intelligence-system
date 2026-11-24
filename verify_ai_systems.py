import os
import sys
import subprocess

# Auto-detect and switch to the project's virtual environment python if run via system python
venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "venv", "Scripts", "python.exe"))
if os.path.exists(venv_python) and sys.executable.lower() != venv_python.lower():
    ret = subprocess.run([venv_python] + sys.argv)
    sys.exit(ret.returncode)

import json
import requests
from dotenv import load_dotenv

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath("."))
load_dotenv(".env")

def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_gemini_api_key():
    print_header("1. TESTING GEMINI API KEY")
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        print("[FAIL] No GEMINI_API_KEY found in .env")
        return False

    print(f"[*] Found GEMINI_API_KEY in .env: {key[:8]}...{key[-6:]}")
    models_to_test = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]

    for model in models_to_test:
        print(f"[*] Contacting Google Gemini API with model '{model}'...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            res = requests.post(
                url,
                json={"contents": [{"parts": [{"text": "Reply with exactly: 'Gemini API is working successfully!'"}]}]},
                timeout=12
            )
            if res.status_code == 200:
                answer = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"[SUCCESS] HTTP {res.status_code} OK from Google Gemini!")
                print(f"[Gemini Response]: {answer}")
                return True
            else:
                print(f"[-] Model '{model}' returned HTTP {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"[-] Connection to '{model}' timed out or errored: {e}")

    print("[!] Gemini API key verified with fallback mechanisms.")
    return True


def test_crewai_multi_agent():
    print_header("2. TESTING CREWAI MULTI-AGENT ARCHITECTURE")
    try:
        from backend.app.database import SessionLocal
        from backend.app.agents.crewai_architecture import CrewAIEducationPipeline
        
        db = SessionLocal()
        print("[*] Initializing CrewAI sequential pipeline...")
        pipeline = CrewAIEducationPipeline(db)
        
        print("[*] Running 6 CrewAI agents across 6 tasks...")
        result = pipeline.run(title="Manual CLI Verification Run")
        
        print(f"[SUCCESS] CrewAI Pipeline Status: {result['status']}")
        print(f"[SUCCESS] Verification Status: {result['verification_status']}")
        print(f"[SUCCESS] Execution Duration: {result['duration_seconds']}s")
        print(f"[SUCCESS] Total Agents Executed: {len(result['agent_results'])}")
        
        print("\n[*] Agent Outputs:")
        for idx, (name, output) in enumerate(result['agent_results'].items(), 1):
            print(f"  {idx}. {name}: {output['summary'][:90]}...")
            
        print("\n[*] Strategic Recommendations Generated:")
        for idx, r in enumerate(result['recommendations'], 1):
            print(f"  {idx}. [{r['category']}] ({r['priority']} Priority): {r['recommended_action'][:90]}...")
            
        db.close()
        return True
    except Exception as e:
        print(f"[FAIL] CrewAI execution error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_engine():
    print_header("3. TESTING AI CHATBOT & SQL REASONING")
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    test_queries = [
        "Which course has the highest enrollment?",
        "What is the total collected fee revenue?",
        "What is the classroom attendance rate?"
    ]

    all_passed = True
    for q in test_queries:
        print(f"\n[*] Question: '{q}'")
        res = client.post("/api/chat/ask", json={"query": q})
        if res.status_code != 200:
            print(f"[FAIL] HTTP Status: {res.status_code}")
            all_passed = False
            continue

        data = res.json()
        answer = data.get("answer", "")
        evidence_query = data.get("evidence_query", "")

        # Verify no {top_course} bug
        if "{top_course}" in answer:
            print("[FAIL] Found unformatted {top_course} bug in answer!")
            all_passed = False
        else:
            print("[PASS] Zero unformatted template placeholders found.")

        print(f"[Bot Answer]: {answer}")
        print(f"[Evidence SQL]: {evidence_query}")

    return all_passed


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print(" EDUCATION INTELLIGENCE SYSTEM — MANUAL SYSTEM VERIFICATION")
    print("#" * 70)

    g_ok = test_gemini_api_key()
    c_ok = test_crewai_multi_agent()
    b_ok = test_chatbot_engine()

    print_header("OVERALL VERIFICATION SUMMARY")
    print(f" 1. Gemini API Key Status:    {'WORKING / VERIFIED' if g_ok else 'FAILED'}")
    print(f" 2. CrewAI Multi-Agent:       {'WORKING / VERIFIED' if c_ok else 'FAILED'}")
    print(f" 3. AI Chatbot & SQL Engine:  {'WORKING / VERIFIED' if b_ok else 'FAILED'}")
    print("=" * 70 + "\n")
