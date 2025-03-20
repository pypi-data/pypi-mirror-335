from deeporigin_molstar.src.viewers.viewer import Viewer


class LigandConfig:
    def __init__(self, data_label="docked_ligand", style_type='ball-and-stick', surface_alpha=0, label_alpha=0):
        self.data_label = data_label
        self.style_type = style_type
        self.surface_alpha = surface_alpha
        self.label_alpha = label_alpha
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
        allowed_styles = ['cartoon', 'backbone', 'gaussian-surface', 'line', 'label', 'molecular-surface', 'ball-and-stick', 'orientation']
        if self.style_type not in allowed_styles:
            raise ValueError(f"Unknown protein representation type: {self.style_type}")
        if not (0 <= self.label_alpha <= 1):
            raise ValueError("Label alpha must be between 0 and 1.")
        if not (0 <= self.surface_alpha <= 1):
            raise ValueError("Surface alpha must be between 0 and 1.")


DEFAULT_LIGAND_CONFIG = LigandConfig()


class MoleculeViewer(Viewer):
    def __init__(self, data: str, format: str, html: str = ''):
        super().__init__(data, format, html)
        if format not in ['pdb', 'pdbqt', 'mol2', 'sdf', 'mol']:
            raise ValueError("Unsupported molecule format: {}".format(format))

    def get_ligand_visualization_config(self):
        """
        Returns the configuration for pocket visualization.

        :return: PocketConfig object representing the configuration for pocket visualization.
        """
        return LigandConfig()


    def render_ligand(self, ligand_config: LigandConfig = None, finalize: bool=True):
        """
        Renders the ligand using the provided data and format.

        Args:
            finalize (bool, optional): Indicates whether to finalize the rendering. 
                Defaults to True.
            ligand_config (LigandConfig, optional): The configuration for ligand visualization.

        Returns:
            str: The HTML representation of the rendered ligand.
        """
        if ligand_config is None:
            ligand_config = self.get_ligand_visualization_config()

        js_code = f"""
            const moleculeData = `{self.data}`;
            const ligandFormat = `{self.format}`;
            await Renderer.renderLigand(moleculeData, ligandFormat);
        """
        self.add_component(js_code)
        if finalize:
            self.add_suffix()

        return self.html
