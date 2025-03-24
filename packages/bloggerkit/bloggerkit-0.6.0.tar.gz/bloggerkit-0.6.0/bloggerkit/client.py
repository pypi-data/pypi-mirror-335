import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import Optional, List, Dict, Any

from bloggerkit.model import Author, Blog, Replies, Post, PostList, Error

# Blogger API에 필요한 Scope 설정
SCOPES = ['https://www.googleapis.com/auth/blogger']
# API 이름 및 버전
API_SERVICE_NAME = 'blogger'
API_VERSION = 'v3'
# 토큰 파일 이름 (클래스 내부에서 관리)
TOKEN_FILE = 'token.json'

class BloggerClient:
    """A client for interacting with the Google Blogger API using OAuth 2.0."""

    def __init__(self, blog_id: str, client_secrets_file: str) -> None:
        """Initializes the BloggerClient with a blog ID and OAuth 2.0 credentials.

        Args:
            blog_id: The ID of the blog to interact with.
            client_secrets_file: The path to the client_secrets.json file.
        """
        self.blog_id = blog_id
        self.client_secrets_file = client_secrets_file  # client_secrets.json 파일 경로 저장
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticates with Google using OAuth 2.0 and returns the Blogger service."""
        creds = None

        # token.json 파일에 사용자 인증 정보가 저장되어 있는지 확인
        if os.path.exists(TOKEN_FILE):
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # (아직) 유효한 인증 정보가 없다면, 사용자에게 로그인 요청
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(google.auth.transport.requests.Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    os.remove(TOKEN_FILE)  # 토큰 갱신에 실패하면 토큰 파일 삭제 후 재인증 시도
                    return self._authenticate()  # 재귀 호출을 통해 다시 인증 시도
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, SCOPES)  # client_secrets_file 사용
                creds = flow.run_local_server(port=0)

            # 인증 정보를 token.json 파일에 저장
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        try:
            # Construct the service object for the Blogger API.
            return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

        except Exception as e:
            print(f"Error during authentication: {e}")
            return None

    def list_posts(self) -> Optional[PostList]:
        """Lists all posts in the blog.

        Returns:
            A PostList object containing the list of posts, or None if an error occurred.
        """
        try:
            results = self.service.posts().list(blogId=self.blog_id).execute()
            posts = []
            for item in results.get("items", []):
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
                kind=results.get("kind", ""),
                nextPageToken=results.get("nextPageToken", ""),
                items=posts,
                etag=results.get("etag", ""),
            )
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def create_post(self, title: str, content: str) -> Optional[Dict[str, Any]]:
        """Creates a new post in the blog.

        Args:
            title: The title of the new post.
            content: The content of the new post.

        Returns:
            A dictionary containing the new post, or None if an error occurred.
        """
        post_body = {
            'title': title,
            'content': content
        }
        try:
            results = self.service.posts().insert(blogId=self.blog_id, body=post_body).execute()
            return results
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def get_post(self, post_id: str) -> Optional[Post]:
        """Retrieves a specific post from the blog.

        Args:
            post_id: The ID of the post to retrieve.

        Returns:
            A Post object containing the post, or None if an error occurred.
        """
        try:
            results = self.service.posts().get(blogId=self.blog_id, postId=post_id).execute()

            author_data = results.get("author", {})
            author = Author(
                displayName=author_data.get("displayName", ""),
                id=author_data.get("id", ""),
                image=author_data.get("image", {}),
                url=author_data.get("url", ""),
            )
            blog_data = results.get("blog", {})
            blog = Blog(id=blog_data.get("id", ""))
            replies_data = results.get("replies", {})
            replies = Replies(
                selfLink=replies_data.get("selfLink", ""),
                totalItems=replies_data.get("totalItems", ""),
            )
            return Post(
                author=author,
                blog=blog,
                content=results.get("content", ""),
                etag=results.get("etag", ""),
                id=results.get("id", ""),
                kind=results.get("kind", ""),
                labels=results.get("labels", []),
                published=results.get("published", ""),
                replies=replies,
                selfLink=results.get("selfLink", ""),
                title=results.get("title", ""),
                updated=results.get("updated", ""),
                url=results.get("url", ""),
            )
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
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
        post_body = {
            'title': title,
            'content': content
        }
        try:
            results = self.service.posts().update(blogId=self.blog_id, postId=post_id, body=post_body).execute()
            return results
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def delete_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Deletes a specific post from the blog.

        Args:
            post_id: The ID of the post to delete.

        Returns:
            A dictionary containing the deleted post, or None if an error occurred.
        """
        try:
            self.service.posts().delete(blogId=self.blog_id, postId=post_id).execute()
            return {} # 성공적으로 삭제된 경우 빈 딕셔너리 반환
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

if __name__ == "__main__":
    # Replace with your blog ID and client_secrets.json path
    blog_id = "YOUR_BLOD_ID"
    client_secrets_file = "YOUR_CLIENT_SECRETS_FILE_PATH"
    client = BloggerClient(blog_id, client_secrets_file)

    # Example usage
    # List posts
    posts = client.list_posts()
    if posts:
        print("Posts:")
        for post in posts.items:
            print(f"- {post.title}: {post.url}")

    # Create a new post
    new_post = client.create_post("Test Post3", "This is a test post created using the Blogger API.")
    if new_post:
        print(f"New post created: {new_post.get('url')}")

    # Get a specific post
    # post = client.get_post("POST_ID")  # Replace with a valid post ID
    # if post:
    #     print(f"Post: {post.title}, {post.content}")

    # Update a post
    # updated_post = client.update_post("POST_ID", "Updated Test Post", "This is the updated content.")
    # if updated_post:
    #     print(f"Post updated: {updated_post.get('url')}")

    # Delete a post
    # deleted = client.delete_post("POST_ID")