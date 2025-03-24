# Bloggerkit

A Python toolkit for interacting with the Google Blogger API.

## Installation

```bash
pip install bloggerkit
```

## Authentication

This library now uses OAuth 2.0 for authentication. Follow these steps to set up your credentials:

1.  **Create a Google Cloud Project:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
2.  **Enable the Blogger API:**
    *   In the Cloud Console, navigate to "APIs & Services" > "Library".
    *   Search for "Blogger API" and enable it.
3.  **Create OAuth 2.0 Credentials:**
    *   Go to "APIs & Services" > "Credentials".
    *   Click "Create Credentials" > "OAuth client ID".
    *   Select "Desktop app" as the application type.
    *   Give your client ID a name and click "Create".
4.  **Download the client_secrets.json file:**
    *   After creating the client ID, download the `client_secrets.json` file.
    *   Place this file in your project directory.

## Usage

```python
from bloggerkit import BloggerClient

# Replace with your blog ID and the path to your client_secrets.json file
BLOG_ID = "YOUR_BLOG_ID"
CLIENT_SECRETS_FILE = "path/to/your/client_secrets.json"

client = BloggerClient(BLOG_ID, CLIENT_SECRETS_FILE)

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

**Note:** 

*   Make sure to replace `YOUR_BLOG_ID`, `path/to/your/client_secrets.json` and `POST_ID` with your actual blog ID, the path to your `client_secrets.json` file, and post ID.
*   The first time you run the script, it will open a web browser to authenticate with your Google account.
*   A `token.json` file will be created to store your access token. If you change the `client_secrets.json` file, you may need to delete the `token.json` file and re-authenticate.
*   The `BloggerClient` now takes the blog ID and the path to the `client_secrets.json` file as arguments.

## Features

*   `list_posts()`: Retrieves a list of all posts in the blog.
*   `create_post(title, content)`: Creates a new post with the given title and content.
*   `get_post(post_id)`: Retrieves a specific post by its ID.
*   `update_post(post_id, title, content)`: Updates an existing post with the given ID, title, and content.
*   `delete_post(post_id)`: Deletes a post with the given ID.

## Change Log

See [changelog.md](changelog.md) for details.