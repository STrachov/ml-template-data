import requests
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Setup headers if the API token is available
api_token = os.getenv('CRAWL4AI_API_TOKEN')  # Ensure the token is set in the .env file as CRAWL4AI_API_TOKEN
headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}

# Configuration for extraction using an LLM (e.g., OpenAI GPT-4)
extraction_config_llm = {
    "type": "llm",
    "params": {
        "provider": "openai/gpt-4",  # Specifies the LLM provider
        "instruction": "Extract main topics from the page"  # Instruction to guide the LLM on what to extract
    }
}

# Schema for extracting data using CSS selectors
schema = {
    "name": "Crypto Prices",  # Descriptive name for the schema
    "baseSelector": ".cds-tableRow-t45thuk",  # Base CSS selector for each row of data
    "fields": [
        {
            "name": "crypto",  # Field name for the cryptocurrency
            "selector": "td:nth-child(1) h2",  # CSS selector to extract the crypto name
            "type": "text",  # The type of data being extracted
        },
        {
            "name": "price",  # Field name for the price
            "selector": "td:nth-child(2)",  # CSS selector to extract the price
            "type": "text",  # The type of data being extracted
        }
    ],
}

# Configuration for extraction using JSON and CSS selectors
extraction_config_css = {
    "type": "json_css",
    "params": {"schema": schema}
}

# Configuration for extraction using a cosine similarity filter
extraction_config_cosine = {
    "type": "cosine",
    "params": {
        "semantic_filter": "business finance economy",  # Keywords to filter content based on relevance
        "word_count_threshold": 10,  # Minimum word count for the content to be considered
        "max_dist": 0.2,  # Maximum distance threshold for cosine similarity
        "top_k": 3  # Limit to the top 3 most relevant results
    }
}

# Making an authenticated POST request to initiate the crawl task
response = requests.post(
    "http://localhost:11235/crawl",  # The endpoint for initiating the crawl
    headers=headers,  # Include authentication headers if available
    json={
        "urls": "https://example.com",  # The URL to crawl
        "priority": 10,  # Priority of the task (higher numbers indicate higher priority)
        "extraction_config": extraction_config_css,  # Extraction config: choose between LLM, CSS, or cosine
        "js_code": [
            # JavaScript code to interact with the page (e.g., clicking a "Load More" button)
            "const loadMoreButton = Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Load More')); loadMoreButton && loadMoreButton.click();"
        ],
        "wait_for": "article.tease-card:nth-child(10)",  # Wait for this element to load before proceeding
        "screenshot": True,  # Capture a screenshot during the crawl
        "crawler_params": {
            "simulate_user": True,  # Simulate real user behavior
            "magic": True,  # Enable automatic optimizations for crawling
            "override_navigator": True,  # Override the navigator object for better anonymity
            "user_agent": "Mozilla/5.0 ...",  # Custom user-agent string to mimic a browser
            "headers": {
                "Accept-Language": "en-US,en;q=0.9"  # Set preferred language for the request
            },
            "extra": {
                "delay_before_return_html": 3.0  # Delay (in seconds) before returning the HTML
            },
            "screenshot_wait_for": ".main-content"  # Wait for this element before taking the screenshot
        },
    }
)

# Check the response status and retrieve the task ID
task_id = response.json().get("task_id")  # Safely get the task_id from the response JSON
if task_id:
    # Make a GET request to check the status of the initiated task
    status = requests.get(
        f"http://localhost:11235/task/{task_id}",  # Endpoint to get task status
        headers=headers  # Include authentication headers if available
    )
    # Print the status response for debugging purposes
    print(status.json())
else:
    print("Error: Task ID not found in the response.")
