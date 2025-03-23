import subprocess
import os
import importlib.resources

class AntiwordConverter:
    def __init__(self):
        # Initialize the converter by determining the path to the antiword binary
        self.binary_path = self._get_binary_path()

    def _get_binary_path(self):
        """
        Determine the path to the antiword binary.

        This function locates the 'antiword.exe' binary, which is installed alongside the package.
        If the binary cannot be found, it raises a FileNotFoundError.
        
        Returns:
        - The full path to the antiword binary as a string.
        """
        binary_name = 'antiword.exe'  # For Windows; adjust this for Linux/MacOS if needed

        # Locate the 'antiword' binary in the package using importlib.resources
        try:
            bin_dir = importlib.resources.files(__package__) / 'bin/antiword'
            binary_path = bin_dir / binary_name

            # Check if the binary exists at the determined location
            if not binary_path.exists():
                raise FileNotFoundError(f"Antiword binary not found at {binary_path}")

            return str(binary_path)

        except Exception as e:
            raise FileNotFoundError(f"Error locating antiword binary: {str(e)}")

    def convert_doc_to_txt(self, doc_path):
        """
        Convert a .doc file to .txt using the antiword binary.

        Parameters:
        - doc_path: The full path to the input .doc file that needs to be converted.

        Returns:
        - The converted text from the .doc file as a string if successful.
        - None if the conversion fails.

        This function captures the output of the antiword command and returns the text as a string.
        If an error occurs, detailed messages will be printed to the console.
        """
        # Validate that the input .doc file exists
        if not os.path.exists(doc_path):
            print(f"Error: The specified document file does not exist: {doc_path}")
            return None

        # Validate that the input file has the correct .doc extension
        if not doc_path.lower().endswith('.doc'):
            print(f"Error: The specified file is not a .doc file: {doc_path}")
            return None

        # Set up the environment for the antiword binary
        working_directory = os.path.dirname(self.binary_path)  # Directory containing antiword.exe
        parent_directory = os.path.dirname(working_directory)  # Go one level up

        # Set HOME environment variable to the parent directory of the binary
        os.environ["HOME"] = parent_directory

        # Construct the antiword command with the full path to the binary and the input document
        cmd = [self.binary_path, doc_path]

        try:
            # Run the antiword command and capture its output
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True, encoding='utf-8')

            # Return the output text from the .doc file conversion
            return result.stdout

        except subprocess.CalledProcessError as e:
            # Handle the case where the antiword command fails (non-zero exit code)
            print(f"An error occurred during conversion: {e}")
            print(f"Error details: {e.stderr}")
            return None

        except FileNotFoundError:
            # Handle the case where the binary or the input file is not found
            print(f"Error: Antiword binary or document file not found.")
            return None

        except Exception as e:
            # Catch-all for any other exceptions that might occur
            print(f"An unexpected error occurred: {e}")
            return None
