from pathlib import Path

from deeporigin_molstar.src.viewers.viewer import Viewer

DEFAULT_SURFACE_COLORS = {
    'red': ('Red', "0xFF0000"),
    'green': ('Green', "0x008000"),
    'blue': ('Blue', "0x0403FF"),
    'yellow': ('Yellow', "0xFFFF00"),
    'magenta': ('Magenta', "0xFF00FF"),
    'cyan': ('Cyan', "0x00FFFF"),
    'orange': ('Orange', "0xFFA500"),
    'celeste': ('Celeste', "0xb2FFFF"),
    'purple': ('Purple', "0x800080"),
    'brown': ('Brown', "0xA52A2A"),
    'darkred': ('DarkRed', '0x8B0000'),
    'darkgreen': ('DarkGreen', '0x006400'),
    'darkblue': ('DarkBlue', '0x00008B'),
    'darkorchid': ('DarkOrchid', '0x9932CC'),
    'firebrick': ('Firebrick', '0xB22222'),
    'chocolate': ('Chocolate', '0xD2691E'),
    'midnightblue': ('MidnightBlue', '0x191970'),
    'forestgreen': ('ForestGreen', '0x228B22'),
    'seagreen': ('SeaGreen', '0x2E8B57'),
    'mediumslateblue': ('MediumSlateBlue', '0x7B68EE'),
    'lightseagreen': ('LightSeaGreen', '0x20B2AA'),
    'darkkhaki': ('DarkKhaki', '0xBDB76B'),
    'indigo': ('Indigo', '0x4B0082'),
    'cadetblue': ('CadetBlue', '0x5F9EA0'),
    'teal': ('Teal', '0x008080'),
    'deepskyblue': ('DeepSkyBlue', '0x00BFFF'),
    'lawngreen': ('LawnGreen', '0x7CFC00'),
    'gold': ('Gold', '0xFFD700'),
    'chartreuse': ('Chartreuse', '0x7FFF00'),
    'mediumaquamarine': ('MediumAquamarine', '0x66CDAA'),
    'violet': ('Violet', '0x8A2BE2'),
    'pink': ('Pink', '0xFFC0CB'),
    'salmon': ('Salmon', '0xFA8072'),
    'orchid': ('Orchid', '0xDA70D6'),
    'plum': ('Plum', '0xDDA0DD'),
    'coral': ('Coral', '0xFF7F50'),
    'hotpink': ('HotPink', '0xFF69B4'),
    'mediumvioletred': ('MediumVioletRed', '0xC71585'),
    'fuchsia': ('Fuchsia', '0xFF00FF'),
    'moccasin': ('Moccasin', '0xFFE4B5'),
    'peachpuff': ('PeachPuff', '0xFFDAB9'),
    'wheat': ('Wheat', '0xF5DEB3'),
    'antiquewhite': ('AntiqueWhite', '0xFAEBD7'),
    'lavender': ('Lavender', '0xE6E6FA'),
    'lightskyblue': ('LightSkyBlue', '0x87CEFA'),
    'mediumseagreen': ('MediumSeaGreen', '0x3CB371'),
    'lightsalmon': ('LightSalmon', '0xFFA07A'),
    'lightpink': ('LightPink', '0xFFB6C1'),
    'crimson': ('Crimson', '0xDC143C'),
    'goldenrod': ('Goldenrod', '0xDAA520'),
    'yellowgreen': ('YellowGreen', '0x9ACD32'),
    'darkslateblue': ('DarkSlateBlue', '0x483D8B'),
    'lightblue': ('LightBlue', '0xADD8E6'),
    'skyblue': ('SkyBlue', '0x87CEEB'),
    'darkviolet': ('DarkViolet', '0x9400D3'),
    'slateblue': ('SlateBlue', '0x6A5ACD'),
    'darkgoldenrod': ('DarkGoldenrod', '0xB8860B'),
    'tan': ('Tan', '0xD2B48C'),
    'lightcoral': ('LightCoral', '0xF08080'),
    'mediumblue': ('MediumBlue', '0x0000CD'),
    'blueviolet': ('BlueViolet', '0x8A2BE2'),
    'slategray': ('SlateGray', '0x708090'),
    'yellow': ('Yellow', '0xFFFF00'),
    'greenyellow': ('GreenYellow', '0xADFF2F'),
    'mediumorchid': ('MediumOrchid', '0xBA55D3'),
    'darksalmon': ('DarkSalmon', '0xE9967A'),
    'lightgreen': ('LightGreen', '0x90EE90'),
    'seashell': ('Seashell', '0xFFF5EE'),
    'honeydew': ('Honeydew', '0xF0FFF0'),
    'floralwhite': ('FloralWhite', '0xFFFAF0'),
    'ivory': ('Ivory', '0xFFFFF0'),
    'aliceblue': ('AliceBlue', '0xF0F8FF'),
    'snow': ('Snow', '0xFFFAFA'),
    'azure': ('Azure', '0xF0FFFF'),
    'lightcyan': ('LightCyan', '0xE0FFFF'),
    'mintcream': ('MintCream', '0xF5FFFA'),
    'beige': ('Beige', '0xF5F5DC'),
    'lightgoldenrodyellow': ('LightGoldenrodYellow', '0xFAFAD2'),
    'palegoldenrod': ('PaleGoldenrod', '0xEEE8AA'),
    'mediumspringgreen': ('MediumSpringGreen', '0x00FA9A'),
    'darkorange': ('DarkOrange', '0xFF8C00'),
    'royalblue': ('RoyalBlue', '0x4169E1'),
    'periwinkle': ('Periwinkle', '0xCCCCFF'),
    'mediumturquoise': ('MediumTurquoise', '0x48D1CC'),
    'limegreen': ('LimeGreen', '0x32CD32'),
    'springgreen': ('SpringGreen', '0x00FF7F'),
    'lightsteelblue': ('LightSteelBlue', '0xB0C4DE'),
    'turquoise': ('Turquoise', '0x40E0D0'),
    'amber': ('Amber', '0xFFBF00'),
    'mint': ('Mint', '0x98FF98'),
    'aquamarine': ('Aquamarine', '0x7FFFD4'),
    'peach': ('Peach', '0xFFDAB9'),
    'lavenderblush': ('LavenderBlush', '0xFFF0F5'),
    'linen': ('Linen', '0xFAF0E6'),
    'blanchedalmond': ('BlanchedAlmond', '0xFFEBCD'),
    'darkturquoise': ('DarkTurquoise', '0x00CED1'),
    'chartreuseyellow': ('ChartreuseYellow', '0xDFFF00'),
    'lightgoldenrod': ('LightGoldenrod', '0xFAFAD2'),
    'darkslategray': ('DarkSlateGray', '0x2F4F4F'),
    'blush': ('Blush', '0xDE5D6D'),
    'papayawhip': ('PapayaWhip', '0xFFEFD5'),
}

DEFAULT_PROTEIN_FORMATS = ['pdb', 'pdbqt']
DEFAULT_MUTAGENS_COLORS: dict[str, str] = {
    "all": "#ffffff",  # White
    "gap": "#0000ff",  # Blue
    "mutation": "#ffa500"  # Orange
}


class ProteinConfig:
    def __init__(self, data_label='protein', style_type='cartoon', surface_alpha=0,
                 label_alpha=0, remove_crystal=False, ligand_style_type='ball-and-stick'):
        self.data_label = data_label
        self.style_type = style_type
        self.surface_alpha = surface_alpha
        self.label_alpha = label_alpha
        self._remove_crystal = remove_crystal
        self.ligand_style_type = ligand_style_type
        self.validate_attributes()

    def validate_attributes(self):
        """
        Validates the attributes of the protein viewer.

        Raises:
            ValueError: If the protein representation type is unknown.
            ValueError: If the ligand representation type is unknown.
            ValueError: If the label alpha is not between 0 and 1.
            ValueError: If the surface alpha is not between 0 and 1.
            ValueError: If the remove crystal flag is not a boolean.
        """
        allowed_styles = ['cartoon', 'backbone', 'gaussian-surface', 'line', 'label', 'molecular-surface']
        if self.style_type not in allowed_styles:
            raise ValueError(f"Unknown protein representation type: {self.style_type}")
        if self.ligand_style_type not in allowed_styles + ['ball-and-stick', 'orientation']:
            raise ValueError(f"Unknown ligand representation type: {self.ligand_style_type}")
        if not (0 <= self.label_alpha <= 1):
            raise ValueError("Label alpha must be between 0 and 1.")
        if not (0 <= self.surface_alpha <= 1):
            raise ValueError("Surface alpha must be between 0 and 1.")
        if not isinstance(self._remove_crystal, bool):
            raise ValueError("Remove crystal must be a boolean.")

    @property
    def remove_crystal(self):
        """
        Returns a string representation of whether the crystal should be removed or not.

        Returns:
            str: 'true' if the crystal should be removed, 'false' otherwise.
        """
        return 'true' if self._remove_crystal else 'false'


class PocketConfig:
    def __init__(self, style_type='gaussian-surface', surface_colors=None, surface_alpha=1):
        self.style_type = style_type
        self.surface_alpha = surface_alpha
        self.surface_colors = surface_colors or list(DEFAULT_SURFACE_COLORS.keys())
        self.validate_attributes()

    def validate_attributes(self):
        """
        Validates the attributes of the protein viewer.

        Raises:
            ValueError: If the style type is not one of the allowed styles.
            ValueError: If the surface alpha is not between 0 and 1.
        """
        allowed_styles = ['gaussian-surface', 'gaussian-volume', 'molecular-surface']
        if self.style_type not in allowed_styles:
            raise ValueError(f"Unknown pocket representation type: {self.style_type}")
        if not (0 <= self.surface_alpha <= 1):
            raise ValueError("Surface alpha must be between 0 and 1.")


DEFAULT_PROTEIN_CONFIG = ProteinConfig()
DEFAULT_POCKET_CONFIG = PocketConfig()


class ProteinViewer(Viewer):
    def __init__(self, data: str, format: str = '', html: str = ''):
        if format != '' and format not in DEFAULT_PROTEIN_FORMATS:
            raise AttributeError("Protein format should be either pdb or pdbqt.")
        super().__init__(data, format, html)

    def render_active_site(self):
        """
        Renders the active site of the protein.

        Returns:
            str: The HTML representation of the rendered active site.
        """
        js_code = f"""
            const proteinData = `{self.data}`;
            const format = `{self.format}`;
            await Renderer.renderProteinActiveSite(proteinData, format);
        """
        self.add_component(js_code)
        self.add_suffix()

        return self.html

    def render_protein_mutagens_result(self, residue_gaps: list, residue_mutations: list):
        """
        Renders the protein mutagens analyze result.

        Args:
            residue_gaps (list): A list of residue gaps.
            residue_mutations (list): A list of residue mutations.

        Returns:
            str: The HTML representation of the rendered protein mutagenesis result.
        """
        js_code = f"""
            const proteinData = `{self.data}`;
            const format = `{self.format}`;
            const residueGaps = {residue_gaps};
            const residueMutations = {residue_mutations};
            await Renderer.renderProteinMutagenResult(
                proteinData,
                format,
                residueGaps,
                residueMutations,
            );
        """
        self.add_component(js_code)
        self.add_suffix()

        return self.html

    @staticmethod
    def get_protein_visualization_config():
        """
        Returns the configuration for protein visualization.

        Returns:
            ProteinConfig: The configuration object for protein visualization.
        """
        return ProteinConfig()

    @staticmethod
    def get_pocket_visualization_config():
        """
        Returns the configuration for pocket visualization.

        :return: PocketConfig object representing the configuration for pocket visualization.
        """
        return PocketConfig()

    def render_protein_with_pockets(
            self,
            pocket_paths: list = None,
            protein_config: ProteinConfig = None,
            pocket_config: PocketConfig = None,
            finalize=True
    ):
        """
        Renders the protein structure with pockets.

        Args:
            pocket_paths (list, optional): List of paths to the pocket files. Defaults to None.
            protein_config (ProteinConfig, optional): Configuration for protein visualization. Defaults to None.
            pocket_config (PocketConfig, optional): Configuration for pocket visualization. Defaults to None.
            finalize (bool, optional): Flag indicating whether to finalize the rendering. Defaults to True.

        Returns:
            str: The rendered HTML.

        """
        if protein_config is None:
            protein_config = self.get_protein_visualization_config()

        if pocket_config is None:
            pocket_config = self.get_pocket_visualization_config()

        js_code = f"""
            var proteinData = `{self.data}`;
            var pocket_surface_alpha = {pocket_config.surface_alpha};
            var structureFormat = '{self.format}';
            var pocketFormat = 'pdb';
            const pocketDataList = [
        """
        if pocket_paths:
            for j in range(len(pocket_paths)):
                pocket_data, pocket_format = self.load_from_file(pocket_paths[j])
                pocket_data = ("{ data: `pocket_data`.trim(), color: { name: 'uniform', value: 'pocket_color' }, "
                               "label: 'pocket_name Pocket' },\n").replace(
                    "pocket_data", pocket_data
                ).replace(
                    "pocket_color", DEFAULT_SURFACE_COLORS[pocket_config.surface_colors[j]][1]
                ).replace(
                    "pocket_name", DEFAULT_SURFACE_COLORS[pocket_config.surface_colors[j]][0]
                )

                js_code += pocket_data
        js_code += f"""];\n
            await Renderer.renderStructureAndPockets(
                proteinData, 
                structureFormat, 
                pocketDataList, 
                pocketFormat,
                '{pocket_config.style_type}',
                'protein',
                '{protein_config.style_type}',
                {protein_config.surface_alpha},
                {protein_config.remove_crystal},
                '{protein_config.ligand_style_type}',
                {pocket_config.surface_alpha}
            );
        """
        self.add_component(js_code)
        if finalize:
            self.add_suffix()
        return self.html

    def render_protein(self, protein_config: ProteinConfig = None, finalize=True):
        """
        Renders the protein visualization based on the provided protein configuration.

        Args:
            protein_config (ProteinConfig, optional): The protein configuration to use for visualization.
                If not provided, the default protein visualization configuration will be used.
            finalize (bool, optional): Indicates whether to finalize the rendering process by adding a suffix.
                Defaults to True.

        Returns:
            str: The HTML representation of the rendered protein visualization.
        """
        if protein_config is None:
            protein_config = self.get_protein_visualization_config()

        js_code = f"""
            const proteinData = `{self.data}`;
            const format = `{self.format}`;
            await Renderer.renderStructureExplicitly(
                proteinData, 
                format, 
                '{protein_config.data_label}', 
                '{protein_config.style_type}',
                {protein_config.surface_alpha}, 
                {protein_config.label_alpha}, 
                {protein_config.remove_crystal}, 
                '{protein_config.ligand_style_type}'
            );
        """
        self.add_component(js_code)

        if finalize:
            self.add_suffix()
        return self.html

    @staticmethod
    def render_structures_overlaying(first_raw_data, second_raw_data, first_format, second_format, colors=None, path=None):
        """
        Renders and overlays two protein structures using the Mol* viewer.

        Args:
            first_raw_data (str): The raw data of the first protein structure.
            second_raw_data (str): The raw data of the second protein structure.
            first_format (str): The format of the first protein structure data.
            second_format (str): The format of the second protein structure data.
            colors (dict, optional): A dictionary specifying the colors for the first and second structures.
                Defaults to None, in which case default colors will be used.
            path (str, optional): The path to save the rendered structure. Defaults to None.

        Returns:
            str: The HTML representation of the rendered protein structures.

        """
        viewer = Viewer(data='', format='pdb')

        def prepare_data(viewer_obj, raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return viewer_obj.load_from_file(raw, _format)
            return viewer_obj.load_from_data(raw, _format)

        if colors is None:
            colors = {'first': '0x0000FF', 'second': '0xFFA500'}

        raw_source = [
            {'raw': first_raw_data, 'format': first_format},
            {'raw': second_raw_data, 'format': second_format}
        ]
        sources = [prepare_data(viewer, source['raw'], source['format']) for source in raw_source]
        js_code = f"""
            await Renderer.renderStructuresOverlayingResult(
                `{sources[0][0]}`,
                `{sources[1][0]}`,
                '{sources[0][1]}',
                '{sources[1][1]}',
                {{
                    first: {colors['first']},
                    second: {colors['second']}
                }}
            );
        """
        viewer.add_component(js_code)
        viewer.add_suffix()

        if path is not None:
            viewer.write(path)

        return viewer.html
