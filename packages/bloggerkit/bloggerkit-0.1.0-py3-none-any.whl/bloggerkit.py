import urllib.request
import urllib.parse
import json

class BloggerClient:
    def __init__(self, api_key, blog_id):
        self.api_key = api_key
        self.blog_id = blog_id

    def _api_request(self, url, method="GET", data=None, headers=None):
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

    def list_posts(self):
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        return self._api_request(api_url)

    def create_post(self, title, content):
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts"
        post_data = {
            "title": title,
            "content": content,
        }
        return self._api_request(api_url, method="POST", data=post_data)
    
    def get_post(self, post_id):
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        return self._api_request(api_url)

    def update_post(self, post_id, title, content):
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        post_data = {
            "title": title,
            "content": content,
        }
        return self._api_request(api_url, method="PUT", data=post_data)

    def delete_post(self, post_id):
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/{post_id}"
        return self._api_request(api_url, method="DELETE")