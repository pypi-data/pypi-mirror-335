from IPython.display import display, HTML
from typing import Union

from deeporigin_molstar.src.viewers import Viewer


class JupyterViewer:
    @classmethod
    def visualize(cls, result: Union[str, Viewer]):
        html = result
        if isinstance(result, Viewer):
            html = result.html

        if html:
            iframe_code = f"""
                <iframe srcdoc="{html.replace('"', '&quot;')}" 
                        style="width:100%; height:600px; border:0;">
                </iframe>
            """
            return display(HTML(iframe_code))
        else:
            return None

