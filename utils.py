"""Utility functions for VidCourse Lesson Manager."""
import re
from typing import Optional


def extract_stream_id_from_url(url: str) -> Optional[str]:
    """
    Extract stream ID from GetCourse URL.
    
    Args:
        url: GetCourse URL (e.g., https://riprokurs.getcourse.ru/teach/control/stream/view/id/934935666)
    
    Returns:
        Stream ID or None if not found.
    """
    pattern = r'/stream/view/id/(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def extract_account_from_url(url: str) -> Optional[str]:
    """
    Extract account name from GetCourse URL.
    
    Args:
        url: GetCourse URL (e.g., https://riprokurs.getcourse.ru/...)
    
    Returns:
        Account name or None if not found.
    """
    pattern = r'https?://([^.]+)\.getcourse\.(ru|io)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None