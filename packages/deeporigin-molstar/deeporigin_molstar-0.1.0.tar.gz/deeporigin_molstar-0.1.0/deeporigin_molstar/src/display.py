import argparse
import os

from .utils import NotValidPDBPath


JS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gallery.js")


IFRAME_PREFIX = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mol* visualization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        iframe {
            border: none;
            width: 50%;
            height: 100px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h1>Mol* visualization</h1>
    <iframe title="Mol* visualizer"
            width="600"
            height="600"
            srcdoc="
'''


IFRAME_SUFFIX = '''">
    </iframe>
</body>
</html>
'''


MOLSTAR_PREFIX = '''
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
        <title>Mol* Gallery</title>
    </head>
    <body>
        <script type="text/javascript">
'''

JS_PART = '''
        async function init() {
          const viewer = new deepOriginMolstar.Viewer('DeepOriginViewer');
          const Renderer = await deepOriginMolstar.Renderer(viewer);
'''


MOLSTARBODY = '''
    var structureFormat = 'pdb'.trim();
    var pocketFormat = 'pdb'.trim();
    var ligandFormat = 'mol2'.trim();
'''

MOLSTARSUFFIX = '''
        var ligand_type = `ball-and-stick`.trim();
        await molstarGallery.loadStructureExplicitly(plugin, structureData, structureFormat, 'protein', 'cartoon', 0, 0, false, ligand_type);
      } 

      init();
      </script>
  </body>
</html>
'''

IFRAME_V2 = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mol* visualization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        iframe {
            border: none;
            width: 100%;
            height: 500px; /* Adjust the height as needed */
        }
    </style>
</head>
<body>
    <h1>Mol* visualization</h1>
    <iframe src="./temp.html"></iframe>
</body>
</html>
'''


def construct_protein_view(protein_path: str):

    if not os.path.isfile(protein_path):
        raise

    with open(protein_path, "r") as e:
        protein = e.read()

    protein = protein.replace('\n', '\\n')
    protein_data = f'var structureData = `{protein}`.trim();'

    with open(JS_PATH, "r") as file:
        js_data = file.read()

    updated_html = (MOLSTAR_PREFIX + "\n" + js_data + "\n" + JS_PART + "\n" + MOLSTARBODY + "\n" +
                    protein_data + "\n" + MOLSTARSUFFIX)

    return updated_html


def display(protein_path: str, save_path: str, embed_path: str) -> str:
    """
        Construct and display pdb file using Mol* visualization.
    :param protein_path: the path to the pdb
    :param save_path: path where to save the core Mol* visualization html
    :param embed_path: a relative path where you want to show the hrml iframe. It can be the same as `save_path`. In
        jupyter notebook for showing iframes, you need to specify the source file from current directory to make a valid
        visualization.
    :return: string html
    """
    try:
        html_code = construct_protein_view(protein_path)

        with open(save_path, "w") as file:
            file.write(html_code)

        iframe = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Mol* visualization</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                        }}
                        iframe {{
                            border: none;
                            width: 50%;
                            height: 500px; /* Adjust the height as needed */
                        }}
                    </style>
                </head>
                <body>
                    <h1>Mol* visualization</h1>
                    <iframe src="{embed_path}"></iframe>
                </body>
                </html>
            """
        return iframe
    except Exception as e:
        raise NotValidPDBPath(f"The visualization has failed - {str(e)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Display protein wirh MolStar")
    parser.add_argument("--protein_path", help="Path to the protein PDB file")

    args = parser.parse_args()
    html_code = construct_protein_view(args.protein_path)
    print(html_code)