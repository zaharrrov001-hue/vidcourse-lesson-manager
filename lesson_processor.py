"""Lesson processing and editing module."""
import re
from typing import Dict, Optional
from google_drive import GoogleDriveClient


class LessonProcessor:
    """Processes and edits lesson content from Google Drive."""
    
    def __init__(self, drive_client: GoogleDriveClient):
        self.drive_client = drive_client
    
    def process_file(self, file_metadata: Dict) -> Dict:
        """
        Process a file from Google Drive and prepare it for GetCourse.
        
        Args:
            file_metadata: File metadata from Google Drive.
        
        Returns:
            Processed lesson data dictionary.
        """
        file_id = file_metadata['id']
        file_name = file_metadata['name']
        mime_type = file_metadata.get('mimeType', '')
        
        # Extract content based on file type
        content = self._extract_content(file_id, mime_type)
        
        # Process and format content
        processed_content = self._format_content(content, mime_type)
        
        # Extract title and description
        title = self._extract_title(file_name, content)
        description = self._extract_description(content, file_metadata)
        
        return {
            'title': title,
            'description': description,
            'content': processed_content,
            'source_file_id': file_id,
            'source_file_name': file_name,
            'mime_type': mime_type,
        }
    
    def _extract_content(self, file_id: str, mime_type: str) -> str:
        """
        Extract content from file based on MIME type.
        
        Args:
            file_id: Google Drive file ID.
            mime_type: File MIME type.
        
        Returns:
            Extracted content as string.
        """
        # Google Docs, Sheets, Slides
        if 'google-apps' in mime_type:
            if 'document' in mime_type:
                content_bytes = self.drive_client.export_file(file_id, 'text/plain')
            elif 'spreadsheet' in mime_type:
                content_bytes = self.drive_client.export_file(file_id, 'text/csv')
            elif 'presentation' in mime_type:
                content_bytes = self.drive_client.export_file(file_id, 'text/plain')
            else:
                content_bytes = self.drive_client.export_file(file_id, 'text/plain')
            return content_bytes.decode('utf-8', errors='ignore')
        
        # Text files
        elif mime_type.startswith('text/'):
            content_bytes = self.drive_client.get_file_content(file_id)
            return content_bytes.decode('utf-8', errors='ignore')
        
        # PDF files
        elif mime_type == 'application/pdf':
            # For PDF, we'll return a placeholder - you might want to add PDF parsing
            return f"[PDF file: {file_id}]"
        
        # Images
        elif mime_type.startswith('image/'):
            return f"[Image file: {file_id}]"
        
        # Videos
        elif mime_type.startswith('video/'):
            return f"[Video file: {file_id}]"
        
        # Default: try to get as text
        else:
            try:
                content_bytes = self.drive_client.get_file_content(file_id)
                return content_bytes.decode('utf-8', errors='ignore')
            except:
                return f"[Binary file: {file_id}]"
    
    def _format_content(self, content: str, mime_type: str) -> str:
        """
        Format content for GetCourse (convert to HTML if needed).
        
        Args:
            content: Raw content string.
            mime_type: Original file MIME type.
        
        Returns:
            Formatted HTML content.
        """
        if not content or content.strip() == "":
            return "<p>No content available.</p>"
        
        # If already HTML-like, return as is
        if '<html' in content.lower() or '<body' in content.lower():
            return content
        
        # Convert plain text to HTML
        html_content = content
        
        # Convert line breaks to paragraphs
        paragraphs = html_content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # Convert single line breaks to <br>
                para = para.replace('\n', '<br>\n')
                formatted_paragraphs.append(f"<p>{para}</p>")
        
        # Add basic styling
        html = f"""
        <div class="lesson-content">
            {''.join(formatted_paragraphs)}
        </div>
        <style>
            .lesson-content {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                padding: 20px;
            }}
            .lesson-content p {{
                margin-bottom: 15px;
            }}
        </style>
        """
        
        return html.strip()
    
    def _extract_title(self, file_name: str, content: str) -> str:
        """
        Extract or generate lesson title.
        
        Args:
            file_name: Original file name.
            content: File content.
        
        Returns:
            Lesson title.
        """
        # Remove file extension
        title = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
        
        # Try to extract title from content (first line or heading)
        if content:
            lines = content.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if line and len(line) < 100:  # Reasonable title length
                    # Check if it looks like a title
                    if line.isupper() or (len(line.split()) <= 10 and line[0].isupper()):
                        title = line
                        break
        
        return title.strip()
    
    def _extract_description(self, content: str, file_metadata: Dict) -> str:
        """
        Extract or generate lesson description.
        
        Args:
            content: File content.
            file_metadata: File metadata.
        
        Returns:
            Lesson description.
        """
        # Try to get description from metadata
        description = file_metadata.get('description', '')
        
        if not description and content:
            # Extract first paragraph or first few sentences
            paragraphs = content.split('\n\n')
            if paragraphs:
                first_para = paragraphs[0].strip()
                # Limit description length
                if len(first_para) > 200:
                    first_para = first_para[:200] + "..."
                description = first_para
        
        if not description:
            description = f"Lesson from {file_metadata.get('name', 'Google Drive')}"
        
        return description.strip()
    
    def enhance_content(self, content: str, **options) -> str:
        """
        Enhance lesson content with additional formatting or features.
        
        Args:
            content: Original content.
            **options: Enhancement options.
        
        Returns:
            Enhanced content.
        """
        enhanced = content
        
        # Add video embeds if video links are found
        if options.get('embed_videos', True):
            video_pattern = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+))'
            enhanced = re.sub(
                video_pattern,
                r'<iframe width="560" height="315" src="https://www.youtube.com/embed/\2" frameborder="0" allowfullscreen></iframe>',
                enhanced
            )
        
        # Add image optimization
        if options.get('optimize_images', True):
            img_pattern = r'<img([^>]+)>'
            enhanced = re.sub(
                img_pattern,
                r'<img\1 style="max-width: 100%; height: auto;">',
                enhanced
            )
        
        return enhanced