import os
import logging
from pathlib import Path


class Viewer:
    MOLSTAR_PREFIX = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
        <link rel="stylesheet" type="text/css" href="https://balto.biosim.ai/molstar/styles.css" />
        <title>Mol* Gallery</title>
    </head>
    <body>
        <div style="margin: 20px">
            <div id="DeepOriginViewer"></div>
        </div>
        <script type="text/javascript" src="https://balto.biosim.ai/molstar/gallery.js"></script>
        <script type="text/javascript">


        async function init() {
            const viewer = new deepOriginMolstar.Viewer('DeepOriginViewer');
            const Renderer = await deepOriginMolstar.Renderer(viewer);
    '''

    MOLSTARSUFFIX = '''
        } 

        init();
        </script>
        </body>
        </html>
    '''

    def __init__(self, data: str, format: str, html: str = ''):
        """
        Initialize the Viewer object.

        Args:
            data (str): The data to be loaded into the viewer. It can be either a file path or raw data.
            format (str): The format of the data. Examples include 'json', 'xml', 'csv', etc.
            html (str, optional): Additional HTML content to be displayed along with the viewer. Defaults to ''.
        """
        self.html = html if html else self.add_prefix()
        self.logger = logging.getLogger(__name__)

        try:
            is_path = Path(data).is_file()
        except (TypeError, OSError):
            is_path = False

        if is_path:
            self.data, self.format = self.load_from_file(data, format)
        else:
            self.data, self.format = self.load_from_data(data, format)

    def load_from_file(self, file_path: str, file_format: str = ''):
        """
        Loads data from a file.

        Args:
            file_path (str): The path to the file.
            file_format (str, optional): The format of the file. Defaults to ''.

        Returns:
            tuple: A tuple containing the loaded data and the file format.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        with open(file_path, 'r') as file:
            data = file.read()

        data = data.replace('\n', '\\n').replace('\t', '\\t')

        extracted_format = file_path.split('.')[-1]
        if file_format == '':
            self.logger.warning(f"Moving forward with extracted file format {extracted_format}.")
            file_format = extracted_format

        if extracted_format != file_format:
            self.logger.warning(f"File format {extracted_format} does not match the specified format {file_format}")

        return data, file_format

    def load_from_data(self, data: str, data_format: str):
        """
        Load data into the viewer from a string.

        Args:
            data (str): The data to be loaded into the viewer.
            data_format (str): The format of the data.

        Returns:
            tuple: A tuple containing the loaded data and its format.
        
        Raises:
            AttributeError: If the data format is not provided.
        """
        data = data.replace('\n', '\\n').replace('\t', '\\t')
        if data_format == '':
            raise AttributeError("Data format is required")
        return data, data_format

    def add_prefix(self):
        """
        Adds a prefix to the MOLSTAR_PREFIX attribute.

        Returns:
            str: The modified MOLSTAR_PREFIX attribute.
        """
        return self.MOLSTAR_PREFIX

    def add_component(self, component: str):
        """
        Adds a component to the viewer's HTML string.

        If the viewer's HTML string ends with the MOLSTARSUFFIX, it means that the viewer has been finalized.
        In that case, the method resets the viewer by setting the HTML string to MOLSTAR_PREFIX.

        Args:
            component (str): The component to be added to the viewer's HTML string.

        Returns:
            None
        """
        if self.html.endswith(self.MOLSTARSUFFIX):
            self.logger.error("Trying to add component on finalized html string, resetting viewer.")
            self.html = self.MOLSTAR_PREFIX

        self.html += (component + '\n')

    def add_suffix(self):
        """
        Adds the MOLSTARSUFFIX to the HTML.

        This method appends the MOLSTARSUFFIX to the existing HTML string.

        Parameters:
        None

        Returns:
        None
        """
        self.html += self.MOLSTARSUFFIX

    def write(self, file_path: str):
        """
        Write the HTML content to a file.

        Args:
            file_path (str): The path to the file where the HTML content will be written.

        Raises:
            ValueError: If the directory for the file path does not exist.
            IOError: If there is an error while writing to the file.

        """
        path = Path(file_path)
        if not path.parent.exists():
            raise ValueError(f"The directory for the file path {file_path} does not exist.")

        if not self.html.endswith(self.MOLSTARSUFFIX):
            self.logger.warning("Html should be closed with molstar suffix. Adding missing part for ensuring validity.")
            self.add_suffix()

        try:
            with open(file_path, 'w') as file:
                file.write(self.html)
        except Exception as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")

