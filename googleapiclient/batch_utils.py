"""
Batch Operation Utilities for Google API Python Client

Provides utilities to detect and prevent incompatible operation mixing
in BatchHttpRequest, specifically addressing Issue #2655.

Author: Claudio Gallardo
Developed as part of PupiBot - AI Agent for Google Workspace
Project: https://github.com/claudiogallardo/PupiBot (proprietary)

This specific utility is contributed to the community under Apache 2.0
while the full AI orchestration layer remains proprietary.

Related Issue: https://github.com/googleapis/google-api-python-client/issues/2655
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class BatchOperationAnalyzer:
    """
    Analyzes batch operations to detect incompatible mixing BEFORE execution.
    
    Background:
    -----------
    When using BatchHttpRequest with Google Drive API, mixing certain operations
    causes a 400 error with message "This API does not support batching".
    
    This class detects these incompatibilities proactively, allowing developers
    to handle them gracefully (e.g., split into separate batches).
    
    Methodology:
    -----------
    Based on real-world testing with 200+ daily requests in production AI agent.
    Developed through systematic analysis of batch failures in PupiBot.
    
    Example:
    --------
    >>> operations = [
    ...     {'method': 'files.modifyLabels', 'fileId': '123'},
    ...     {'method': 'files.update', 'fileId': '456'}
    ... ]
    >>> result = BatchOperationAnalyzer.analyze_batch(operations)
    >>> print(result['compatible'])
    False
    >>> print(result['warning'])
    'Incompatible mixing detected: files.modifyLabels + files.update'
    """
    
    # Known incompatible operation pairs (expandable as more are discovered)
    INCOMPATIBLE_PAIRS = [
        ('files.modifyLabels', 'files.update'),
        ('files.modifyLabels', 'files.copy'),
        ('files.modifyLabels', 'files.create'),
    ]
    
    @classmethod
    def analyze_batch(cls, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of operations for incompatible mixing.
        
        Args:
            operations: List of operation dictionaries, each containing at least
                       a 'method' key (e.g., 'files.update', 'files.modifyLabels')
        
        Returns:
            Dictionary with:
            - compatible (bool): True if batch is safe to execute
            - warning (str): Description of incompatibility if found
            - incompatible_pairs (list): List of detected incompatible pairs
            - suggestion (str): Recommended action if incompatible
        
        Example:
            >>> ops = [{'method': 'files.update'}, {'method': 'files.copy'}]
            >>> result = BatchOperationAnalyzer.analyze_batch(ops)
            >>> result['compatible']
            True
        """
        if not operations:
            return {
                'compatible': True,
                'warning': None,
                'incompatible_pairs': [],
                'suggestion': None
            }
        
        # Extract unique method names from operations
        methods = set(op.get('method', '') for op in operations if op.get('method'))
        
        if not methods:
            logger.warning("No methods found in operations")
            return {
                'compatible': True,
                'warning': 'No method names found in operations',
                'incompatible_pairs': [],
                'suggestion': None
            }
        
        # Check for incompatible pairs
        detected_incompatibilities = []
        
        for method1, method2 in cls.INCOMPATIBLE_PAIRS:
            if method1 in methods and method2 in methods:
                detected_incompatibilities.append((method1, method2))
        
        if detected_incompatibilities:
            # Build detailed warning message
            pairs_str = ', '.join([f"{m1} + {m2}" for m1, m2 in detected_incompatibilities])
            warning = f"Incompatible mixing detected: {pairs_str}"
            
            return {
                'compatible': False,
                'warning': warning,
                'incompatible_pairs': detected_incompatibilities,
                'suggestion': 'Split operations into separate batches by method type'
            }
        
        return {
            'compatible': True,
            'warning': None,
            'incompatible_pairs': [],
            'suggestion': None
        }
    
    @classmethod
    def suggest_batch_split(cls, operations: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Suggest how to split operations into compatible batches.
        
        Args:
            operations: List of operations that may contain incompatibilities
        
        Returns:
            List of operation batches, where each batch is compatible
        
        Example:
            >>> ops = [
            ...     {'method': 'files.modifyLabels', 'fileId': '1'},
            ...     {'method': 'files.update', 'fileId': '2'},
            ...     {'method': 'files.update', 'fileId': '3'}
            ... ]
            >>> batches = BatchOperationAnalyzer.suggest_batch_split(ops)
            >>> len(batches)
            2
            >>> batches[0][0]['method']
            'files.modifyLabels'
            >>> batches[1][0]['method']
            'files.update'
        """
        if not operations:
            return []
        
        # Group operations by method
        grouped = defaultdict(list)
        for op in operations:
            method = op.get('method', 'unknown')
            grouped[method].append(op)
        
        # Check if current grouping is compatible
        analysis = cls.analyze_batch(operations)
        
        if analysis['compatible']:
            # No split needed
            return [operations]
        
        # Split needed - group by method type to avoid mixing
        # Strategy: Keep modifyLabels separate from all other operations
        modify_labels_ops = []
        other_ops = []
        
        for method, ops in grouped.items():
            if 'modifyLabels' in method:
                modify_labels_ops.extend(ops)
            else:
                other_ops.extend(ops)
        
        batches = []
        if modify_labels_ops:
            batches.append(modify_labels_ops)
        if other_ops:
            batches.append(other_ops)
        
        return batches
    
    @classmethod
    def add_incompatible_pair(cls, method1: str, method2: str) -> None:
        """
        Add a new incompatible pair to the analyzer.
        
        Allows extending the analyzer as new incompatibilities are discovered.
        
        Args:
            method1: First method name (e.g., 'files.modifyLabels')
            method2: Second method name (e.g., 'files.update')
        
        Example:
            >>> BatchOperationAnalyzer.add_incompatible_pair('files.newMethod', 'files.update')
        """
        pair = (method1, method2)
        if pair not in cls.INCOMPATIBLE_PAIRS:
            cls.INCOMPATIBLE_PAIRS.append(pair)
            logger.info(f"Added incompatible pair: {method1} + {method2}")


def validate_batch_request(batch_operations: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Convenience function to quickly validate a batch request.
    
    Args:
        batch_operations: List of operations to validate
    
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if batch is safe to execute
        - error_message: None if valid, otherwise description of issue
    
    Example:
        >>> ops = [{'method': 'files.update'}, {'method': 'files.copy'}]
        >>> valid, error = validate_batch_request(ops)
        >>> valid
        True
        >>> error is None
        True
    """
    result = BatchOperationAnalyzer.analyze_batch(batch_operations)
    
    if result['compatible']:
        return True, None
    
    error_msg = f"{result['warning']}. {result['suggestion']}"
    return False, error_msg


# Backward compatibility alias
BatchValidator = BatchOperationAnalyzer
