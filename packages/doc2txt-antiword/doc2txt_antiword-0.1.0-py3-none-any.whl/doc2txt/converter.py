import subprocess
import os

class AntiwordConverter:
    def __init__(self):
        self.binary_path = self._get_binary_path()

    def _get_binary_path(self):
        """
        Determine the path to the antiword binary, which will be installed alongside the package.
        """
        # Find the antiword binary in the package bin directory
        current_dir = os.path.dirname(__file__)
        bin_dir = os.path.join(current_dir, 'bin','antiword')
        binary_name = 'antiword.exe'  # For Windows; adjust if using Linux/MacOS
        
        binary_path = os.path.join(bin_dir, binary_name)

        if not os.path.exists(binary_path):
            raise FileNotFoundError(f"Antiword binary not found at {binary_path}")
        
        return binary_path

    def convert_doc_to_txt(self, doc_path, output_dir):
        """
        Convert a .doc file to .txt using antiword binary.
        """
        # Get the current working directory and set HOME
        working_directory = os.getcwd()
        working_directory = os.path.join(working_directory, 'antiword_py','bin')
        print(working_directory)
        os.environ["HOME"] = working_directory

        # Ensure output_dir exists
        os.makedirs(output_dir, exist_ok=True)

        # Get the base filename without extension
        base_filename = os.path.splitext(os.path.basename(doc_path))[0]

        # Set the output .txt file path
        output_txt_path = os.path.join(output_dir, f"{base_filename}.txt")

        # Command to run antiword with the full path
        cmd = [self.binary_path, doc_path]

        try:
            # Open the output file in write mode
            with open(output_txt_path, 'w') as output_file:
                # Run the antiword command and direct output to the file
                subprocess.run(cmd, stdout=output_file, check=True)
            print(f"Conversion successful! Output saved to: {output_txt_path}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during conversion: {e}")

# For testing locally (can be removed for the pip package version)
# if __name__ == "__main__":
#     converter = AntiwordConverter()
#     doc_path = r'antiword_py/01744-ch0002_Release_2024_Jun-28-24-0931 - checked.doc'
#     output_dir = r'antiword_py/output'
#     converter.convert_doc_to_txt(doc_path, output_dir)
