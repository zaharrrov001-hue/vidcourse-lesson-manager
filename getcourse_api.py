"""GetCourse API client for creating lessons."""
import requests
from typing import Dict, Optional, List
from config import Config


class GetCourseAPI:
    """Client for interacting with GetCourse API."""
    
    def __init__(self, api_key=None, account=None, api_url=None):
        self.api_key = api_key or Config.GETCOURSE_API_KEY
        self.api_url = api_url or Config.GETCOURSE_API_URL
        self.account = account or Config.GETCOURSE_ACCOUNT
        
        if not self.api_key:
            raise ValueError("GetCourse API key is required")
        
        if not self.account:
            raise ValueError("GetCourse account name is required (extract from URL, e.g., 'riprokurs' from riprokurs.getcourse.ru)")
    
    def _make_request(
        self,
        action: str,
        params: Optional[Dict] = None,
        method: str = "POST"
    ) -> Dict:
        """
        Make a request to GetCourse API.
        
        Args:
            action: API action name.
            params: Request parameters.
            method: HTTP method (POST or GET).
        
        Returns:
            API response as dictionary.
        """
        # GetCourse API format: https://account.getcourse.ru/pl/api/account/account_name/actions
        if self.account:
            base_url = f"https://{self.account}.getcourse.ru"
        else:
            base_url = self.api_url
        
        url = f"{base_url}/pl/api/account/{self.account}/actions"
        
        # GetCourse API uses form data, not JSON
        payload = {
            "key": self.api_key,
            "action": action,
        }
        
        if params:
            payload.update(params)
        
        try:
            if method.upper() == "POST":
                # GetCourse API typically expects form data
                response = requests.post(url, data=payload)
            else:
                response = requests.get(url, params=payload)
            
            response.raise_for_status()
            
            # GetCourse API may return different formats
            try:
                return response.json()
            except ValueError:
                # If not JSON, return text response
                return {"success": True, "response": response.text}
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
    
    def create_lesson(
        self,
        title: str,
        description: str,
        content: str,
        course_id: Optional[str] = None,
        stream_id: Optional[str] = None,
        order: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """
        Create a lesson in GetCourse.
        
        Args:
            title: Lesson title.
            description: Lesson description.
            content: Lesson content (HTML or text).
            course_id: Course ID to attach lesson to.
            stream_id: Stream ID (from URL like /stream/view/id/934935666).
            order: Lesson order in course.
            **kwargs: Additional lesson parameters.
        
        Returns:
            Created lesson data.
        """
        # GetCourse API uses different parameter names
        params = {
            "title": title,
            "description": description,
            "text": content,  # GetCourse may use 'text' instead of 'content'
        }
        
        if stream_id:
            params["stream_id"] = stream_id
        elif course_id:
            params["course_id"] = course_id
        
        if order is not None:
            params["order"] = order
        
        params.update(kwargs)
        
        # Try different action names that GetCourse might use
        try:
            return self._make_request("streams.addLesson", params)
        except:
            try:
                return self._make_request("lessons.add", params)
            except:
                return self._make_request("lessons.create", params)
    
    def update_lesson(
        self,
        lesson_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing lesson in GetCourse.
        
        Args:
            lesson_id: Lesson ID to update.
            title: New lesson title.
            description: New lesson description.
            content: New lesson content.
            **kwargs: Additional lesson parameters.
        
        Returns:
            Updated lesson data.
        """
        params = {"lesson_id": lesson_id}
        
        if title:
            params["title"] = title
        if description:
            params["description"] = description
        if content:
            params["content"] = content
        
        params.update(kwargs)
        
        return self._make_request("lessons.update", params)
    
    def list_lessons(self, course_id: Optional[str] = None) -> List[Dict]:
        """
        List lessons in GetCourse.
        
        Args:
            course_id: Optional course ID to filter lessons.
        
        Returns:
            List of lessons.
        """
        params = {}
        if course_id:
            params["course_id"] = course_id
        
        response = self._make_request("lessons.list", params)
        return response.get("lessons", [])
    
    def get_lesson(self, lesson_id: str) -> Dict:
        """
        Get lesson details.
        
        Args:
            lesson_id: Lesson ID.
        
        Returns:
            Lesson data.
        """
        return self._make_request("lessons.get", {"lesson_id": lesson_id})
    
    def create_course(
        self,
        title: str,
        description: str,
        **kwargs
    ) -> Dict:
        """
        Create a course in GetCourse.
        
        Args:
            title: Course title.
            description: Course description.
            **kwargs: Additional course parameters.
        
        Returns:
            Created course data.
        """
        params = {
            "title": title,
            "description": description,
        }
        params.update(kwargs)
        
        return self._make_request("courses.create", params)