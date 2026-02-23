import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime, timedelta
from google import genai
import os

# ================= CONFIG =================

NEWS_API_KEY = "fe3d519d26a44a45b291825e050a9e75"
GEMINI_API_KEY = "AIzaSyCbeFzhrw9c-Yo0bKrqhbJ919VIcF6DsfU"

client = genai.Client(api_key=GEMINI_API_KEY)

# ================= FUNCTIONS =================

def fetch_news():
    query = search_entry.get()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a topic.")
        return
    status_label.config(text="Fetching news...")
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    news_box.delete("1.0", tk.END)
    if response.status_code != 200:
        news_box.insert(tk.END, "Error fetching news.\n")
        status_label.config(text="Error.")
        return
    articles = response.json().get("articles", [])
    if not articles:
        news_box.insert(tk.END, "No news found.\n")
        status_label.config(text="No results.")
        return
    for i, article in enumerate(articles, 1):
        news_box.insert(tk.END, f"📰 Article {i}\n")
        news_box.insert(tk.END, f"Title: {article['title']}\n")
        news_box.insert(tk.END, f"Source: {article['source']['name']}\n")
        news_box.insert(tk.END, "-"*60 + "\n")
    status_label.config(text="News loaded successfully.")

def summarize_news():
    content = news_box.get("1.0", tk.END)
    if not content.strip():
        messagebox.showwarning("No Content", "Fetch news first.")
        return
    status_label.config(text="Generating AI summary...")

    try:
        # Limit content size (IMPORTANT FIX)
        limited_content = content[:3000]
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=f"Summarize this news content in 5 bullet points:\n{limited_content}"
        )
        summary = response.text
        news_box.delete("1.0", tk.END)
        news_box.insert(tk.END, "🤖 AI Summary\n")
        news_box.insert(tk.END, "="*60 + "\n")
        news_box.insert(tk.END, summary)
        status_label.config(text="Summary generated.")
    except Exception as e:
        news_box.insert(tk.END, f"\nAI Error: {e}")
        status_label.config(text="AI error.")

# ================= GUI =================

root = tk.Tk()
root.title("AI News Intelligence Dashboard")
root.geometry("800x600")
root.configure(bg="#1e1e1e")
title_label = tk.Label(root, text="🔎 AI News Dashboard", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="white")
title_label.pack(pady=10)
search_frame = tk.Frame(root, bg="#1e1e1e")
search_frame.pack(pady=5)
search_entry = tk.Entry(search_frame, width=40, font=("Arial", 12))
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="Fetch News", command=fetch_news, bg="#4CAF50", fg="white")
search_button.pack(side=tk.LEFT, padx=5)
summary_button = tk.Button(search_frame, text="AI Summarize", command=summarize_news, bg="#2196F3", fg="white")
summary_button.pack(side=tk.LEFT, padx=5)
news_box = tk.Text(root, wrap=tk.WORD, font=("Arial", 11), bg="#2e2e2e", fg="white")
news_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(news_box)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
news_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=news_box.yview)
status_label = tk.Label(root, text="Ready", bg="#1e1e1e", fg="lightgreen")
status_label.pack(pady=5)

root.mainloop()
