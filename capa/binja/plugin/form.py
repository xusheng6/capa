# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy
import logging
import collections
from enum import IntFlag
from typing import Any, Optional
from pathlib import Path

try:
    import binaryninja as binja
    from binaryninja.plugin import BackgroundTaskThread
    from binaryninja.interaction import show_message_box, get_directory_name_input
    from binaryninja.log import log_info, log_error, log_warn
    from binaryninja.dockwidgets import DockWidget, DockContextHandler
    
    # Try to import Qt - different versions of Binary Ninja use different Qt versions
    try:
        from binaryninjaui import UIContext, Menu, UIAction, UIActionHandler
        from PySide2.QtCore import Qt, QAbstractItemModel, QModelIndex, QSortFilterProxyModel, QThread, pyqtSignal
        from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, 
                                      QLineEdit, QTextEdit, QTabWidget, QProgressBar, QLabel,
                                      QSplitter, QHeaderView, QMessageBox, QFileDialog, QCheckBox)
        from PySide2.QtGui import QFont, QStandardItemModel, QStandardItem
        QT_AVAILABLE = True
    except ImportError:
        try:
            from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, QSortFilterProxyModel, QThread, Signal as pyqtSignal
            from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, 
                                          QLineEdit, QTextEdit, QTabWidget, QProgressBar, QLabel,
                                          QSplitter, QHeaderView, QMessageBox, QFileDialog, QCheckBox)
            from PySide6.QtGui import QFont, QStandardItemModel, QStandardItem
            QT_AVAILABLE = True
        except ImportError:
            QT_AVAILABLE = False
    
    BINJA_AVAILABLE = True
except ImportError:
    BINJA_AVAILABLE = False
    QT_AVAILABLE = False

import capa.main
import capa.rules
import capa.engine
import capa.version
import capa.render.json
import capa.features.common
import capa.capabilities.common
import capa.render.result_document
from capa.rules import Rule
from capa.engine import FeatureSet
from capa.rules.cache import compute_ruleset_cache_identifier

if BINJA_AVAILABLE:
    import capa.features.extractors.binja.extractor

logger = logging.getLogger(__name__)

# Settings keys for Binary Ninja
CAPA_SETTINGS_RULE_PATH = "capa.rule_path"
CAPA_SETTINGS_ANALYZE = "capa.analyze"

CAPA_OFFICIAL_RULESET_URL = f"https://github.com/mandiant/capa-rules/releases/tag/v{capa.version.__version__}"
CAPA_RULESET_DOC_URL = "https://github.com/mandiant/capa/blob/master/doc/rules.md"

class Options(IntFlag):
    NO_ANALYSIS = 0  # No auto analysis
    ANALYZE_AUTO = 1  # Runs the analysis when starting the explorer

AnalyzeOptionsText = {
    Options.NO_ANALYSIS: "Do not analyze",
    Options.ANALYZE_AUTO: "Analyze on plugin start (load cached results)",
}

def update_wait_box(text):
    """Update status with text"""
    log_info(f"capa explorer: {text}")

class CapaExplorerResultsModel(QStandardItemModel):
    """Data model for capa results tree view"""
    
    def __init__(self):
        super().__init__()
        self.results = None
        self.setHorizontalHeaderLabels(["Rule Information", "Address", "Details"])
        
    def clear_results(self):
        """Clear all results from the model"""
        self.clear()
        self.setHorizontalHeaderLabels(["Rule Information", "Address", "Details"])
        self.results = None
        
    def update_results(self, results):
        """Update the model with new capa results"""
        self.clear_results()
        self.results = results
        
        if not results:
            return
            
        # Add results to tree
        for rule_name, rule_data in results.items():
            rule_item = QStandardItem(rule_name)
            addr_item = QStandardItem("")
            details_item = QStandardItem(f"{len(rule_data.get('matches', []))} matches")
            
            # Add matches
            for match in rule_data.get('matches', []):
                match_item = QStandardItem(f"Match")
                match_addr = QStandardItem(f"0x{match.get('address', 0):x}")
                match_details = QStandardItem("Rule match")
                
                rule_item.appendRow([match_item, match_addr, match_details])
            
            self.appendRow([rule_item, addr_item, details_item])

class CapaAnalysisThread(QThread):
    """Background thread for running capa analysis"""
    
    finished = pyqtSignal(object)  # Signal emitted when analysis completes
    progress = pyqtSignal(str)     # Signal for progress updates
    
    def __init__(self, bv, rules_path):
        super().__init__()
        self.bv = bv
        self.rules_path = rules_path
        
    def run(self):
        """Run capa analysis in background thread"""
        try:
            self.progress.emit("Initializing capa analysis...")
            
            # Create extractor
            extractor = capa.features.extractors.binja.extractor.BinjaFeatureExtractor(self.bv)
            
            self.progress.emit("Loading rules...")
            
            # Load rules
            rules_path = Path(self.rules_path)
            if not rules_path.exists():
                raise ValueError(f"Rules directory does not exist: {rules_path}")
                
            rules = capa.rules.get_rules([rules_path])
            if not rules:
                raise ValueError("No rules loaded")
            
            self.progress.emit("Running capa analysis...")
            
            # Run analysis
            capabilities, counts = capa.main.find_capabilities(rules, extractor)
            
            self.progress.emit("Analysis complete")
            
            # Convert results to simple dict format
            results = {}
            for rule_name, rule_matches in capabilities.items():
                if rule_matches:
                    results[rule_name] = {
                        'matches': [{'address': match.address.value if hasattr(match.address, 'value') else 0}
                                   for match in rule_matches]
                    }
            
            self.finished.emit(results)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.finished.emit({"error": str(e)})

if QT_AVAILABLE and BINJA_AVAILABLE:
    class CapaExplorerWidget(QWidget):
        """Main widget for capa explorer"""
        
        def __init__(self, bv):
            super().__init__()
            self.bv = bv
            self.results = None
            self.rules_path = None
            self.analysis_thread = None
            
            self.init_ui()
            self.load_settings()
            
        def init_ui(self):
            """Initialize the user interface"""
            layout = QVBoxLayout()
            
            # Create tab widget
            self.tabs = QTabWidget()
            
            # Program Analysis tab
            self.analysis_tab = self.create_analysis_tab()
            self.tabs.addTab(self.analysis_tab, "Program Analysis")
            
            layout.addWidget(self.tabs)
            self.setLayout(layout)
            
        def create_analysis_tab(self):
            """Create the program analysis tab"""
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Controls
            controls_layout = QHBoxLayout()
            
            self.analyze_btn = QPushButton("Analyze")
            self.analyze_btn.clicked.connect(self.run_analysis)
            controls_layout.addWidget(self.analyze_btn)
            
            self.reset_btn = QPushButton("Reset")
            self.reset_btn.clicked.connect(self.reset_analysis)
            controls_layout.addWidget(self.reset_btn)
            
            self.settings_btn = QPushButton("Settings")
            self.settings_btn.clicked.connect(self.show_settings)
            controls_layout.addWidget(self.settings_btn)
            
            controls_layout.addStretch()
            layout.addLayout(controls_layout)
            
            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            layout.addWidget(self.progress_bar)
            
            # Results tree
            self.results_model = CapaExplorerResultsModel()
            self.results_tree = QTreeView()
            self.results_tree.setModel(self.results_model)
            self.results_tree.doubleClicked.connect(self.on_result_double_click)
            
            layout.addWidget(self.results_tree)
            
            widget.setLayout(layout)
            return widget
            
        def load_settings(self):
            """Load plugin settings"""
            # Try to get saved rules path
            saved_path = self.bv.file.session_data.get(CAPA_SETTINGS_RULE_PATH)
            if saved_path and Path(saved_path).exists():
                self.rules_path = saved_path
                
        def save_settings(self):
            """Save plugin settings"""
            if self.rules_path:
                self.bv.file.session_data[CAPA_SETTINGS_RULE_PATH] = self.rules_path
                
        def show_settings(self):
            """Show settings dialog"""
            # For now, just ask for rules directory
            rules_dir = get_directory_name_input("Select capa rules directory", self.rules_path or "")
            if rules_dir:
                self.rules_path = rules_dir
                self.save_settings()
                show_message_box("Settings", f"Rules directory set to: {rules_dir}")
                
        def run_analysis(self):
            """Run capa analysis"""
            if not self.rules_path:
                self.show_settings()
                if not self.rules_path:
                    return
                    
            # Start analysis in background thread
            self.analyze_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self.analysis_thread = CapaAnalysisThread(self.bv, self.rules_path)
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            self.analysis_thread.progress.connect(self.on_analysis_progress)
            self.analysis_thread.start()
            
        def on_analysis_progress(self, message):
            """Handle analysis progress updates"""
            log_info(f"capa: {message}")
            
        def on_analysis_finished(self, results):
            """Handle analysis completion"""
            self.analyze_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            
            if "error" in results:
                show_message_box("Analysis Error", f"Analysis failed: {results['error']}")
                return
                
            self.results = results
            self.results_model.update_results(results)
            
            # Expand tree
            self.results_tree.expandAll()
            
            log_info(f"capa analysis complete: {len(results)} rules matched")
            
        def reset_analysis(self):
            """Reset analysis results"""
            self.results = None
            self.results_model.clear_results()
            
        def on_result_double_click(self, index):
            """Handle double-click on results tree"""
            if not index.isValid():
                return
                
            # Get the address from the second column
            addr_index = self.results_model.index(index.row(), 1, index.parent())
            addr_text = self.results_model.itemFromIndex(addr_index).text()
            
            if addr_text.startswith("0x"):
                try:
                    addr = int(addr_text, 16)
                    # Navigate to address in Binary Ninja
                    self.bv.navigate(self.bv.view, addr)
                except ValueError:
                    pass
                    
    class CapaExplorerForm(DockWidget):
        """Main form for capa explorer"""
        
        def __init__(self, bv):
            super().__init__("FLARE capa explorer")
            self.bv = bv
            self.widget = CapaExplorerWidget(bv)
            self.setWidget(self.widget)
            
        def show(self):
            """Show the capa explorer widget"""
            # Get the UI context and show as docked widget
            context = UIContext.contextForWidget(self.widget)
            if context:
                context.openDockWidget(self)
            else:
                # Fallback - show as regular widget
                self.widget.show()
                
        def load_capa_results(self, use_cache=True, analyze_auto=False):
            """Load capa results (for compatibility with IDA plugin interface)"""
            if analyze_auto and self.widget.rules_path:
                self.widget.run_analysis()
                
else:
    # Dummy classes when Qt is not available
    class CapaExplorerForm:
        def __init__(self, bv):
            pass
        def show(self):
            pass
        def load_capa_results(self, use_cache=True, analyze_auto=False):
            pass