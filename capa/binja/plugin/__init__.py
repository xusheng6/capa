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

import logging

logger = logging.getLogger(__name__)

try:
    import binaryninja as binja
    from capa.binja.plugin.form import CapaExplorerForm
    from capa.binja.plugin.icon import ICON
    from capa.binja import helpers
    
    class CapaExplorerPlugin:
        """Main capa explorer plugin class"""
        
        def __init__(self):
            """initialize plugin"""
            self.form = None

        def is_valid(self, view):
            """Check if the plugin can run on this binary view"""
            if not isinstance(view, binja.BinaryView):
                return False
            
            # Check basic file type and architecture support
            return (helpers.is_supported_file_type(view) and 
                   helpers.is_supported_arch_type(view))

        def run(self, view):
            """Run the capa explorer plugin"""
            try:
                if not self.form or self.form.bv != view:
                    self.form = CapaExplorerForm(view)
                    
                self.form.show()
                
            except Exception as e:
                logger.error(f"Error running capa explorer: {e}")
                if hasattr(binja, 'show_message_box'):
                    binja.show_message_box("Capa Explorer Error", 
                                         f"Failed to run capa explorer: {str(e)}")

    # Create plugin instance
    plugin_instance = CapaExplorerPlugin()

    # Register the plugin command
    binja.PluginCommand.register(
        "FLARE capa explorer",
        "Identify capabilities in executable files using FLARE capa",
        plugin_instance.run,
        plugin_instance.is_valid
    )

    logger.info("FLARE capa explorer plugin registered successfully")

except ImportError as e:
    # Binary Ninja not available, plugin will not be registered
    logger.debug(f"Binary Ninja not available for capa plugin: {e}")
    pass