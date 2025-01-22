import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

import pandas as pd

from src.agent.llm.json_llm import JsonProcessor
from src.benchmark.data_loader import BenchmarkDataLoader
from src.common.interfaces import Message

logger = logging.getLogger(__name__)

class BenchmarkRunner:
    def __init__(self):
        """Initialize the benchmark runner with data loader and LLM processor."""
        self.data_loader = BenchmarkDataLoader()
        self.llm = JsonProcessor()
        
        # Load company mappings
        mapping_path = Path(__file__).parent / "companies_mapping.csv"
        self.company_data = pd.read_csv(mapping_path)
        self.company_tags = set(self.company_data['tag'].values)
        
        # Create mapping string for prompt
        self.mapping_text = self._create_mapping_text()

    def _create_mapping_text(self) -> str:
        """Create a formatted string of company mappings for the prompt.
        
        Returns:
            str: Formatted company mappings
        """
        mapping_lines = []
        for _, row in self.company_data.iterrows():
            mapping_lines.append(f"{row['name']}: {row['tag']}")
        return "\n".join(mapping_lines)

    def _create_prompt(self, news_item: Dict) -> str:
        """Create a prompt for the LLM to analyze the news item.
        
        Args:
            news_item (Dict): News item containing title and content
            
        Returns:
            str: Formatted prompt for the LLM
        """
        prompt = f"""Analyze the following news article and identify all relevant company stock/crypto symbols that are affected by this news. 
Use the provided company mappings to help identify the correct symbols.

Company Mappings:
{self.mapping_text}

Title: {news_item['title']}
Content: {news_item['content']}

Provide your response in the following JSON format:
{{
    "thought": "Your reasoning for selecting these symbols",
    "actions": [
        {{
            "action": "identify_symbols",
            "symbols": ["SYMBOL1", "SYMBOL2"]
        }}
    ]
}}
"""
        return prompt

    def _get_actual_symbols(self, news_item: Dict) -> Set[str]:
        """Get the actual symbols from the news item.
        
        Args:
            news_item (Dict): News item containing related_symbols
            
        Returns:
            Set[str]: Set of related symbols
        """
        if pd.isna(news_item['related_symbols']):
            return set()
        return set(news_item['related_symbols'].split(';'))

    def _evaluate_prediction(self, predicted: Set[str], actual: Set[str]) -> Dict:
        """Evaluate the prediction against actual symbols.
        
        Args:
            predicted (Set[str]): Predicted symbols
            actual (Set[str]): Actual symbols
            
        Returns:
            Dict: Evaluation metrics
        """
        true_positives = len(predicted.intersection(actual))
        false_positives = len(predicted - actual)
        false_negatives = len(actual - predicted)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }

    async def run_benchmark(self, num_samples: int = 10) -> Dict:
        """Run the benchmark on a sample of news items.
        
        Args:
            num_samples (int): Number of news items to test
            
        Returns:
            Dict: Benchmark results
        """
        results = []
        sample_data = self.data_loader.data.sample(n=num_samples)
        
        for _, news_item in sample_data.iterrows():
            try:
                # Create and process prompt
                prompt = self._create_prompt(news_item)
                message = Message(content=prompt)
                response = await self.llm.process_message(message)
                
                # Extract predicted symbols
                predicted_symbols = set()
                for action in response.get('actions', []):
                    if action.get('action') == 'identify_symbols':
                        symbols = action.get('symbols', [])
                        predicted_symbols.update([s.upper() for s in symbols])
                
                # Filter predictions to only include valid company tags
                predicted_symbols = predicted_symbols.intersection(self.company_tags)
                
                # Get actual symbols and evaluate
                actual_symbols = self._get_actual_symbols(news_item)
                evaluation = self._evaluate_prediction(predicted_symbols, actual_symbols)
                
                results.append({
                    'news_id': news_item['id'],
                    'title': news_item['title'],
                    'predicted_symbols': list(predicted_symbols),
                    'actual_symbols': list(actual_symbols),
                    'precision': evaluation['precision'],
                    'recall': evaluation['recall'],
                    'f1': evaluation['f1']
                })
                
            except Exception as e:
                logger.error(f"Error processing news item {news_item['id']}: {str(e)}")
                continue
        
        # Calculate aggregate metrics
        aggregate_metrics = {
            'precision': sum(r['precision'] for r in results) / len(results),
            'recall': sum(r['recall'] for r in results) / len(results),
            'f1': sum(r['f1'] for r in results) / len(results),
            'total_samples': len(results)
        }
        
        return {
            'individual_results': results,
            'aggregate_metrics': aggregate_metrics
        }

async def main():
    """Run the benchmark and print results."""
    benchmark = BenchmarkRunner()
    results = await benchmark.run_benchmark(num_samples=10)
    
    # Print results to console
    print("\nBenchmark Results:")
    print("=================")
    print(f"\nAggregate Metrics:")
    print(f"Precision: {results['aggregate_metrics']['precision']:.3f}")
    print(f"Recall: {results['aggregate_metrics']['recall']:.3f}")
    print(f"F1 Score: {results['aggregate_metrics']['f1']:.3f}")
    print(f"Total Samples: {results['aggregate_metrics']['total_samples']}")
    
    print("\nDetailed Results:")
    for result in results['individual_results']:
        print(f"\nNews: {result['title']}")
        print(f"Predicted: {result['predicted_symbols']}")
        print(f"Actual: {result['actual_symbols']}")
        print(f"F1 Score: {result['f1']:.3f}")

    # Save results to markdown file
    docs_dir = Path(__file__).parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_path = docs_dir / f"benchmark_results_{timestamp}.md"
    
    with open(markdown_path, 'w') as f:
        f.write("# Benchmark Results\n\n")
        f.write(f"*Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        
        # Write aggregate metrics
        f.write("## Aggregate Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Precision | {results['aggregate_metrics']['precision']:.3f} |\n")
        f.write(f"| Recall | {results['aggregate_metrics']['recall']:.3f} |\n")
        f.write(f"| F1 Score | {results['aggregate_metrics']['f1']:.3f} |\n")
        f.write(f"| Total Samples | {results['aggregate_metrics']['total_samples']} |\n\n")
        
        # Write detailed results
        f.write("## Detailed Results\n\n")
        for result in results['individual_results']:
            f.write(f"### {result['title']}\n\n")
            f.write(f"**News ID:** {result['news_id']}\n\n")
            f.write("| Metric | Details |\n")
            f.write("|--------|----------|\n")
            f.write(f"| Predicted Symbols | {', '.join(result['predicted_symbols'])} |\n")
            f.write(f"| Actual Symbols | {', '.join(result['actual_symbols'])} |\n")
            f.write(f"| Precision | {result['precision']:.3f} |\n")
            f.write(f"| Recall | {result['recall']:.3f} |\n")
            f.write(f"| F1 Score | {result['f1']:.3f} |\n\n")
    
    print(f"\nResults saved to: {markdown_path}")

if __name__ == "__main__":
    asyncio.run(main())
