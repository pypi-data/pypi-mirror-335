import urllib.request
import urllib.parse
import json
from typing import Optional, List, Dict, Any
from models import Author, Blog, Replies, Post, PostList, Error

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
                    # Create Error object for non-200 responses
                    return Error(code=response.getcode(), message="Request failed")
        except urllib.error.HTTPError as e:
            # Create Error object for HTTP errors
            return Error(code=e.code, message=e.read().decode("utf-8"))

    def list_posts(self) -> Optional[PostList]:
        """Lists all posts in the blog.

        Returns:
            A PostList object containing the list of posts, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        response = self._api_request(api_url)
        if response:
            posts = []
            for item in response.get("items", []):
                author_data = item.get("author", {})
                author = Author(
                    displayName=author_data.get("displayName", ""),
                    id=author_data.get("id", ""),
                    image=author_data.get("image", {}),
                    url=author_data.get("url", ""),
                )
                blog_data = item.get("blog", {})
                blog = Blog(id=blog_data.get("id", ""))
                replies_data = item.get("replies", {})
                replies = Replies(
                    selfLink=replies_data.get("selfLink", ""),
                    totalItems=replies_data.get("totalItems", ""),
                )
                post = Post(
                    author=author,
                    blog=blog,
                    content=item.get("content", ""),
                    etag=item.get("etag", ""),
                    id=item.get("id", ""),
                    kind=item.get("kind", ""),
                    labels=item.get("labels", []),
                    published=item.get("published", ""),
                    replies=replies,
                    selfLink=item.get("selfLink", ""),
                    title=item.get("title", ""),
                    updated=item.get("updated", ""),
                    url=item.get("url", ""),
                )
                posts.append(post)
            return PostList(
                kind=response.get("kind", ""),
                nextPageToken=response.get("nextPageToken", ""),
                items=posts,
                etag=response.get("etag", ""),
            )
        return None

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
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Retrieves a specific post from the blog.

        Args:
            post_id: The ID of the post to retrieve.

        Returns:
            A Post object containing the post, or None if an error occurred.
        """
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        response = self._api_request(api_url)
        if isinstance(response, Error):
            print(f"Error retrieving post: {response.message}")
            return None
        if response:
            author_data = response.get("author", {})
            author = Author(
                displayName=author_data.get("displayName", ""),
                id=author_data.get("id", ""),
                image=author_data.get("image", {}),
                url=author_data.get("url", ""),
            )
            blog_data = response.get("blog", {})
            blog = Blog(id=blog_data.get("id", ""))
            replies_data = response.get("replies", {})
            replies = Replies(
                selfLink=replies_data.get("selfLink", ""),
                totalItems=replies_data.get("totalItems", ""),
            )
            return Post(
                author=author,
                blog=blog,
                content=response.get("content", ""),
                etag=response.get("etag", ""),
                id=response.get("id", ""),
                kind=response.get("kind", ""),
                labels=response.get("labels", []),
                published=response.get("published", ""),
                replies=replies,
                selfLink=response.get("selfLink", ""),
                title=response.get("title", ""),
                updated=response.get("updated", ""),
                url=response.get("url", ""),
            )
        return None

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

if __name__ == "__main__":
    
    api_key= "YOUR_API_KEY"
    blog_id= "YOUR_BLOG_ID"
    if api_key and blog_id:
        client = BloggerClient(api_key=api_key, blog_id=blog_id)
        post_list = client.list_posts()
        if post_list:
            print(f"Kind: {post_list.kind}")
            print(f"Next Page Token: {post_list.nextPageToken}")
            print(f"Etag: {post_list.etag}")
            print("Items:")
            for post in post_list.items:
                print(f"  Title: {post.title}")
                print(f"  ID: {post.id}")
                print(f"  Author: {post.author.displayName}")
                print("-" * 20)
        else:
            print("Failed to retrieve posts.")

        # Get a specific post
        if post_list and post_list.items:
            first_post_id = post_list.items[0].id
            post = client.get_post(first_post_id)
            if post:
                print("\nRetrieved Post:")
                print(f"  Title: {post.title}")
                print(f"  ID: {post.id}")
                print(f"  Content: {post.content}")
                print(f"  Author: {post.author.displayName}")
                print(f"  Full Post: {post}")
            else:
                print(f"Failed to retrieve post with ID: {first_post_id}")
        else:
            print("No posts available to retrieve.")

        # More tests for response stability
        post_list = client.list_posts()
        # Print full response for debugging
        # print("\nFull PostList Response:")
        # print(post_list)
        if post_list and post_list.items:
            print(f"\nTest 1: Retrieved PostList with {len(post_list.items)} items")
            first_post_id = post_list.items[0].id
            post = client.get_post(first_post_id)
            if post:
                print(f"Test 1: Retrieved Post with title: {post.title}")
            else:
                print(f"Test 1: Failed to retrieve post with ID: {first_post_id}")

       # Test with non-existent post ID
        post = client.get_post("non_existent_post_id")
        if post:
           print("Test 2: Retrieved Post with non-existent ID (Error!)")
        elif isinstance(post, Error):
           print(f"Test 2: Failed to retrieve Post with non-existent ID (OK). Error: {post.message}")
        else:
           print("Test 2: Failed to retrieve Post with non-existent ID (OK)")

        # Test with a different post ID
        if post_list and len(post_list.items) > 1:
            second_post_id = post_list.items[1].id
            post = client.get_post(second_post_id)
            if post:
                print(f"Test 3: Retrieved Post with title: {post.title}")
            else:
                print(f"Test 3: Failed to retrieve post with ID: {second_post_id}")
        else:
            print("Test 3: Not enough posts to test with a different ID")

    else:
        print("Please set the BLOGGER_APIKEY and BLOG_ID environment variables.")