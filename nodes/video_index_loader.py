import os
import folder_paths
from typing import List


class SimpleVideoIndexLoader:
    """
    Simple video index loader - returns video path based on folder and index
    """
    
    # Common video file extensions
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', '.3gp', '.ts'}
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get available folders - you can customize this to your needs
        input_dir = folder_paths.get_input_directory()
        folders = ["input"]  # Default to input folder
        
        # Optionally add other common folders
        try:
            # Add subdirectories of input folder
            if os.path.exists(input_dir):
                subdirs = [d for d in os.listdir(input_dir) 
                          if os.path.isdir(os.path.join(input_dir, d))]
                folders.extend([f"input/{subdir}" for subdir in subdirs])
        except:
            pass
            
        # Add some common video folders if they exist
        for folder_name in ["videos", "movies", "clips"]:
            folder_path = os.path.join(folder_paths.get_input_directory(), folder_name)
            if os.path.exists(folder_path):
                folders.append(f"input/{folder_name}")
        
        if not folders:
            folders = ["input"]
            
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "input", 
                    "tooltip": "Folder path relative to ComfyUI input directory, or absolute path"
                }),
                "video_index": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 10000, 
                    "step": 1,
                    "tooltip": "Index of video file to select (0-based)"
                }),
                "loop_videos": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "If True, index wraps around when it exceeds number of videos"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("video_path", "video_filename", "current_index", "total_videos")
    
    FUNCTION = "get_video_path"
    CATEGORY = "Video Loader"
    
    def get_video_files(self, folder_path: str) -> List[str]:
        """Get all video files from the specified folder"""
        video_files = []
        
        # Handle relative paths (relative to input directory)
        if not os.path.isabs(folder_path):
            if folder_path.startswith("input/") or folder_path.startswith("input\\"):
                # Remove "input/" prefix and join with input directory
                relative_path = folder_path[6:]  # Remove "input/"
                full_path = os.path.join(folder_paths.get_input_directory(), relative_path)
            elif folder_path == "input":
                full_path = folder_paths.get_input_directory()
            else:
                full_path = os.path.join(folder_paths.get_input_directory(), folder_path)
        else:
            full_path = folder_path
        
        try:
            if os.path.exists(full_path) and os.path.isdir(full_path):
                for filename in sorted(os.listdir(full_path)):
                    file_path = os.path.join(full_path, filename)
                    if os.path.isfile(file_path):
                        # Check if file has video extension
                        _, ext = os.path.splitext(filename.lower())
                        if ext in self.VIDEO_EXTENSIONS:
                            video_files.append(os.path.join(full_path, filename))
        except Exception as e:
            print(f"Error reading folder {full_path}: {str(e)}")
        
        return video_files
    
    def get_video_path(self, folder_path: str, video_index: int, loop_videos: bool):
        try:
            # Get all video files from the folder
            video_files = self.get_video_files(folder_path)
            
            if not video_files:
                error_msg = f"No video files found in folder: {folder_path}"
                return (error_msg, "No videos found", 0, 0)
            
            total_videos = len(video_files)
            
            # Handle index
            if loop_videos and total_videos > 0:
                # Wrap around if index is out of bounds
                current_index = video_index % total_videos
            else:
                # Clamp to valid range
                current_index = max(0, min(video_index, total_videos - 1))
            
            # Get the selected video
            selected_video_path = video_files[current_index]
            video_filename = os.path.basename(selected_video_path)
            
            return (selected_video_path, video_filename, current_index, total_videos)
            
        except Exception as e:
            error_msg = f"Error loading video: {str(e)}"
            return (error_msg, "Error", 0, 0)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when video_index changes
        return kwargs.get("video_index", 0)


class SimpleVideoLoop:
    """
    Simple video looper - automatically increments through videos like SimpleCharacterLoop
    """
    
    # Common video file extensions
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', '.3gp', '.ts'}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "input", 
                    "tooltip": "Folder path relative to ComfyUI input directory, or absolute path"
                }),
                "loop_count": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 10000, 
                    "step": 1,
                    "tooltip": "Increment this to go to next video"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("video_path", "video_filename", "loop_info")
    
    FUNCTION = "loop_video"
    CATEGORY = "Video Loader"
    
    def get_video_files(self, folder_path: str) -> List[str]:
        """Get all video files from the specified folder"""
        video_files = []
        
        # Handle relative paths (relative to input directory)
        if not os.path.isabs(folder_path):
            if folder_path.startswith("input/") or folder_path.startswith("input\\"):
                # Remove "input/" prefix and join with input directory
                relative_path = folder_path[6:]  # Remove "input/"
                full_path = os.path.join(folder_paths.get_input_directory(), relative_path)
            elif folder_path == "input":
                full_path = folder_paths.get_input_directory()
            else:
                full_path = os.path.join(folder_paths.get_input_directory(), folder_path)
        else:
            full_path = folder_path
        
        try:
            if os.path.exists(full_path) and os.path.isdir(full_path):
                for filename in sorted(os.listdir(full_path)):
                    file_path = os.path.join(full_path, filename)
                    if os.path.isfile(file_path):
                        # Check if file has video extension
                        _, ext = os.path.splitext(filename.lower())
                        if ext in self.VIDEO_EXTENSIONS:
                            video_files.append(os.path.join(full_path, filename))
        except Exception as e:
            print(f"Error reading folder {full_path}: {str(e)}")
        
        return video_files
    
    def loop_video(self, folder_path: str, loop_count: int):
        try:
            # Get all video files from the folder
            video_files = self.get_video_files(folder_path)
            
            if not video_files:
                error_msg = f"No video files found in folder: {folder_path}"
                return (error_msg, "No videos found", "No videos in folder")
            
            total_videos = len(video_files)
            current_index = loop_count % total_videos
            
            # Get the selected video
            selected_video_path = video_files[current_index]
            video_filename = os.path.basename(selected_video_path)
            
            loop_info = f"Video {current_index + 1} of {total_videos}: {video_filename}"
            
            return (selected_video_path, video_filename, loop_info)
            
        except Exception as e:
            error_msg = f"Error loading video: {str(e)}"
            return (error_msg, "Error", error_msg)
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force re-execution when loop_count changes
        return kwargs.get("loop_count", 0)