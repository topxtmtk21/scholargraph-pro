# -*- coding: utf-8 -*-
"""
Test Suite: Verify 10 Academic Layouts, 10 Themes, Multi-Layer Combined Filtering & F0 Anchor Pinning
"""
import sys
import unittest
from agents.citenet import CiteNetAgent

class TestGraphLayoutsAndPalettes(unittest.TestCase):
    def setUp(self):
        self.agent = CiteNetAgent()
        self.sample_nodes = {
            "W_SEED": {
                "id": "W_SEED",
                "title": "Quantum Foundations of Deep Learning",
                "authors": "Nguyen Van A, Le Van B",
                "first_author": "Nguyen Van A",
                "year": 2022,
                "venue": "Nature Machine Intelligence",
                "citation_count": 450,
                "level": 0,
                "layer": "seed",
                "scopus_tier": "Scopus Q1",
                "study_type": "Empirical Journalism Study",
                "doi": "10.1038/s42256-022-001",
                "is_oa": True
            },
            "W_R1_A": {
                "id": "W_R1_A",
                "title": "Classical Statistical Learning Theory",
                "authors": "Vapnik V",
                "first_author": "Vapnik V",
                "year": 1998,
                "venue": "IEEE TIT",
                "citation_count": 8900,
                "level": -1,
                "layer": "backward",
                "scopus_tier": "Scopus Q1",
                "study_type": "Theoretical Benchmark",
                "doi": "10.1109/TIT.1998.001",
                "is_oa": False
            },
            "W_R1_B": {
                "id": "W_R1_B",
                "title": "Kernel Methods for Pattern Analysis",
                "authors": "Shawe-Taylor J",
                "first_author": "Shawe-Taylor J",
                "year": 2004,
                "venue": "Cambridge Press",
                "citation_count": 3200,
                "level": -1,
                "layer": "backward",
                "scopus_tier": "Scopus Q1",
                "study_type": "Theoretical Benchmark",
                "doi": "10.1017/CBO9780511809682",
                "is_oa": True
            },
            "W_F1_A": {
                "id": "W_F1_A",
                "title": "Quantum Neural Network Scalability in Vision",
                "authors": "Smith J, Doe A",
                "first_author": "Smith J",
                "year": 2023,
                "venue": "IEEE TPAMI",
                "citation_count": 85,
                "level": 1,
                "layer": "forward",
                "scopus_tier": "Scopus Q1",
                "study_type": "Empirical Journalism Study",
                "doi": "10.1109/TPAMI.2023.001",
                "is_oa": True
            },
            "W_F1_B": {
                "id": "W_F1_B",
                "title": "Empirical Verification of Quantum Generative Models",
                "authors": "Garcia M",
                "first_author": "Garcia M",
                "year": 2023,  # Cùng năm 2023 với W_F1_A để test Same-Year Anti-Collision
                "venue": "NeurIPS",
                "citation_count": 42,
                "level": 1,
                "layer": "forward",
                "scopus_tier": "Scopus Q1",
                "study_type": "Empirical Journalism Study",
                "doi": "10.5555/neurips.2023.002",
                "is_oa": True
            },
            "W_F2": {
                "id": "W_F2",
                "title": "Quantum Foundation Models for Climate Modeling",
                "authors": "Chen L",
                "first_author": "Chen L",
                "year": 2024,
                "venue": "Science Advances",
                "citation_count": 18,
                "level": 2,
                "layer": "forward",
                "scopus_tier": "Scopus Q1",
                "study_type": "Empirical Journalism Study",
                "doi": "10.1126/sciadv.2024.001",
                "is_oa": True
            }
        }
        self.sample_edges = [
            ("W_SEED", "W_R1_A"),
            ("W_SEED", "W_R1_B"),
            ("W_F1_A", "W_SEED"),
            ("W_F1_B", "W_SEED"),
            ("W_F2", "W_F1_A")
        ]

    def test_10_themes_present(self):
        """Kiểm tra sự hiện diện và đầy đủ của 10 Themes trong HTML và CSS"""
        html_out = self.agent.generate_network_html(self.sample_nodes, self.sample_edges)
        
        expected_themes = [
            'theme-synapse-cyan',
            'theme-emerald-matrix',
            'theme-monochrome-classic',
            'theme-nebula-violet',
            'theme-solar-amber',
            'theme-deep-ocean',
            'theme-crimson-ruby',
            'theme-nordic-frost',
            'theme-vintage-parchment',
            'theme-neon-gold'
        ]
        
        for theme in expected_themes:
            self.assertIn(theme, html_out, f"Theme {theme} phải có trong mã HTML/CSS/JS")

    def test_10_layout_modes_present(self):
        """Kiểm tra sự hiện diện của 10 Chế độ Bố cục Học thuật"""
        html_out = self.agent.generate_network_html(self.sample_nodes, self.sample_edges)
        
        expected_layouts = [
            'timeline',
            'radar',
            'fishbone',
            'dendrogram',
            'hierarchical',
            'matrix',
            'force',
            'quartile',
            'diamond',
            'fanchart'
        ]
        
        for layout in expected_layouts:
            self.assertIn(f"switchLayoutMode('{layout}')", html_out, f"Layout action {layout} phải có trong HTML")
            self.assertIn(f"value=\"{layout}\"", html_out, f"Layout option {layout} phải có trong select dropdown")

    def test_multi_layer_combined_options_and_f0_anchor(self):
        """Kiểm tra các tùy chọn lọc đa tầng kết hợp và logic neo giữ bài gốc F0"""
        html_out = self.agent.generate_network_html(self.sample_nodes, self.sample_edges)
        
        # Kiểm tra các option kết hợp trong layerFilter
        combined_filters = [
            'value="all"',
            'value="f0_forward"',
            'value="f0_backward"',
            'value="f0_f1"',
            'value="f0_f2"',
            'value="f0_r1"',
            'value="f0_r2"',
            'value="seed_only"',
            'value="f1_f3"',
            'value="r1_r3"'
        ]
        for opt in combined_filters:
            self.assertIn(opt, html_out, f"Bộ lọc đa tầng {opt} phải có trong select layerFilter")
            
        # Kiểm tra logic neo F0 trong JS
        self.assertIn("layerVal === 'f0_forward'", html_out)
        self.assertIn("layerVal === 'f0_backward'", html_out)
        self.assertIn("matchLayer = (isSeed || lvl > 0", html_out)
        self.assertIn("matchLayer = (isSeed || lvl < 0", html_out)

    def test_same_year_anti_collision_logic(self):
        """Kiểm tra thuật toán so le trục Y chống đè trùng năm"""
        html_out = self.agent.generate_network_html(self.sample_nodes, self.sample_edges)
        self.assertIn("yearGroups", html_out)
        self.assertIn("idxInYr", html_out)
        self.assertIn("totalInYr", html_out)

    def test_omnidirectional_uniform_box_shadow(self):
        """Kiểm tra đổ bóng đều khung (Omnidirectional Box-Shadow)"""
        html_out = self.agent.generate_network_html(self.sample_nodes, self.sample_edges)
        self.assertIn("--theme-hud-shadow: 0 0 20px rgba(0, 242, 254, 0.20), 0 4px 20px rgba(0, 0, 0, 0.45);", html_out)
        self.assertIn("box-shadow: var(--theme-hud-shadow)", html_out)

    def test_standalone_fullscreen_mode(self):
        """Kiểm tra hàm generate_standalone_fullscreen_html hoạt động hoàn hảo"""
        fullscreen_html = self.agent.generate_standalone_fullscreen_html(self.sample_nodes, self.sample_edges)
        self.assertIn("min-height: 100vh;", fullscreen_html)
        self.assertIn("display: none !important;", fullscreen_html)
        self.assertIn("theme-monochrome-classic", fullscreen_html)
        self.assertIn("switchLayoutMode('fishbone')", fullscreen_html)

if __name__ == "__main__":
    unittest.main()
