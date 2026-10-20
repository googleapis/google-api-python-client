"""
Unit tests for batch_utils.py

Author: Claudio Gallardo
Related to Issue #2655
"""

import unittest
from batch_utils import (
    BatchOperationAnalyzer,
    validate_batch_request
)


class TestBatchOperationAnalyzer(unittest.TestCase):
    """Test suite for BatchOperationAnalyzer"""
    
    def test_compatible_operations(self):
        """Test that compatible operations are correctly identified"""
        operations = [
            {'method': 'files.update', 'fileId': '123'},
            {'method': 'files.copy', 'fileId': '456'},
            {'method': 'files.create', 'name': 'test.txt'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertTrue(result['compatible'])
        self.assertIsNone(result['warning'])
        self.assertEqual(len(result['incompatible_pairs']), 0)
    
    def test_incompatible_modify_labels_with_update(self):
        """Test detection of modifyLabels + update incompatibility (Issue #2655)"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '123'},
            {'method': 'files.update', 'fileId': '456'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertFalse(result['compatible'])
        self.assertIsNotNone(result['warning'])
        self.assertIn('files.modifyLabels', result['warning'])
        self.assertIn('files.update', result['warning'])
        self.assertEqual(len(result['incompatible_pairs']), 1)
        self.assertIn(('files.modifyLabels', 'files.update'), result['incompatible_pairs'])
    
    def test_incompatible_modify_labels_with_copy(self):
        """Test detection of modifyLabels + copy incompatibility"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '123'},
            {'method': 'files.copy', 'fileId': '456'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertFalse(result['compatible'])
        self.assertIn('files.modifyLabels', result['warning'])
        self.assertIn('files.copy', result['warning'])
    
    def test_incompatible_modify_labels_with_create(self):
        """Test detection of modifyLabels + create incompatibility"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '123'},
            {'method': 'files.create', 'name': 'test.txt'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertFalse(result['compatible'])
        self.assertIn('files.modifyLabels', result['warning'])
    
    def test_empty_operations(self):
        """Test handling of empty operations list"""
        result = BatchOperationAnalyzer.analyze_batch([])
        
        self.assertTrue(result['compatible'])
        self.assertIsNone(result['warning'])
    
    def test_operations_without_method(self):
        """Test handling of operations missing 'method' key"""
        operations = [
            {'fileId': '123'},  # Missing 'method'
            {'method': 'files.update', 'fileId': '456'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        # Should still work with valid operations
        self.assertTrue(result['compatible'])
    
    def test_suggest_batch_split_compatible(self):
        """Test that compatible batches are not split"""
        operations = [
            {'method': 'files.update', 'fileId': '123'},
            {'method': 'files.copy', 'fileId': '456'}
        ]
        
        batches = BatchOperationAnalyzer.suggest_batch_split(operations)
        
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0], operations)
    
    def test_suggest_batch_split_incompatible(self):
        """Test that incompatible batches are correctly split"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '1'},
            {'method': 'files.update', 'fileId': '2'},
            {'method': 'files.update', 'fileId': '3'},
            {'method': 'files.modifyLabels', 'fileId': '4'}
        ]
        
        batches = BatchOperationAnalyzer.suggest_batch_split(operations)
        
        # Should split into 2 batches: modifyLabels and others
        self.assertEqual(len(batches), 2)
        
        # Find which batch contains modifyLabels
        modify_labels_batch = None
        other_batch = None
        
        for batch in batches:
            methods = [op['method'] for op in batch]
            if 'files.modifyLabels' in methods:
                modify_labels_batch = batch
            else:
                other_batch = batch
        
        self.assertIsNotNone(modify_labels_batch)
        self.assertIsNotNone(other_batch)
        self.assertEqual(len(modify_labels_batch), 2)  # 2 modifyLabels ops
        self.assertEqual(len(other_batch), 2)  # 2 update ops
    
    def test_suggest_batch_split_empty(self):
        """Test handling of empty operations in suggest_batch_split"""
        batches = BatchOperationAnalyzer.suggest_batch_split([])
        
        self.assertEqual(len(batches), 0)
    
    def test_add_incompatible_pair(self):
        """Test adding custom incompatible pairs"""
        # Save original pairs
        original_pairs = BatchOperationAnalyzer.INCOMPATIBLE_PAIRS.copy()
        
        try:
            # Add new pair
            BatchOperationAnalyzer.add_incompatible_pair('files.testMethod1', 'files.testMethod2')
            
            # Test detection
            operations = [
                {'method': 'files.testMethod1', 'fileId': '123'},
                {'method': 'files.testMethod2', 'fileId': '456'}
            ]
            
            result = BatchOperationAnalyzer.analyze_batch(operations)
            
            self.assertFalse(result['compatible'])
            self.assertIn('files.testMethod1', result['warning'])
            self.assertIn('files.testMethod2', result['warning'])
        
        finally:
            # Restore original pairs
            BatchOperationAnalyzer.INCOMPATIBLE_PAIRS = original_pairs
    
    def test_validate_batch_request_valid(self):
        """Test validate_batch_request convenience function with valid batch"""
        operations = [
            {'method': 'files.update', 'fileId': '123'},
            {'method': 'files.copy', 'fileId': '456'}
        ]
        
        valid, error = validate_batch_request(operations)
        
        self.assertTrue(valid)
        self.assertIsNone(error)
    
    def test_validate_batch_request_invalid(self):
        """Test validate_batch_request convenience function with invalid batch"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '123'},
            {'method': 'files.update', 'fileId': '456'}
        ]
        
        valid, error = validate_batch_request(operations)
        
        self.assertFalse(valid)
        self.assertIsNotNone(error)
        self.assertIn('modifyLabels', error)
        self.assertIn('update', error)
    
    def test_multiple_incompatible_pairs(self):
        """Test detection when multiple incompatible pairs are present"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '1'},
            {'method': 'files.update', 'fileId': '2'},
            {'method': 'files.copy', 'fileId': '3'},
            {'method': 'files.create', 'name': 'test.txt'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertFalse(result['compatible'])
        # Should detect all 3 incompatible pairs with modifyLabels
        self.assertEqual(len(result['incompatible_pairs']), 3)
    
    def test_suggestion_included_when_incompatible(self):
        """Test that suggestions are provided for incompatible batches"""
        operations = [
            {'method': 'files.modifyLabels', 'fileId': '123'},
            {'method': 'files.update', 'fileId': '456'}
        ]
        
        result = BatchOperationAnalyzer.analyze_batch(operations)
        
        self.assertIsNotNone(result['suggestion'])
        self.assertIn('separate', result['suggestion'].lower())


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def test_production_scenario_issue_2655(self):
        """
        Reproduce exact scenario from Issue #2655
        
        User reported: Mixing files.modifyLabels with files.update in batch
        causes "This API does not support batching" error
        """
        # Simulate user's batch request
        batch_operations = [
            {
                'method': 'files.modifyLabels',
                'fileId': 'file_abc123',
                'body': {'labels': {'important': True}}
            },
            {
                'method': 'files.update',
                'fileId': 'file_def456',
                'body': {'name': 'Updated Name.txt'}
            }
        ]
        
        # Analyzer should detect this incompatibility
        result = BatchOperationAnalyzer.analyze_batch(batch_operations)
        
        self.assertFalse(result['compatible'], 
                        "Should detect modifyLabels + update incompatibility")
        self.assertIn('modifyLabels', result['warning'])
        self.assertIn('update', result['warning'])
        
        # Suggest how to fix
        batches = BatchOperationAnalyzer.suggest_batch_split(batch_operations)
        self.assertEqual(len(batches), 2, "Should suggest splitting into 2 batches")
        
        # Each resulting batch should be compatible
        for batch in batches:
            batch_result = BatchOperationAnalyzer.analyze_batch(batch)
            self.assertTrue(batch_result['compatible'], 
                          f"Split batch should be compatible: {batch}")
    
    def test_ai_agent_workflow(self):
        """
        Test scenario from PupiBot: AI agent processing multiple file operations
        
        Context: AI decides to update metadata and content in single batch
        System should detect incompatibility and suggest split
        """
        # AI-generated batch (would fail in production)
        ai_batch = [
            {'method': 'files.modifyLabels', 'fileId': 'report_2024.xlsx'},
            {'method': 'files.modifyLabels', 'fileId': 'budget_2024.xlsx'},
            {'method': 'files.update', 'fileId': 'summary.docx'},
            {'method': 'files.copy', 'fileId': 'template.pptx'}
        ]
        
        # Pre-validate before executing
        valid, error = validate_batch_request(ai_batch)
        
        self.assertFalse(valid)
        self.assertIsNotNone(error)
        
        # Get corrected batches
        corrected_batches = BatchOperationAnalyzer.suggest_batch_split(ai_batch)
        
        # Should have split into 2: labels vs others
        self.assertEqual(len(corrected_batches), 2)
        
        # Verify each corrected batch is valid
        for batch in corrected_batches:
            valid, _ = validate_batch_request(batch)
            self.assertTrue(valid, "Corrected batch should be valid")


if __name__ == '__main__':
    unittest.main()
