#!/usr/bin/env python3
"""
Test that demonstrates the citation cleaning fix works in the actual workflow.

This test monkey-patches the mock implementation to return text with citations,
then verifies that the workflow cleans them properly.
"""

import unittest
import sys
import os

# Add the parent directory to Python path to import question_answerer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from question_answerer import QuestionnaireAgentUI


class TestWorkflowCitationCleaning(unittest.TestCase):
    """Test citation cleaning in the actual workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.agent = QuestionnaireAgentUI(headless_mode=True, mock_mode=True)
        
    def test_workflow_cleans_citations(self):
        """Test that the workflow properly cleans citations from answers."""
        
        # Store the original mock implementation
        original_mock_impl = self.agent._execute_question_answerer_mock
        
        def mock_with_citations(question, context, char_limit, attempt_history=None):
            """Mock implementation that returns text with citations."""
            self.agent.log_reasoning("Question Answerer (MOCK): Generating mock response with citations")
            
            # Return answer with citations and space-before-period issues (like in the example)
            mock_answer = """For deliveries over 5km, MetroParcel is the most cost-efficient courier, with an average delivery cost of $22.50. RapidWay ($23.04) and BlueArrow Logistics ($23.22) are also competitive options. Ludus Dryden is the least cost-efficient, costing $35.13 on average for these distances 【3:0†source】 .

Based on structured data related to Microsoft Azure, FedEx is the most commonly used courier for Azure shipments. This conclusion is supported by shipment records showing FedEx as the frequent choice for Azure-related logistics 【message_idx:search_0†source】 .

Based on the data, the largest customer is identified by having the highest number of deliveries. CustomerKey 11607 is the largest customer, receiving a total of 92 deliveries, which is the most among all customers listed in the dataset ."""
            
            self.agent.log_reasoning(f"Question Answerer (MOCK): Generated response with citations")
            return mock_answer, []
        
        # Temporarily replace the mock implementation
        self.agent._execute_question_answerer_mock = mock_with_citations
        
        try:
            # Process a question
            question = "What are the delivery costs and customer details?"
            context = "Microsoft Azure AI"
            char_limit = 2000
            max_retries = 1
            
            # Call the workflow
            success, answer, links = self.agent.process_single_question_cli(
                question, context, char_limit, verbose=True, max_retries=max_retries
            )
            
            # Verify we got a successful result
            self.assertTrue(success, "Question processing should succeed")
            self.assertIsNotNone(answer, "Should receive an answer")
            self.assertIsInstance(answer, str, "Answer should be a string")
            
            # Verify citations are cleaned
            self.assertNotIn('【3:0†source】', answer, "Citation 【3:0†source】 should be removed from final answer")
            self.assertNotIn('【message_idx:search_0†source】', answer, "Citation 【message_idx:search_0†source】 should be removed from final answer")
            
            # Verify space-before-period is fixed
            self.assertNotIn(' .', answer, "Space before period should be fixed in final answer")
            
            # Verify the content is preserved
            self.assertIn('MetroParcel is the most cost-efficient courier', answer)
            self.assertIn('FedEx is the most commonly used courier', answer)
            self.assertIn('CustomerKey 11607 is the largest customer', answer)
            
            print(f"\n✓ Workflow successfully cleaned citations from answer")
            print(f"✓ Final answer length: {len(answer)} characters")
            print(f"✓ Citations removed and spacing fixed")
            print(f"✓ Answer preview: {answer[:200]}...")
            
        finally:
            # Restore the original mock implementation
            self.agent._execute_question_answerer_mock = original_mock_impl


if __name__ == '__main__':
    print("Testing workflow citation cleaning...")
    print("This test verifies that the workflow properly cleans citations from answers.")
    
    unittest.main(verbosity=2)