"""Main entry point for VidCourse Lesson Manager."""
import argparse
import sys
from typing import List, Dict, Optional
from config import Config
from google_drive import GoogleDriveClient
from getcourse_api import GetCourseAPI
from lesson_processor import LessonProcessor


class VidCourseManager:
    """Main manager class for VidCourse lesson processing."""
    
    def __init__(self):
        """Initialize the manager with all required clients."""
        if not Config.validate():
            missing = Config.get_missing_config()
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            print("Please set these in your .env file or environment variables.")
            sys.exit(1)
        
        print("🔐 Authenticating with Google Drive...")
        self.drive_client = GoogleDriveClient()
        
        print("🔐 Connecting to GetCourse API...")
        self.getcourse_api = GetCourseAPI()
        
        self.processor = LessonProcessor(self.drive_client)
        print("✅ Initialization complete!\n")
    
    def list_lessons(self) -> List[Dict]:
        """List all available lessons from Google Drive."""
        print("📂 Fetching lessons from Google Drive...")
        files = self.drive_client.list_files_in_folder()
        
        if not files:
            print("No files found in the specified folder.")
            return []
        
        print(f"\n📚 Found {len(files)} file(s):\n")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file['name']} (ID: {file['id']})")
            print(f"   Type: {file.get('mimeType', 'Unknown')}")
            print(f"   Modified: {file.get('modifiedTime', 'Unknown')}")
            print()
        
        return files
    
    def process_lesson(
        self,
        file_metadata: Dict,
        course_id: Optional[str] = None,
        stream_id: Optional[str] = None,
        create_in_getcourse: bool = True,
        **options
    ) -> Dict:
        """
        Process a single lesson and optionally create it in GetCourse.
        
        Args:
            file_metadata: File metadata from Google Drive.
            course_id: Optional course ID to attach lesson to.
            create_in_getcourse: Whether to create lesson in GetCourse.
            **options: Additional processing options.
        
        Returns:
            Processed lesson data.
        """
        print(f"🔄 Processing: {file_metadata['name']}")
        
        # Process the lesson
        lesson_data = self.processor.process_file(file_metadata)
        
        # Enhance content if options provided
        if options:
            lesson_data['content'] = self.processor.enhance_content(
                lesson_data['content'],
                **options
            )
        
        print(f"✅ Processed: {lesson_data['title']}")
        print(f"   Description: {lesson_data['description'][:100]}...")
        
        # Create in GetCourse if requested
        if create_in_getcourse:
            print("🚀 Creating lesson in GetCourse...")
            try:
                result = self.getcourse_api.create_lesson(
                    title=lesson_data['title'],
                    description=lesson_data['description'],
                    content=lesson_data['content'],
                    course_id=course_id,
                    stream_id=stream_id,
                    **{k: v for k, v in options.items() if k not in ['embed_videos', 'optimize_images']}
                )
                print(f"✅ Lesson created successfully in GetCourse!")
                lesson_data['getcourse_id'] = result.get('lesson_id')
                lesson_data['getcourse_result'] = result
            except Exception as e:
                print(f"❌ Failed to create lesson in GetCourse: {e}")
                lesson_data['getcourse_error'] = str(e)
        
        return lesson_data
    
    def process_all_lessons(
        self,
        course_id: Optional[str] = None,
        stream_id: Optional[str] = None,
        create_in_getcourse: bool = True,
        **options
    ) -> List[Dict]:
        """
        Process all lessons from Google Drive folder.
        
        Args:
            course_id: Optional course ID to attach lessons to.
            create_in_getcourse: Whether to create lessons in GetCourse.
            **options: Additional processing options.
        
        Returns:
            List of processed lesson data.
        """
        files = self.list_lessons()
        
        if not files:
            return []
        
        processed_lessons = []
        
        for file in files:
            try:
                lesson = self.process_lesson(
                    file,
                    course_id=course_id,
                    stream_id=stream_id,
                    create_in_getcourse=create_in_getcourse,
                    **options
                )
                processed_lessons.append(lesson)
                print()  # Empty line for readability
            except Exception as e:
                print(f"❌ Error processing {file['name']}: {e}\n")
                continue
        
        print(f"\n✨ Processed {len(processed_lessons)} lesson(s) successfully!")
        return processed_lessons


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VidCourse Lesson Manager - Process lessons from Google Drive and send to GetCourse"
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available lessons from Google Drive'
    )
    
    parser.add_argument(
        '--process-all',
        action='store_true',
        help='Process all lessons from Google Drive folder'
    )
    
    parser.add_argument(
        '--lesson-id',
        type=str,
        help='Process a specific lesson by Google Drive file ID'
    )
    
    parser.add_argument(
        '--course-id',
        type=str,
        help='GetCourse course ID to attach lessons to'
    )
    
    parser.add_argument(
        '--stream-id',
        type=str,
        help='GetCourse stream ID to attach lessons to (from URL like /stream/view/id/934935666)'
    )
    
    parser.add_argument(
        '--no-create',
        action='store_true',
        help='Process lessons but do not create them in GetCourse'
    )
    
    parser.add_argument(
        '--embed-videos',
        action='store_true',
        default=True,
        help='Embed YouTube videos in content (default: True)'
    )
    
    parser.add_argument(
        '--optimize-images',
        action='store_true',
        default=True,
        help='Optimize images in content (default: True)'
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    try:
        manager = VidCourseManager()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)
    
    # Execute requested action
    if args.list:
        manager.list_lessons()
    
    elif args.process_all:
        manager.process_all_lessons(
            course_id=args.course_id,
            stream_id=args.stream_id,
            create_in_getcourse=not args.no_create,
            embed_videos=args.embed_videos,
            optimize_images=args.optimize_images
        )
    
    elif args.lesson_id:
        files = manager.drive_client.list_files_in_folder()
        file_metadata = next((f for f in files if f['id'] == args.lesson_id), None)
        
        if not file_metadata:
            print(f"❌ Lesson with ID '{args.lesson_id}' not found.")
            sys.exit(1)
        
        manager.process_lesson(
            file_metadata,
            course_id=args.course_id,
            stream_id=args.stream_id,
            create_in_getcourse=not args.no_create,
            embed_videos=args.embed_videos,
            optimize_images=args.optimize_images
        )
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()