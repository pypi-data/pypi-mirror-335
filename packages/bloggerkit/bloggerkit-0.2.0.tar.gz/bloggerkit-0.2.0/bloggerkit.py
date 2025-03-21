import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any

class BloggerClient:
    """A client for interacting with the Google Blogger API.

    Attributes:
        api_key: The API key for accessing the Blogger API.
        blog_id: The ID of the blog to interact with.
    """

    def __init__(self, api_key: str, blog_id: str) -> None:
        """Initializes the BloggerClient with an API key and blog ID.

        Args:
            api_key: The API key for accessing the Blogger API.
            blog_id: The ID of the blog to interact with.
        """
        self.api_key = api_key
        self.blog_id = blog_id

    def _api_request(self, url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Sends a request to the Blogger API.

        Args:
            url: The URL to send the request to.
            method: The HTTP method to use (default: "GET").
            data: The data to send with the request (default: None).
            headers: The headers to send with the request (default: None).

        Returns:
            The JSON response from the API, or None if an error occurred.
        """
        url += f"?key={self.api_key}"

        if data:
            data = json.dumps(data).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
        else:
            req = urllib.request.Request(url, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                if response.getcode() in (200, 201):
                    return json.loads(response.read().decode("utf-8"))
                else:
                    print(f"Error: {response.getcode()}")
                    return None
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code}")
            print(e.read().decode("utf-8"))
            return None

    def list_posts(self) -> Optional[Dict[str, Any]]:
        """Lists all posts in the blog.

        Returns:
            A dictionary containing the list of posts, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        return self._api_request(api_url)

    def create_post(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """Creates a new post in the blog.

        Args:
            title: The title of the new post.
            content: The content of the new post.

        Returns:
            A dictionary containing the new post, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        post_data = {
            "title": title,
            "content": content,
        }
        return self._api_request(api_url, method="POST", data=post_data)
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific post from the blog.

        Args:
            post_id: The ID of the post to retrieve.

        Returns:
            A dictionary containing the post, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        return self._api_request(api_url)

    def update_post(self, post_id: str, title: str, content: str) -> Optional[Dict[str, Any]]:
        """Updates a specific post in the blog.

        Args:
            post_id: The ID of the post to update.
            title: The new title of the post.
            content: The new content of the post.

        Returns:
            A dictionary containing the updated post, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        post_data = {
            "title": title,
            "content": content,
        }
        return self._api_request(api_url, method="PUT", data=post_data)

    def delete_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Deletes a specific post from the blog.

        Args:
            post_id: The ID of the post to delete.

        Returns:
            A dictionary containing the deleted post, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        return self._api_request(api_url, method="DELETE")