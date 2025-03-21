from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Author:
    """Represents the author of a blog post."""
    displayName: str
    id: str
    image: Dict[str, str]
    url: str

@dataclass
class Blog:
    """Represents a blog."""
    id: str
    name: str = ""
    url: str = ""

@dataclass
class Error:
    """Represents an error returned by the Blogger API."""
    code: int
    message: str
    domain: str = ""
    reason: str = ""

@dataclass
class Replies:
    """Represents the replies to a blog post."""
    selfLink: str
    totalItems: str
    kind: str = ""

@dataclass
class Post:
    """Represents a blog post."""
    author: Author
    blog: Blog
    content: str
    etag: str
    id: str
    kind: str
    labels: List[str]
    published: str
    replies: Replies
    selfLink: str
    title: str
    updated: str
    url: str

@dataclass
class PostList:
    """Represents a list of blog posts."""
    kind: str
    nextPageToken: str
    items: List[Post]
    etag: str