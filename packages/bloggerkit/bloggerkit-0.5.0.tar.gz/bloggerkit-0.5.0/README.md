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

## Features

*   `list_posts()`: Retrieves a list of all posts in the blog.
*   `create_post(title, content)`: Creates a new post with the given title and content.
*   `get_post(post_id)`: Retrieves a specific post by its ID.
*   `update_post(post_id, title, content)`: Updates an existing post with the given ID, title, and content.
*   `delete_post(post_id)`: Deletes a post with the given ID.

## Usage

```python
from bloggerkit import BloggerClient

# Replace with your credentials
API_KEY = "YOUR_API_KEY"
BLOG_ID = "YOUR_BLOG_ID"

client = BloggerClient(API_KEY, BLOG_ID)

# List posts
posts = client.list_posts()
if posts and "items" in posts:
    for post in posts["items"]:
        print(post['title'], post['url'])

# Create a new post
new_post = client.create_post("My New Post", "Content of my new post.")
if new_post:
    print(f"New post created: {new_post['url']}")

# Get a specific post
post = client.get_post("POST_ID")  # Replace with the actual post ID
if post:
    print(f"Post title: {post['title']}")

# Update a post
updated_post = client.update_post("POST_ID", "Updated Title", "Updated content.")  # Replace with the actual post ID
if updated_post:
    print(f"Post updated: {updated_post['url']}")

# Delete a post
client.delete_post("POST_ID")  # Replace with the actual post ID
print("Post deleted successfully.")
```

**Note:** Make sure to replace `YOUR_API_KEY`, `YOUR_BLOG_ID`, and `POST_ID` with your actual API key, blog ID, and post ID. It's recommended to store your API key in a secure way, such as using environment variables.