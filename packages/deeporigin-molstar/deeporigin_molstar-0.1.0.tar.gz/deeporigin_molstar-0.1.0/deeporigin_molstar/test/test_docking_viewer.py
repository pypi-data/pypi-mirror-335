import unittest
from unittest.mock import patch
from pathlib import Path
import deeporigin_molstar
from deeporigin_molstar.src.viewers import DockingViewer, ProteinConfig, LigandConfig, ProteinViewer

class TestDockingViewer(unittest.TestCase):

    def setUp(self):
        self.path = Path(deeporigin_molstar.__path__[0])
        self.viewer = DockingViewer()

    def test_render_merged_structures_with_default_configs(self):
        protein_data = f"{self.path.parent}/examples/1eby.pdb"
        protein_format = "pdb"
        ligands_data = [f"{self.path.parent}/examples/molecule.mol2"]
        ligand_format = "mol2"

        result = self.viewer.render_merged_structures(
            protein_data, protein_format, ligands_data, ligand_format
        )
        with open(f"{self.path}/test/static/render_docking_default.html", "r") as fd:
            fixture = fd.read()

        self.assertEqual(fixture, result)


    def test_render_merged_structures_with_custom_configs(self):
        protein_data = f"{self.path.parent}/examples/1eby.pdb"
        protein_format = "pdb"
        ligands_data = [f"{self.path.parent}/examples/molecule.mol2"]
        ligand_format = "mol2"
        protein_config = ProteinConfig(style_type="molecular-surface", surface_alpha=0.5)
        ligand_config = LigandConfig(style_type="ball-and-stick", surface_alpha=0.8)


        result = self.viewer.render_merged_structures(
            protein_data, protein_format, ligands_data, ligand_format,
            protein_config=protein_config, ligand_config=ligand_config
        )
        with open(f"{self.path}/test/static/render_docking_custom_config.html", "r") as fd:
            fixture = fd.read()

        self.assertEqual(fixture, result)

    def test_render_merged_structures_with_pocket(self):
        protein_data = f"{self.path.parent}/examples/1eby.pdb"
        protein_format = "pdb"
        ligands_data = [f"{self.path.parent}/examples/molecule.mol2"]
        ligand_format = "mol2"
        protein_config = ProteinConfig(style_type="molecular-surface", surface_alpha=0)
        ligand_config = LigandConfig(style_type="ball-and-stick", surface_alpha=0.8)


        result = self.viewer.render_merged_structures(
            protein_data, protein_format, ligands_data, ligand_format,
            protein_config=protein_config, ligand_config=ligand_config,
            finalize=False
        )

        protein_viewer = ProteinViewer(data="", format="pdb", html=result)
        pocket_config = protein_viewer.get_pocket_visualization_config()
        pocket_config.style_type = "molecular-surface"
        pocket_config.surface_alpha = 0.5

        result = protein_viewer.render_protein_with_pockets(
            pocket_paths=[f"{self.path.parent}/examples/pockets/1EBY_red_pocket.pdb"], 
            pocket_config=pocket_config
        )

        with open(f"{self.path}/test/static/render_docking_with_pocket_custom_config.html", "r") as fd:
            fixture = fd.read()

        self.assertEqual(fixture, result)

if __name__ == '__main__':
    unittest.main()