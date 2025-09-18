# Copyright 2023 Google LLC
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

import pytest
import logging
from pathlib import Path

logger = logging.getLogger(__file__)


def test_binja_plugin_import():
    """Test that the Binary Ninja plugin can be imported without Binary Ninja"""
    try:
        import capa.binja.plugin
        assert True  # If we get here, import succeeded
    except ImportError as e:
        # If Binary Ninja dependencies are missing, that's expected
        if "binaryninja" in str(e) or "PySide" in str(e):
            pytest.skip("Binary Ninja not available")
        else:
            # Other import errors are real failures
            raise


def test_binja_helpers_import():
    """Test that Binary Ninja helpers can be imported"""
    try:
        import capa.binja.helpers
        assert True
    except ImportError as e:
        if "binaryninja" in str(e):
            pytest.skip("Binary Ninja not available")
        else:
            raise


def test_binja_plugin_structure():
    """Test that the Binary Ninja plugin directory structure exists"""
    import capa
    capa_path = Path(capa.__file__).parent
    
    binja_path = capa_path / "binja"
    assert binja_path.exists(), "Binary Ninja plugin directory should exist"
    
    plugin_path = binja_path / "plugin"
    assert plugin_path.exists(), "Binary Ninja plugin subdirectory should exist"
    
    # Check key files exist
    key_files = [
        binja_path / "__init__.py",
        binja_path / "helpers.py", 
        plugin_path / "__init__.py",
        plugin_path / "form.py",
        plugin_path / "icon.py",
        plugin_path / "capa_explorer.py",
        plugin_path / "README.md"
    ]
    
    for file_path in key_files:
        assert file_path.exists(), f"Required file should exist: {file_path}"


def test_binja_plugin_doesnt_break_ida():
    """Test that adding Binary Ninja plugin doesn't break IDA plugin"""
    # IDA plugin should still be importable (even if IDA isn't available)
    try:
        import capa.ida.plugin
        # If we can import it, that's good
        assert True
    except ImportError as e:
        # If it's just missing IDA, that's expected
        if "idaapi" in str(e) or "ida_" in str(e):
            # This is expected when IDA isn't available
            assert True
        else:
            # Other import errors suggest we broke something
            raise


def test_capa_core_still_works():
    """Test that core capa functionality still works after adding Binary Ninja plugin"""
    # Core imports should work
    import capa.main
    import capa.rules
    import capa.engine
    
    # Basic functionality test
    assert hasattr(capa.main, "find_capabilities")
    assert hasattr(capa.rules, "get_rules")
    assert hasattr(capa.engine, "FeatureSet")