import os
import json
import requests
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def fetch_blog_content(url):
    """Fetch and clean blog content"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.decompose()
    
    # Find main content
    for selector in ['article', '.post-content', '.entry-content', '.content', 'main']:
        content = soup.select_one(selector)
        if content:
            break
    else:
        content = soup.find('body')
    
    # Clean text
    text = content.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return ' '.join(chunk for chunk in chunks if chunk)

# Define the 3 chain steps
extract_prompt = ChatPromptTemplate.from_template(
    """Extract 5-7 key insights from this blog that would make engaging social media content:

    {blog_content}

    Focus on actionable advice, interesting facts, and thought-provoking ideas. Return as bullet points."""
)

thread_prompt = ChatPromptTemplate.from_template(
    """Convert these key points into a Twitter thread. Requirements:
    - 4-7 tweets total
    - Each under 280 characters
    - Conversational tone
    - No hashtags
    - Start with engaging hook

    Key Points: {key_points}

    Format: 1/n Tweet content..."""
)

json_prompt = ChatPromptTemplate.from_template(
    """Convert this thread to JSON format:

    {thread}

    Return ONLY this structure:
    {{
        "thread": [
            {{"tweet_number": 1, "content": "tweet text", "character_count": 0}}
        ]
    }}"""
)

# Create chained pipeline
def format_for_thread(key_points):
    return {"key_points": key_points}

def format_for_json(thread):
    return {"thread": thread}

# Build the complete chain using | operator
complete_chain = (
    extract_prompt | llm | StrOutputParser() |
    RunnableLambda(format_for_thread) |
    thread_prompt | llm | StrOutputParser() |
    RunnableLambda(format_for_json) |
    json_prompt | llm | StrOutputParser()
)

def parse_json_result(raw_output):
    """Clean and parse LLM JSON output"""
    cleaned = raw_output.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    
    thread_data = json.loads(cleaned.strip())
    
    # Add character counts
    for tweet in thread_data['thread']:
        tweet['character_count'] = len(tweet['content'])
    
    return thread_data

def generate_thread(blog_url):
    """Generate Twitter thread from blog URL using LangChain chaining"""
    print(f"Processing: {blog_url}")
    
    # Fetch content
    blog_content = fetch_blog_content(blog_url)
    print(f"Extracted {len(blog_content)} characters")
    
    # Run the complete chained pipeline
    print("Running chained pipeline: Extract → Thread → JSON...")
    raw_result = complete_chain.invoke({"blog_content": blog_content[:3000]})
    
    # Parse result
    thread_data = parse_json_result(raw_result)
    
    # Display results
    print(f"\nGenerated {len(thread_data['thread'])} tweets:")
    for tweet in thread_data['thread']:
        chars = tweet['character_count']
        print(f"  {tweet['tweet_number']}: ({chars} chars) {tweet['content']}")
    
    return thread_data

if __name__ == "__main__":
    blog_url = "https://www.siddharthbharath.com/mastering-ai-coding-the-universal-playbook-of-tips-tricks-and-patterns/"
    
    result = generate_thread(blog_url)
    
    print("\nJSON Output:")
    print(json.dumps(result, indent=2))