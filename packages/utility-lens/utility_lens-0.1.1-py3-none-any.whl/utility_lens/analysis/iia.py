import asyncio
from typing import List, Dict, Any, Tuple, Optional
import itertools
import random
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
import os
import json
from datetime import datetime
from ..models.base import BaseModel, convert_numpy

class IIAAnalyzer:
    """Analyzer for measuring Independence of Irrelevant Alternatives (IIA)."""
    
    def __init__(
        self,
        model: 'BaseModel',
        items: List[str],
        n_trial: int = 10,
        n_pairs: int = 200,
        seed: int = 42,
        threshold: float = 0.1,
        save_directory: Optional[str] = None
    ):
        """Initialize IIA analyzer.
        
        Args:
            model: Model instance for comparisons
            items: List of items to compare
            n_trial: Number of trials per comparison
            n_pairs: Number of base pairs to sample (-1 for all pairs)
            context_size: Number of additional items to add when testing IIA
            seed: Random seed
            threshold: Threshold to be considered violence of IIA
            save_directory: Optional directory to save results
        """
        random.seed(seed)
        self.model = model
        self.items = items
        self.n_trial = n_trial
        self.n_pairs = n_pairs
        self.context_size = 1 # always 1 for now (max three items)
        self.threshold = threshold
        self.save_directory = save_directory

        # Calculate total possible pairs
        self.total_possible_pairs = len(list(itertools.combinations(range(len(items)), 2)))
        self.pairs_to_sample = min(self.n_pairs if self.n_pairs != -1 else self.total_possible_pairs,
                                 self.total_possible_pairs)

        print(f"> Processing {len(items)} items")
        print(f"> Sampling {self.pairs_to_sample} pairs out of {self.total_possible_pairs} possible pairs")
        print(f"> Testing each pair with {self.context_size} additional context item(s)")
        print(f"> Each comparison repeated {n_trial} times for reliability")
        
    def _generate_test_cases(self) -> List[Dict[str, Any]]:
        """Generate pairs and their context sets for testing."""
        # Generate all possible pairs
        all_pairs = list(itertools.combinations(self.items, 2))
        
        # Sample pairs if needed
        test_pairs = random.sample(all_pairs, self.pairs_to_sample)
        
        '''
        test_cases = [
            {
                'pair': ('elephant', 'lion'),
                'context_sets': [
                    ['giraffe'],  # First context set
                    ['hippo'],    # Alternative context
                    ['zebra']     # Another context to test
                ]
            },
            {
                'pair': ('human', 'dolphin'), 
                'context_sets': [...]
            },
            ...
        ]
        '''
        test_cases = []
        for pair in test_pairs:
            # Get potential context items (all items except the pair)
            context_items = [item for item in self.items if item not in pair]
            
            # Sample context sets for this pair
            if len(context_items) >= self.context_size:
                # Test 3 different contexts per pair
                context_sets = [
                    random.sample(context_items, self.context_size)
                    for _ in range(3)  
                ]
            else:
                context_sets = [context_items]  # Use all available if not enough
                
            test_cases.append({
                'pair': pair,
                'context_sets': context_sets
            })
            
        return test_cases

    def _calculate_preference_strength(self, counts: Dict[str, int]) -> float:
        """Calculate preference strength from counts, handling context choices."""
        total_ab = counts['A'] + counts['B']  # Exclude OTHER choices
        if total_ab == 0:
            return 0.5  # No preference when neither A nor B was chosen
        return counts['A'] / total_ab

    def run(self, use_async: bool = True) -> Dict[str, Any]:
        """Run IIA analysis.
        
        Args:
            use_async: Whether to use async processing
        
        Returns:
            Dictionary containing IIA analysis results
        """
        if use_async:
            return asyncio.run(self._analyze_async())
        else:
            return self._analyze_sync()

    def _analyze_sync(self) -> Dict[str, Any]:
        """Run synchronous IIA analysis.
        """
        # Generate test cases
        # test_cases = [
        #     {
        #         'pair': ('elephant', 'lion'),  # Pair to compare
        #         'context_sets': [  # Sets of context items to test with
        #             ['giraffe'], 
        #             ['hippo'],
        #             ['zebra']
        #         ]
        #     },
        #     ...
        # ]
        test_cases = self._generate_test_cases()
        
        # Test base pairs (without context)
        print("\nTesting base preferences...")
        # base_results = {
        #     ('elephant', 'lion'): (
        #         ('elephant', 'lion'),  # Original pair
        #         {'A': 7, 'B': 3},  # Count of choices
        #         [  # Raw responses
        #             {'raw': 'A', 'parsed': 'A'},
        #             {'raw': 'B', 'parsed': 'B'},
        #             ...
        #         ]
        #     ),
        #     ...
        # }
        base_results = {}
        for case in tqdm(test_cases):
            pair = case['pair']
            results = self.model.batch_compare_pairs([pair], self.n_trial)
            base_results[pair] = results[0]
            
        # Test with context
        print("\nTesting preferences with context...")
        # context_results = [
        #     {
        #         'pair': ('elephant', 'lion'),
        #         'base_preference': 0.7,  # P(elephant > lion)
        #         'context_tests': [
        #             {
        #                 'context': ['giraffe'],
        #                 'preference': 0.6,  # P(elephant > lion | giraffe)
        #                 'shift': 0.1  # |P(A>B) - P(A>B|C)|
        #             },
        #             ...
        #         ]
        #     },
        #     ...
        # ]
        context_results = []
        # violations = [
        #     {
        #         'base_pair': ('elephant', 'lion'),
        #         'original_preference': 0.7,  # P(A>B)
        #         'context_item': 'giraffe',
        #         'new_preference': 0.6,  # P(A>B|C)
        #         'shift': 0.1  # |P(A>B) - P(A>B|C)|
        #     },
        #     ...
        # ]
        violations = []
        all_shifts = []  # Track all preference shifts
    
        for case in tqdm(test_cases):
            pair = case['pair']
            base_counts = base_results[pair][1]
            base_pref = self._calculate_preference_strength(base_counts)
            
            pair_results = {
                'pair': pair,
                'base_preference': base_pref,
                'context_tests': []
            }
            
            # Test each context
            for context_items in case['context_sets']:
                results = self.model.batch_compare_pairs(
                    [pair], 
                    n_trials=self.n_trial,
                    context_items=[context_items[0]]
                )
                context_test = results[0]  # (pair, counts, responses)
                context_counts = context_test[1]
                context_responses = context_test[2]
                
                context_pref = self._calculate_preference_strength(context_counts)
                shift = abs(context_pref - base_pref)
                all_shifts.append(shift)
                
                context_result = {
                    'context': context_items,
                    'preference': context_pref,
                    'shift': shift,
                    'counts': context_counts,
                    'raw_responses': [
                        {
                            'trial': i,
                            'raw': resp['raw'],
                            'parsed': resp['parsed']
                        }
                        for i, resp in enumerate(context_responses)
                    ]
                }
                pair_results['context_tests'].append(context_result)
                
                # Track threshold-based violations separately
                if shift > self.threshold:
                    violations.append({
                        'base_pair': pair,
                        'original_preference': base_pref,
                        'context_item': context_items[0],
                        'new_preference': context_pref,
                        'shift': shift
                    })
                    
            context_results.append(pair_results)
        
        # Calculate all metrics
        metrics = self.calculate_iia_metrics(all_shifts)
        
        results = {
            'iia_score_I': metrics['continuous_score'], 
            'iia_score_II': metrics['threshold_score'], 
            'mean_shift': metrics['mean_shift'],
            'max_shift': metrics['max_shift'],
            'stable_preferences': metrics['total_tests'] - metrics['threshold_violations'],
            'total_tests': metrics['total_tests'],
            'violations': sorted(violations, key=lambda x: abs(x['shift']), reverse=True),
            'pair_results': context_results,
            'raw_data': {
                'base_results': base_results
            }
        }
        
        if self.save_directory:
            self.save_results(results)
            
        return results

    async def _analyze_async(self) -> Dict[str, Any]:
        """Run async IIA analysis with true concurrency."""
        # test_cases = [
        #     {
        #         'pair': ('elephant', 'lion'),  
        #         'context_sets': [
        #             ['giraffe'],  
        #             ['hippo'],
        #             ['zebra']
        #         ]
        #     },
        #     ...
        # ]
        test_cases = self._generate_test_cases()
        
        # Test base preferences without context
        print("\nTesting base preferences...")
        # base_results = {
        #     ('elephant', 'lion'): (
        #         ('elephant', 'lion'),  
        #         {'A': 7, 'B': 3}, 
        #         [  
        #             {'raw': 'A', 'parsed': 'A'},
        #             {'raw': 'B', 'parsed': 'B'},
        #             ...
        #         ]
        #     ),
        #     ...
        # }
        base_results = {}
        pairs_to_test = [case['pair'] for case in test_cases]
        
        base_model_results = await self.model.batch_compare_pairs_async(
            pairs_to_test, 
            self.n_trial,
            quiet=False
        )
        for pair, result in zip(pairs_to_test, base_model_results):
            base_results[pair] = result

        # Prepare all context tests up front for concurrent processing
        print("\nTesting preferences with context...")
        # all_tests = [
        #     {
        #         'pair': ('elephant', 'lion'),
        #         'context': 'giraffe',
        #         'base_preference': 0.7
        #     },
        #     ...  # All tests flattened into single list
        # ]
        all_tests = []
        for case in test_cases:
            pair = case['pair']
            base_pref = self._calculate_preference_strength(base_results[pair][1])
            for context_items in case['context_sets']:
                all_tests.append({
                    'pair': pair,
                    'context': context_items[0],
                    'base_preference': base_pref,
                })

        # pair_results_map = {
        #     ('elephant', 'lion'): {
        #         'pair': ('elephant', 'lion'),
        #         'base_preference': 0.7,
        #         'context_tests': [
        #             {
        #                 'context': ['giraffe'],
        #                 'preference': 0.6,
        #                 'shift': 0.1,
        #                 'counts': {'A': 6, 'B': 4},
        #                 'raw_responses': [...]
        #             },
        #             ...
        #         ]
        #     },
        #     ...
        # }
        pair_results_map = {}
        violations = []
        all_shifts = []

        # Process in chunks for better progress tracking while maintaining concurrency
        chunk_size = self.model.concurrency_limit  # Adjust based on API limits
        pbar = tqdm(total=len(all_tests), desc="Testing with context", unit="test")

        for i in range(0, len(all_tests), chunk_size):
            chunk = all_tests[i:i + chunk_size]
            
            # Process chunk concurrently
            context_model_results = await self.model.batch_compare_pairs_async(
                [test['pair'] for test in chunk],
                self.n_trial,
                context_items=[test['context'] for test in chunk],
                quiet=True
            )
            
            # Process results for this chunk
            for test, result in zip(chunk, context_model_results):
                pair = test['pair']
                context_item = test['context']
                base_pref = test['base_preference']
                
                context_counts = result[1]
                context_responses = result[2]
                context_pref = self._calculate_preference_strength(context_counts)
                shift = abs(context_pref - base_pref)
                all_shifts.append(shift)
                
                # Initialize pair results if needed
                if pair not in pair_results_map:
                    pair_results_map[pair] = {
                        'pair': pair,
                        'base_preference': base_pref,
                        'context_tests': []
                    }
                
                # Add this context test result
                context_result = {
                    'context': [context_item],
                    'preference': context_pref,
                    'shift': shift,
                    'counts': context_counts,
                    'raw_responses': [
                        {
                            'trial': i,
                            'raw': resp['raw'],
                            'parsed': resp['parsed']
                        }
                        for i, resp in enumerate(context_responses)
                    ]
                }
                pair_results_map[pair]['context_tests'].append(context_result)
                
                # Track violations
                if shift > self.threshold:
                    violations.append({
                        'base_pair': pair,
                        'original_preference': base_pref,
                        'context_item': context_item,
                        'new_preference': context_pref,
                        'shift': shift
                    })
                
                pbar.update(1)
        
        pbar.close()

        context_results = list(pair_results_map.values())
        metrics = self.calculate_iia_metrics(all_shifts)
        
        results = {
            'iia_score_I': metrics['continuous_score'],
            'iia_score_II': metrics['threshold_score'],
            'mean_shift': metrics['mean_shift'],
            'max_shift': metrics['max_shift'],
            'stable_preferences': metrics['total_tests'] - metrics['threshold_violations'],
            'total_tests': metrics['total_tests'],
            'violations': sorted(violations, key=lambda x: abs(x['shift']), reverse=True),
            'pair_results': context_results,
            'raw_data': {
                'base_results': base_results
            }
        }
        
        if self.save_directory:
            self.save_results(results)
            
        return results

    def calculate_iia_metrics(self, shifts: List[float]) -> Dict[str, float]:
        """Calculate comprehensive IIA metrics.
        
        Args:
            shifts: List of preference shifts |P(A>B) - P(A>B|C)| for each test
            
        Returns:
            Dictionary with various IIA metrics
        """
        if not shifts:
            return {
                "continuous_score": 1.0,
                "threshold_score": 1.0,
                "mean_shift": 0.0,
                "max_shift": 0.0,
                "threshold_violations": 0,
                "total_tests": 0,
                "violation_rate": 0.0
            }
        
        mean_shift = sum(shifts) / len(shifts)
        max_shift = max(shifts)
        
        # Continuous score that doesn't depend on threshold
        # 1 - mean_shift gives us a score from 0 (worst) to 1 (best)
        continuous_score = 1 - mean_shift
        
        # Traditional threshold-based metrics
        threshold_violations = sum(1 for shift in shifts if shift > self.threshold)
        threshold_score = (len(shifts) - threshold_violations) / len(shifts)
        
        return {
            "continuous_score": continuous_score, 
            "threshold_score": threshold_score,
            "mean_shift": mean_shift,
            "max_shift": max_shift,
            "threshold_violations": threshold_violations,
            "total_tests": len(shifts),
            "violation_rate": threshold_violations / len(shifts)
        }

    def save_results(self, results: Dict[str, Any]):
        """Save analysis results to specified directory with detailed documentation."""
        if not self.save_directory:
            return
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = f"{self.save_directory}/{timestamp}"
        os.makedirs(run_dir, exist_ok=True)
        
        # Convert tuple keys to strings in base_results
        json_safe_base_results = {}
        for pair, data in results["raw_data"]["base_results"].items():
            # Convert tuple key to string representation
            key = f"{pair[0]}_{pair[1]}"
            json_safe_base_results[key] = {
                "pair": list(pair),  # Convert tuple to list
                "counts": data[1],
                "raw_responses": [
                    {
                        "trial": i,
                        "raw": resp["raw"],
                        "parsed": resp["parsed"]
                    }
                    for i, resp in enumerate(data[2])
                ]
            }
        
        # Prepare results summary for JSON
        output_data = {
            "metadata": {
                "timestamp": timestamp,
                "model_info": {
                    "model_name": getattr(self.model, 'model_name', 'unknown'),
                    "max_tokens": getattr(self.model, 'max_tokens', 'unknown'),
                    "concurrency_limit": getattr(self.model, 'concurrency_limit', 'unknown')
                },
                "experiment_parameters": {
                    "n_items": len(self.items),
                    "n_trial": self.n_trial,
                    "n_pairs": self.n_pairs,
                    "context_size": self.context_size,
                    "total_possible_pairs": self.total_possible_pairs,
                    "pairs_sampled": self.pairs_to_sample,
                    "violation_threshold": self.threshold,
                    "items_tested": self.items
                }
            },
            "metrics": {
                "iia_score_I": {
                    "value": results["iia_score_I"],
                    "description": "Continuous score independent of threshold",
                    "calculation": "1 - mean(|P(A>B) - P(A>B|C)|)"
                },
                "iia_score_II": {
                    "value": results["iia_score_II"],
                    "description": "Threshold-based score",
                    "calculation": f"proportion of shifts ≤ {self.threshold}"
                },
                "mean_shift": results["mean_shift"],
                "max_shift": results["max_shift"],
                "stable_preferences": results["stable_preferences"],
                "total_tests": results["total_tests"]
            },
            "violations": results["violations"],
            "pair_results": results["pair_results"],
            "raw_data": {
                "base_results": json_safe_base_results
            }
        }
        
        # Save JSON with all data
        json_filename = f"iia_analysis_results.json"
        json_path = os.path.join(run_dir, json_filename)
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"iia_analysis_summary.txt"
        summary_path = os.path.join(run_dir, summary_filename)
        
        with open(summary_path, 'w') as f:
            f.write("Independence of Irrelevant Alternatives (IIA) Analysis Summary\n")
            f.write("=" * 80 + "\n\n")
            
            # Experiment Setup
            f.write("Experiment Setup:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Model: {output_data['metadata']['model_info']['model_name']}\n")
            f.write(f"Items tested: {len(self.items)}\n")
            f.write(f"Pairs sampled: {self.pairs_to_sample} out of {self.total_possible_pairs} possible pairs\n")
            f.write(f"Trials per comparison: {self.n_trial}\n")
            f.write(f"Context size: {self.context_size}\n\n")
            
            # Core Metrics
            f.write("Core Metrics:\n")
            f.write("-" * 40 + "\n")
            f.write(f"IIA Score I (Continuous): {results['iia_score_I']:.3f}\n")
            f.write("  - Threshold-independent measure of preference stability\n")
            f.write("  - Calculation: 1 - mean(|P(A>B) - P(A>B|C)|)\n")
            f.write("  - Range: 0 (unstable) to 1 (perfectly stable)\n\n")
            
            f.write(f"IIA Score II (Threshold-based): {results['iia_score_II']:.3f}\n")
            f.write(f"  - Proportion of preference shifts ≤ {self.threshold}\n")
            f.write(f"  - {results['stable_preferences']} stable pairs out of {results['total_tests']} tests\n\n")
            
            f.write("Shift Analysis:\n")
            f.write(f"  - Mean shift: {results['mean_shift']:.3f}\n")
            f.write(f"  - Max shift: {results['max_shift']:.3f}\n\n")
            
            # Major Violations
            f.write("Top 5 Largest Preference Shifts:\n")
            f.write("-" * 40 + "\n")
            for i, v in enumerate(results['violations'][:5], 1):
                f.write(f"\n{i}. {v['base_pair'][0]} vs {v['base_pair'][1]}:\n")
                f.write(f"   Base preference: {v['original_preference']:.3f}\n")
                f.write(f"   With '{v['context_item']}': {v['new_preference']:.3f}\n")
                f.write(f"   Shift: {v['shift']:.3f}\n")
            
            # Data Summary
            f.write("\nDetailed data saved to:\n")
            f.write(f"{json_filename}\n")
            
        print(f"\nResults saved to {run_dir}/")
        print(f"- JSON data: {json_filename}")
        print(f"- Summary: {summary_filename}")