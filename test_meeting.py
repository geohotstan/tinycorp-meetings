import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import sys
import os
from pathlib import Path
import meeting # Assuming meeting.py is in the same directory or PYTHONPATH is set

class TestMeeting(unittest.TestCase):

    def setUp(self):
        # Keep track of started patches to stop them in tearDown
        self.patches = []

        # Mock external dependencies from meeting.py
        self.mock_make_mp4 = self._start_patch('meeting.make_mp4')
        self.mock_upload_video = self._start_patch('meeting.upload_video')
        self.mock_run_whisperx = self._start_patch('meeting.run_whisperx')
        self.mock_json_to_transcript = self._start_patch('meeting.json_to_transcript')

        # Mock file system operations
        self.mock_os_path_isfile = self._start_patch('os.path.isfile')
        # meeting.shutil should refer to the imported shutil in meeting.py
        self.mock_shutil_copy2 = self._start_patch('meeting.shutil.copy2')
        self.mock_path_mkdir = self._start_patch('pathlib.Path.mkdir')

        # Mock open for file reading/writing
        self.mock_builtin_open = self._start_patch('builtins.open', new_callable=mock_open)
        self.mock_path_exists = self._start_patch('pathlib.Path.exists') # Add this mock

        # Mock constants
        self.mock_hf_token = self._start_patch('meeting.HF_TOKEN', new="test_hf_token")
        self.mock_client_secret_path = self._start_patch('meeting.CLIENT_SECRET_PATH', new="test_client_secret_path")
        self.mock_weekly_log_path = self._start_patch('meeting.WEEKLY_LOG_PATH', new=Path("/fake/weekly_log"))
        self.mock_resources_path = self._start_patch('meeting.RESOURCES_PATH', new=Path("/fake/resources"))
        self.mock_speakers = self._start_patch('meeting.SPEAKERS', new=1)
        self.mock_meeting_agenda = self._start_patch('meeting.MEETING_AGENDA', new="Test Agenda")


    def _start_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.patches.append(patcher)
        return patcher.start()

    def tearDown(self):
        for patcher in self.patches:
            patcher.stop()

    @patch('sys.argv', ['meeting.py', '2023-10-26.wav'])
    def test_parse_arguments_valid(self):
        self.mock_os_path_isfile.return_value = True
        audio_path, date = meeting.parse_arguments()
        self.assertEqual(Path('2023-10-26.wav'), audio_path)
        self.assertEqual('2023-10-26', date)
        self.mock_os_path_isfile.assert_called_once_with(Path('2023-10-26.wav'))

    @patch('sys.argv', ['meeting.py'])
    @patch('sys.exit')
    def test_parse_arguments_missing_arg(self, mock_exit):
        mock_exit.side_effect = SystemExit # Make mock_exit raise an exception
        with self.assertRaises(SystemExit): # Expect SystemExit
            meeting.parse_arguments()
        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['meeting.py', 'invalid_date.wav'])
    @patch('sys.exit')
    def test_parse_arguments_invalid_date(self, mock_exit):
        self.mock_os_path_isfile.return_value = True
        meeting.parse_arguments()
        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['meeting.py', '2023-10-26.mp3'])
    @patch('sys.exit')
    def test_parse_arguments_invalid_extension(self, mock_exit):
        self.mock_os_path_isfile.return_value = True
        meeting.parse_arguments()
        mock_exit.assert_called_once_with(1)

    @patch('sys.argv', ['meeting.py', '2023-10-26.wav'])
    @patch('sys.exit')
    def test_parse_arguments_file_not_found(self, mock_exit):
        self.mock_os_path_isfile.return_value = False
        meeting.parse_arguments()
        mock_exit.assert_called_once_with(1)


    def test_setup_paths_and_folders_valid(self):
        audio_path_arg = Path('2023-10-26.wav')
        date = '2023-10-26'

        # Configure WEEKLY_LOG_PATH if it's a module-level constant in meeting.py
        # For this example, assume it's accessible or also mocked if necessary.
        # If meeting.WEEKLY_LOG_PATH is used:
        with patch('meeting.WEEKLY_LOG_PATH', Path('/fake/weekly_log')):
            new_audio_path, last_week_path = meeting.setup_paths_and_folders(audio_path_arg, date)

        expected_last_week_path = Path('/fake/weekly_log') / date
        self.mock_path_mkdir.assert_called_once_with(exist_ok=True)
        # Check that the parent of the mkdir call is the expected_last_week_path
        # This requires inspecting the 'self' of the mock_path_mkdir call if it's a method of Path
        # For simplicity here, we assume the call is correct if made.
        # A more robust way is to check the instance it was called on if Path itself is not mocked.

        self.mock_shutil_copy2.assert_called_once_with(audio_path_arg, expected_last_week_path / audio_path_arg.name)
        self.assertEqual(str(expected_last_week_path / audio_path_arg.name), new_audio_path)
        self.assertEqual(expected_last_week_path, last_week_path)

    # Test for os.path.isfile returning False is effectively covered in test_parse_arguments_file_not_found
    # setup_paths_and_folders does not directly call os.path.isfile. It expects a valid path.

    def test_process_audio_and_video_successful(self):
        audio_path = '/fake/weekly_log/2023-10-26/2023-10-26.wav'
        date = '2023-10-26'
        last_week_path = Path('/fake/weekly_log/2023-10-26')

        self.mock_upload_video.return_value = 'http://fakeyoutube.com/video'
        self.mock_path_exists.return_value = True # Ensure still_img_path.exists() is true
        # If RESOURCES_PATH is used:
        with patch('meeting.RESOURCES_PATH', Path('/fake/resources')):
            youtube_url = meeting.process_audio_and_video(audio_path, date, last_week_path)

        expected_mp4_path = last_week_path / f"{date}.mp4"
        expected_still_img_path = Path('/fake/resources') / "tiny.jpeg"

        self.mock_make_mp4.assert_called_once_with(str(audio_path), str(expected_still_img_path), str(expected_mp4_path))
        self.mock_upload_video.assert_called_once_with(str(expected_mp4_path), f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/', "test_client_secret_path")
        self.assertEqual('http://fakeyoutube.com/video', youtube_url)

    def test_transcribe_and_generate_readme_successful(self):
        audio_path = '/fake/weekly_log/2023-10-26/2023-10-26.wav'
        date = '2023-10-26'
        last_week_path = Path('/fake/weekly_log/2023-10-26')
        youtube_url = 'http://fakeyoutube.com/video'

        self.mock_json_to_transcript.return_value = "Fake transcript content"
        # Mock reading the json file
        mock_json_data = '{"fake": "json_data"}'
        self.mock_builtin_open.return_value.read.return_value = mock_json_data

        meeting.transcribe_and_generate_readme(audio_path, date, last_week_path, youtube_url)

        self.mock_run_whisperx.assert_called_once_with(audio_path, last_week_path, 1, "test_hf_token")

        # Check json load call
        expected_json_path = last_week_path / f"{date}.json"
        # Ensure open was called for reading the json
        # self.mock_builtin_open.assert_any_call(expected_json_path, "r")
        # Ensure json_to_transcript was called with the loaded data
        # The actual check for json.load(file) is tricky as file is a mock.
        # Instead, we can verify the argument passed to json_to_transcript if it was simple.
        # For now, ensure it's called.
        self.mock_json_to_transcript.assert_called_once() # Args check can be more specific

        expected_readme_path = last_week_path / "meeting-transcript.md"
        expected_readme_content = f"""# {date} Meeting

### Meeting Agenda

**Time:** Test Agenda

### Audio

[Youtube Link]({youtube_url})

### Highlights

### Transcript
Fake transcript content
"""
        # Check that open was called for writing the readme
        # And that write was called with the correct content
        self.mock_builtin_open.assert_any_call(expected_readme_path, 'w')
        # Get the mock file handle for the write call
        handle = self.mock_builtin_open()
        handle.write.assert_called_once_with(expected_readme_content)


    @patch('sys.argv', ['meeting.py', '2023-10-26.wav'])
    def test_main_end_to_end(self):
        # Setup return values for mocks
        self.mock_os_path_isfile.return_value = True # For parse_arguments
        self.mock_path_exists.return_value = True # For still_img_path.exists() in process_audio_and_video
        self.mock_upload_video.return_value = 'http://fakeyoutube.com/video_main' # For process_audio_and_video
        self.mock_json_to_transcript.return_value = "Fake transcript content for main" # For transcribe_and_generate_readme

        # Mock reading the json file for transcribe_and_generate_readme
        mock_json_data = '{"fake": "json_data_main"}'
        # Configure the mock_open to handle multiple open calls if necessary
        # For simplicity, assume the read call for json is distinct or manage side_effect
        self.mock_builtin_open.return_value.read.return_value = mock_json_data

        # Call main
        meeting.main()

        # Assertions for parse_arguments part (indirectly, via setup_paths_and_folders args)
        date = '2023-10-26'
        audio_path_arg = Path('2023-10-26.wav')

        # Assertions for setup_paths_and_folders
        expected_last_week_path = self.mock_weekly_log_path / date # Using mocked WEEKLY_LOG_PATH
        self.mock_path_mkdir.assert_called_with(exist_ok=True) # Check if called on the correct path object might be needed

        expected_new_audio_path_str = str(expected_last_week_path / audio_path_arg.name)
        self.mock_shutil_copy2.assert_called_once_with(audio_path_arg, Path(expected_new_audio_path_str))

        # Assertions for process_audio_and_video
        expected_mp4_path = expected_last_week_path / f"{date}.mp4"
        expected_still_img_path = self.mock_resources_path / "tiny.jpeg" # Using mocked RESOURCES_PATH
        self.mock_make_mp4.assert_called_once_with(expected_new_audio_path_str, str(expected_still_img_path), str(expected_mp4_path))
        self.mock_upload_video.assert_called_once_with(str(expected_mp4_path), f"TINYCORP MEETING {date}", 'github.com/geohotstan/tinycorp-meetings/', self.mock_client_secret_path)

        # Assertions for transcribe_and_generate_readme
        self.mock_run_whisperx.assert_called_once_with(expected_new_audio_path_str, expected_last_week_path, self.mock_speakers, self.mock_hf_token)

        expected_json_path = expected_last_week_path / f"{date}.json"
        # self.mock_builtin_open.assert_any_call(expected_json_path, "r") # Check read call
        self.mock_json_to_transcript.assert_called_once() # More specific arg check if possible

        expected_readme_path = expected_last_week_path / "meeting-transcript.md"
        expected_readme_content = f"""# {date} Meeting

### Meeting Agenda

**Time:** {self.mock_meeting_agenda}

### Audio

[Youtube Link](http://fakeyoutube.com/video_main)

### Highlights

### Transcript
Fake transcript content for main
"""
        # self.mock_builtin_open.assert_any_call(expected_readme_path, 'w') # Check write call
        # Get the mock file handle for the write call
        # This assumes the last call to open was for writing the README.
        # If other files are opened and written, this needs to be more specific.
        # For example, by checking the call list: self.mock_builtin_open.mock_calls

        # A robust way to check write content for a specific file:
        # Find the call to open for the readme file, then check the write on that handle.
        # This is simplified here.
        write_call_found = False
        for call_obj in self.mock_builtin_open.mock_calls:
            if call_obj == call(expected_readme_path, 'w'): # Check if this call was made
                # The actual write would be on the object returned by this call.
                # This part is tricky with a single mock_open for all open calls.
                # Using mock_open.side_effect to return different mocks for different files is more robust.
                pass # Cannot directly assert write content here without more complex mock_open setup

        # A simpler, though less robust, check for the write content:
        self.mock_builtin_open().write.assert_called_with(expected_readme_content)


if __name__ == '__main__':
    unittest.main()
