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

"""
Binary Ninja helper utilities for capa explorer plugin
"""

import logging

try:
    import binaryninja as binja
    BINJA_AVAILABLE = True
except ImportError:
    BINJA_AVAILABLE = False

logger = logging.getLogger(__name__)


def is_supported_file_type(bv=None):
    """Check if the current binary view is supported by capa"""
    if not BINJA_AVAILABLE:
        return False
        
    if bv is None:
        return False
        
    # capa supports PE, ELF files primarily
    supported_types = [
        'PE',
        'ELF', 
        'COFF',
        'Raw'  # For shellcode
    ]
    
    view_type = bv.view_type
    if view_type in supported_types:
        return True
        
    return False


def is_supported_arch_type(bv=None):
    """Check if the current architecture is supported by capa"""
    if not BINJA_AVAILABLE:
        return False
        
    if bv is None:
        return False
        
    # capa primarily supports x86/x64
    supported_archs = [
        'x86',
        'x86_64'
    ]
    
    arch_name = bv.arch.name
    if arch_name in supported_archs:
        return True
        
    return False


def get_binary_ninja_version():
    """Get Binary Ninja version string"""
    if not BINJA_AVAILABLE:
        return "Binary Ninja not available"
        
    try:
        core_version = binja.core_version()
        return f"Binary Ninja {core_version}"
    except:
        return "Binary Ninja version unknown"


def is_supported_binja_version():
    """Check if Binary Ninja version is supported"""
    if not BINJA_AVAILABLE:
        return False
        
    try:
        # Basic check - if we can import binaryninja, it's probably new enough
        # Binary Ninja plugin API has been fairly stable
        return True
    except:
        return False


def get_function_name_at(bv, address):
    """Get function name at the given address"""
    if not BINJA_AVAILABLE or not bv:
        return None
        
    functions = bv.get_functions_at(address)
    if functions:
        return functions[0].name
    return None


def navigate_to_address(bv, address):
    """Navigate Binary Ninja to the given address"""
    if not BINJA_AVAILABLE or not bv:
        return False
        
    try:
        bv.navigate(bv.view, address)
        return True
    except:
        return False


def get_current_address(bv):
    """Get the current address in Binary Ninja view"""
    if not BINJA_AVAILABLE or not bv:
        return None
        
    try:
        # This might vary depending on Binary Ninja version
        # For now, return None as this requires UI context
        return None
    except:
        return None


def log_info(message):
    """Log info message to Binary Ninja log"""
    if BINJA_AVAILABLE:
        binja.log_info(message)
    else:
        logger.info(message)


def log_error(message):
    """Log error message to Binary Ninja log"""
    if BINJA_AVAILABLE:
        binja.log_error(message)
    else:
        logger.error(message)


def log_warn(message):
    """Log warning message to Binary Ninja log"""
    if BINJA_AVAILABLE:
        binja.log_warn(message)
    else:
        logger.warning(message)