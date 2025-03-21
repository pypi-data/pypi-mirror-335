# Bloggerkit

A Python toolkit for interacting with the Google Blogger API.

## Installation

```bash
pip install bloggerkit
```

## Usage

```python
from bloggerkit import BloggerClient

# Replace with your credentials
API_KEY = "YOUR_API_KEY"
BLOG_ID = "YOUR_BLOG_ID"

client = BloggerClient(API_KEY, BLOG_ID)

posts = client.list_posts()
if posts and "items" in posts:
    for post in posts["items"]:
        print(post['title'], post['url'])

new_post = client.create_post("My New Post", "Content of my new post.")
if new_post:
    print(f"New post created: {new_post['url']}")