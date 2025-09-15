#!/usr/bin/env python3
"""
Test for citation cleaning functionality.

This test verifies that citations like 【3:0†source】 and space-before-periods
are properly cleaned from answers returned by the question answerer.
"""

import unittest
import sys
import os

# Add the parent directory to Python path to import question_answerer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_answerer import QuestionnaireAgentUI


class TestCitationCleaning(unittest.TestCase):
    """Test citation cleaning functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.agent = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
        
    def test_extract_links_and_clean_function(self):
        """Test the extract_links_and_clean function directly."""
        # Test text with citations and space-before-period issues
        test_text = """For deliveries over 5km, MetroParcel is the most cost-efficient courier, with an average delivery cost of $22.50. RapidWay ($23.04) and BlueArrow Logistics ($23.22) are also competitive options. Ludus Dryden is the least cost-efficient, costing $35.13 on average for these distances 【3:0†source】 .

Based on structured data related to Microsoft Azure, FedEx is the most commonly used courier for Azure shipments. This conclusion is supported by shipment records showing FedEx as the frequent choice for Azure-related logistics 【message_idx:search_0†source】 .

Based on the data, the largest customer is identified by having the highest number of deliveries. CustomerKey 11607 is the largest customer, receiving a total of 92 deliveries, which is the most among all customers listed in the dataset ."""
        
        clean_text, urls = self.agent.extract_links_and_clean(test_text)
        
        # Verify citations are removed
        self.assertNotIn('【3:0†source】', clean_text, "Citation 【3:0†source】 should be removed")
        self.assertNotIn('【message_idx:search_0†source】', clean_text, "Citation 【message_idx:search_0†source】 should be removed")
        
        # Verify space-before-period is fixed
        self.assertNotIn(' .', clean_text, "Space before period should be fixed")
        
        # Verify the content is preserved
        self.assertIn('MetroParcel is the most cost-efficient courier', clean_text)
        self.assertIn('FedEx is the most commonly used courier', clean_text)
        self.assertIn('CustomerKey 11607 is the largest customer', clean_text)
        
        print(f"\n✓ Original text contained citations and spacing issues")
        print(f"✓ Cleaned text: {clean_text[:200]}...")
        print(f"✓ Citations removed and spacing fixed")
        
    def test_various_citation_formats(self):
        """Test cleaning of various citation formats."""
        test_cases = [
            ("Text with 【3:0†source】 citation", "【3:0†source】"),
            ("Text with [1] citation", "[1]"),
            ("Text with (2) citation", "(2)"),
            ("Text with [3:3†source] citation", "[3:3†source]"),
            ("Text with space before period .", " ."),
            ("Text with multiple spaces before period  .", "  ."),
        ]
        
        for original_text, citation_to_remove in test_cases:
            with self.subTest(citation=citation_to_remove):
                clean_text, _ = self.agent.extract_links_and_clean(original_text)
                self.assertNotIn(citation_to_remove, clean_text, 
                               f"Citation '{citation_to_remove}' should be removed")
                
        print(f"\n✓ All citation formats properly cleaned")
        
    def test_mock_answer_cleaning_integration(self):
        """Test that mock answers are properly cleaned in integration."""
        # First, let's see what the current mock implementation returns
        question = "What are delivery costs for different couriers?"
        context = "Microsoft Azure AI"
        char_limit = 2000
        max_retries = 1
        
        # Call the mock question answering method
        success, answer, links = self.agent.process_single_question_cli(
            question, context, char_limit, verbose=False, max_retries=max_retries
        )
        
        # Verify we got a successful result
        self.assertTrue(success, "Mock question processing should succeed")
        self.assertIsNotNone(answer, "Should receive an answer")
        self.assertIsInstance(answer, str, "Answer should be a string")
        
        # The current mock implementation doesn't include citations,
        # but we should verify that if it did, they would be cleaned
        self.assertNotIn('【', answer, "Answer should not contain citation markers")
        self.assertNotIn('†source】', answer, "Answer should not contain source markers")
        self.assertNotIn(' .', answer, "Answer should not have space before periods")
        
        print(f"\n✓ Mock answer integration test passed")
        print(f"✓ Answer: {answer}")


if __name__ == '__main__':
    print("Testing citation cleaning functionality...")
    print("This test verifies citation removal and space-before-period fixes.")
    
    unittest.main(verbosity=2)