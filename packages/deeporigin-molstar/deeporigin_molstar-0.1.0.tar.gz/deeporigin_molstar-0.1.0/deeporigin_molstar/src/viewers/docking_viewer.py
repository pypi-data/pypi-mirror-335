import json

from pathlib import Path
from deeporigin_molstar.src.viewers.molecule_viewer import LigandConfig
from deeporigin_molstar.src.viewers.protein_viewer import ProteinConfig
from deeporigin_molstar.src.viewers.viewer import Viewer


class DockingViewer(Viewer):
    def __init__(self, html: str = ''):
        """
        Initializes a DockingViewer object.

        Args:
            html (str): The HTML content to be displayed in the viewer.

        """
        super().__init__(
            data='', format='pdb', html=html
        )

    def render_with_seperate_crystal(
            self, 
            protein_data: str, 
            protein_format: str, 
            ligands_data: list[str], 
            ligand_format: str, 
            crystal_data: str = None,
            protein_config: ProteinConfig = None, 
            ligand_config: LigandConfig = None,
            finalize: bool = True
        ):
        """
        Renders merged structures using the provided protein, ligand and native crystal data.

        Args:
            protein_data (str): The protein data to be rendered.
            protein_format (str): The format of the protein data.
            ligand_data (list[str]): The list of ligand data to be rendered.
            ligand_format (str): The format of the ligand data.
            crystal_data (str): The native crystal data, optional

        Returns:
            str: The HTML representation of the rendered structures.
        """

        if not protein_config:
            protein_config = ProteinConfig()

        if not ligand_config:
            ligand_config = LigandConfig()

        if not crystal_data:
            crystal_data = ''

        def prepare_data(raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return self.load_from_file(raw, _format)
            return self.load_from_data(raw, _format)

        representations = [
            {'componentType': 'polymer', 'representationConfig': {'type': protein_config.style_type, 'typeParams': {'alpha': protein_config.surface_alpha, 'quality': 'high'}}},
            {'componentType': 'ligand', 'representationConfig': {'type': ligand_config.style_type, 'typeParams': {'alpha': ligand_config.surface_alpha, 'quality': 'high'}}}
        ]

        formatted_representations = ', '.join(
            f"{{componentType: '{representation['componentType']}', representationConfig: {{type: '{representation['representationConfig']['type']}', typeParams: {{alpha: {representation['representationConfig']['typeParams']['alpha']}, quality: '{representation['representationConfig']['typeParams']['quality']}'}}}}}}"
            for representation in representations
        )

        raw_source = [
            {'raw': protein_data, 'format': protein_format}
        ]
        for data in ligands_data:
            raw_source.append({'raw': data, 'format': ligand_format})

        sources = [prepare_data(source['raw'], source['format']) for source in raw_source]
        formatted_sources = ', '.join([f"{{raw: `{raw}`, format: '{_format}'}}" for raw, _format in sources])
        if crystal_data:
            crystal_from_raw = prepare_data(crystal_data['raw'], crystal_data['format'])
            formatted_crystal = f"{{raw: `{crystal_from_raw[0]}`, format: '{crystal_from_raw[1]}'}}"
        js_code = f"await Renderer.renderStructureWithSeperateCrystal([{formatted_representations}], [{formatted_sources}], Renderer.renderMergedRawStructuresAndMergeWithRepresentation, {formatted_crystal if crystal_data else ''});"
                    
        self.add_component(js_code)
        if finalize:
            self.add_suffix()

        return self.html

    def render_merged_structures(
            self, 
            protein_data: str, 
            protein_format: str, 
            ligands_data: list[str], 
            ligand_format: str, 
            protein_config: ProteinConfig = None, 
            ligand_config: LigandConfig = None, 
            finalize: bool = True
        ):
        """
        Renders merged structures using the provided protein and ligand data.

        Args:
            protein_data (str): The protein data to be rendered.
            protein_format (str): The format of the protein data.
            ligand_data (list[str]): The list of ligand data to be rendered.
            ligand_format (str): The format of the ligand data.

        Returns:
            str: The HTML representation of the rendered structures.
        """

        if not protein_config:
            protein_config = ProteinConfig()

        if not ligand_config:
            ligand_config = LigandConfig()

        def prepare_data(raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return self.load_from_file(raw, _format)
            return self.load_from_data(raw, _format)

        representations = [
            {'componentType': 'polymer', 'representationConfig': {'type': protein_config.style_type, 'typeParams': {'alpha': protein_config.surface_alpha, 'quality': 'high'}}},
            {'componentType': 'ligand', 'representationConfig': {'type': ligand_config.style_type, 'typeParams': {'alpha': ligand_config.surface_alpha, 'quality': 'high'}}}
        ]

        formatted_representations = ', '.join(
            f"{{componentType: '{representation['componentType']}', representationConfig: {{type: '{representation['representationConfig']['type']}', typeParams: {{alpha: {representation['representationConfig']['typeParams']['alpha']}, quality: '{representation['representationConfig']['typeParams']['quality']}'}}}}}}"
            for representation in representations
        )

        raw_source = [
            {'raw': protein_data, 'format': protein_format}
        ]
        for data in ligands_data:
            raw_source.append({'raw': data, 'format': ligand_format})

        sources = [prepare_data(source['raw'], source['format']) for source in raw_source]
        formatted_sources = ', '.join([f"{{raw: `{raw}`, format: '{_format}'}}" for raw, _format in sources])
        js_code = f"await Renderer.renderWithNativeCrystalControl([{formatted_representations}], [{formatted_sources}], Renderer.renderMergedRawStructuresAndMergeWithRepresentation);"
                    
        self.add_component(js_code)
        if finalize:
            self.add_suffix()

        return self.html

    @staticmethod
    def render_ligand_with_bounding_box(protein_data: str, protein_format: str, ligand_data: str, ligand_format: str,
                                        box: dict, path=None):
        viewer = Viewer('', 'pdb')

        def prepare_data(raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return viewer.load_from_file(raw, _format)
            return viewer.load_from_data(raw, _format)

        formatted_box = f"{{min: {box['min']}, max: {box['max']}}}"
        raw_source = [
            {'raw': protein_data, 'format': protein_format},
            {'raw': ligand_data, 'format': ligand_format}
        ]
        sources = [prepare_data(source['raw'], source['format']) for source in raw_source]

        formatted_sources = ', '.join([f"{{raw: `{raw}`, format: '{_format}'}}" for raw, _format in sources])
        js_code = f"await Renderer.renderLigandWidthBoundingBox({formatted_box}, [{formatted_sources}]);"

        viewer.add_component(js_code)
        viewer.add_suffix()

        if path is not None:
            viewer.write(path)

        return viewer.html
    
    @staticmethod
    def render_bounding_box(protein_data: str, protein_format: str, box_center, box_size, path=None):
        viewer = Viewer('', 'pdb')

        def prepare_data(raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return viewer.load_from_file(raw, _format)
            return viewer.load_from_data(raw, _format)


        # Calculate half of the dimensions
        half_dimensions = [d / 2 for d in box_size]

        # Calculate min and max coordinates
        min_coords = [box_center[i] - half_dimensions[i] for i in range(len(box_center))]
        max_coords = [box_center[i] + half_dimensions[i] for i in range(len(box_center))]
        formatted_box = f"{{min: {min_coords}, max: {max_coords}}}"

        raw_source = [
            {'raw': protein_data, 'format': protein_format},
        ]
        sources = [prepare_data(source['raw'], source['format']) for source in raw_source]

        formatted_sources = ', '.join([f"{{raw: `{raw}`, format: '{_format}'}}" for raw, _format in sources])
        js_code = f"await Renderer.renderLigandWidthBoundingBox({formatted_box}, [{formatted_sources}]);"

        viewer.add_component(js_code)
        viewer.add_suffix()

        if path is not None:
            viewer.write(path)

        return viewer.html
    

    @staticmethod
    def render_highligh_residues(protein_data: str, protein_format: str, residue_ids: list):
        viewer = Viewer('', 'pdb')

        def prepare_data(raw, _format):
            try:
                is_path = Path(raw).is_file()
            except (TypeError, OSError):
                is_path = False

            if is_path:
                return viewer.load_from_file(raw, _format)
            return viewer.load_from_data(raw, _format)

        protein_data, protein_format = prepare_data(protein_data, protein_format)
        js_code = f"""
            const proteinData = `{protein_data}`;
            const format = `{protein_format}`;
            const residue_ids = {residue_ids};
            await Renderer.renderProteinPocketBasedOnResidues(
                proteinData, 
                format, 
                residue_ids
            );
        """
        viewer.add_component(js_code)
        viewer.add_suffix()
        
        return viewer.html