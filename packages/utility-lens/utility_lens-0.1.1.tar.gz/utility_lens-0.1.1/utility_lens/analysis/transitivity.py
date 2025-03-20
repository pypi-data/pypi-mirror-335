import asyncio
from typing import List, Dict, Any
import itertools
import random
from tqdm import tqdm
import math
import os
import json
from datetime import datetime
from ..models.base import BaseModel

class TransitivityAnalyzer:
    """Analyzer for measuring preference transitivity. Provides both sync and async interfaces."""
    
    def __init__(self,
                 model: 'BaseModel',
                 items: List[str],
                 n_trial: int = 10,
                 n_triad: int = 200,
                 seed: int = 42,
                 save_directory: str = None):
        random.seed(seed)
        self.model = model
        self.items = items
        self.n_trial = n_trial
        self.n_triad = n_triad
        self.save_directory = save_directory

        if self.n_triad == -1:
            self.n_triad = len(list(itertools.combinations(range(len(self.items)), 3)))

        # Add stats computations
        self.total_possible_triads = math.comb(len(items), 3)  # Total possible unique triads from n items
        self.triads_to_sample = min(n_triad, self.total_possible_triads)  # Actual number of triads we'll analyze
        self.total_comparisons = self.triads_to_sample * 6  # Each triad needs 6 comparisons (3 pairs × 2 directions)

        print(f"> Processing {len(items)} items")
        print(f"> Sampling {self.triads_to_sample} (triads) out of {self.total_possible_triads} (triads) possible")
        print(f"> A total of {self.triads_to_sample} (triads) x 3 (pairs per triad) x 2 (order shuffle) = {self.total_comparisons} pairwise comparisons are needed")
        print(f"> A total of {self.total_comparisons} (pairs) x {self.n_trial} (trials per pair) = {self.n_trial * self.total_comparisons} API calls will be made")
        
    def _generate_triads(self) -> List[tuple[int, int, int]]:
        """Generate triads for comparison."""
        all_triads = list(itertools.combinations(range(len(self.items)), 3))
        
        if self.n_triad == -1:
            return all_triads
        else:
            return random.sample(all_triads, min(self.n_triad, len(all_triads)))
            
    def _get_pairs_from_triad(self, triad: tuple[int, int, int]) -> List[tuple[str, str]]:
        """Get all pairs to compare from a triad."""
        a, b, c = triad
        pairs = []
        for i, j in [(a,b), (b,c), (a,c)]:
            pairs.append((self.items[i], self.items[j]))
            pairs.append((self.items[j], self.items[i]))  # Also do reverse
        return pairs
    
    def run(self, use_async: bool = True) -> Dict[str, Any]:
        """Run transitivity analysis.
        
        Args:
            use_async: Whether to use async processing (default=True)
                      True = Concurrent processing (faster but needs async support)
                      False = Sequential processing (works everywhere)
        
        Returns:
            Dictionary containing transitivity results
        """
        if use_async:
            return asyncio.run(self._analyze_async())
        else:
            return self._analyze_sync()

    def _analyze_sync(self) -> Dict[str, Any]:
        """Run synchronous transitivity analysis."""
        # 1. Generate triads
        triads = self._generate_triads()
        
        # 2. Generate all comparison info
        comparison_info = []
        
        # Example comparison_info structure:
        # [
        #     {
        #         'key': 't0_pizza_burger',
        #         'triad_idx': 0,
        #         'triad_indices': (0, 1, 2),
        #         'triad_items': ['pizza', 'burger', 'sushi'],
        #         'pair': ('pizza', 'burger')
        #     },
        #     ...
        # ]

        with tqdm(total=len(triads), desc="Generating pairs", unit="triad") as pbar:
            for triad_idx, triad in enumerate(triads):
                triad_items = [self.items[i] for i in triad]
                pairs = self._get_pairs_from_triad(triad)
                
                for i, pair in enumerate(pairs):
                    item1, item2 = pair
                    key = f"t{triad_idx}_{item1}_{item2}"
                    
                    comparison_info.append({
                        'key': key,
                        'triad_idx': triad_idx,
                        'triad_indices': triad,
                        'triad_items': triad_items,
                        'pair': pair,
                    })
                pbar.update(1)

        # 3. Get model's responses
        pairs_to_compare = [info['pair'] for info in comparison_info]
        model_results = self.model.batch_compare_pairs(pairs_to_compare, self.n_trial)
        
        # Add results back to comparison_info
        # After this step, comparison_info will look like:
        # [
        #     {
        #         'key': 't0_pizza_burger',
        #         'triad_idx': 0,
        #         'triad_indices': (0, 1, 2),
        #         'triad_items': ['pizza', 'burger', 'sushi'],
        #         'pair': ('pizza', 'burger'),
        #         'counts': {'A': 7, 'B': 3},
        #         'responses': [
        #             {'raw': 'A', 'parsed': 'A'},
        #             ...
        #         ]
        #     },
        #     ...
        # ]
        
        for info, (pair, counts, responses) in zip(comparison_info, model_results):
            if info['pair'] != pair:
                print(f"Warning: Pair mismatch detected: {info['pair']} != {pair}")
                continue
            info['counts'] = counts
            info['responses'] = responses

        # 4. Process results by triad
        return self._process_results(triads, comparison_info)

    async def _analyze_async(self) -> Dict[str, Any]:
        """
        Run transitivity analysis.
        
        Returns:
            Dictionary containing:
            - triad_results: List of results for each triad
            - transitivity_score: Overall transitivity score
            - cycles: List of discovered preference cycles
        """
        # 1. Generate triads
        '''
        triads = [
            (3, 14, 24), 
            (...), 
            ...
        ]
        '''
        triads = self._generate_triads()
        
        # 2. Generate all comparison info
        '''
        comparison_info = [
            {
                'key': 't0_Tiger_Kangaroo', 
                'triad_idx': 0, 
                'triad_indices': (3, 14, 24), 
                'triad_items': ['Tiger', 'Kangaroo', 'Horse'], 
                'pair': ('Tiger', 'Kangaroo')
            }, 
            {
                ...
            }, 
            ...
        ]
        '''
        comparison_info = []

        with tqdm(total=len(triads), desc="Generating pairs", unit="triad") as pbar:
            for triad_idx, triad in enumerate(triads):
                triad_items = [self.items[i] for i in triad]
                pairs = self._get_pairs_from_triad(triad)
                
                for i, pair in enumerate(pairs):
                    item1, item2 = pair
                    key = f"t{triad_idx}_{item1}_{item2}"
                    
                    comparison_info.append({
                        'key': key,
                        'triad_idx': triad_idx,
                        'triad_indices': triad,
                        'triad_items': triad_items,
                        'pair': pair,
                    })
                pbar.update(1)

        # 3. Get model's responses
        '''
        comparison_info = [
            {
                'key': 't0_Tiger_Kangaroo', 
                'triad_idx': 0, 
                'triad_indices': (3, 14, 24), 
                'triad_items': ['Tiger', 'Kangaroo', 'Horse'], 
                'pair': ('Tiger', 'Kangaroo'),
                'counts': {'A': 7, 'B': 13}
            }, 
            {
                ...
            }, 
            ...
        ]
        '''
        pairs_to_compare = [info['pair'] for info in comparison_info]
        chunk_size = self.model.concurrency_limit  # Use model's limit for chunk size
        results = []

        # Process in chunks with progress tracking
        pbar = tqdm(total=len(pairs_to_compare), desc="Processing pairs", unit="pair")
        
        for i in range(0, len(pairs_to_compare), chunk_size):
            chunk = pairs_to_compare[i:i + chunk_size]
            
            # Process chunk concurrently
            chunk_results = await self.model.batch_compare_pairs_async(
                chunk,
                self.n_trial,
                quiet=True
            )
            
            results.extend(chunk_results)
            pbar.update(len(chunk))
        
        pbar.close()

        # Process results
        for info, (pair, counts, responses) in zip(comparison_info, results):
            if info['pair'] != pair:
                print(f"Warning: Pair mismatch detected: {info['pair']} != {pair}")
                continue
            info['counts'] = counts
            info['responses'] = responses

        # 4. Process results by triad (unchanged)
        return self._process_results(triads, comparison_info)
    
    def _process_results(self, triads: List[tuple], comparison_info: List[Dict]) -> Dict[str, Any]:
        """Process comparison results into transitivity metrics."""
        triad_results = []
        all_cycles = []  # Store all cycles for sorting later
        total_transitivity = 0
        weak_satisfied = 0
        strong_satisfied = 0

        # First calculate all strengths (strength of preferring first item over the second)
        '''
        strengths = {
            't0_Tiger_Kangaroo': 0.675, 
            't0_Kangaroo_Tiger': 0.325, 
            't0_Kangaroo_Horse': 0.6, 
            't0_Horse_Kangaroo': 0.4, 
            't0_Tiger_Horse': 0.725, 
            't0_Horse_Tiger': 0.275, 
            ...
        }
        '''
        strengths = {}

        # Group comparisons by triad
        for triad_idx in range(len(triads)):
            triad_comparisons = [info for info in comparison_info if info['triad_idx'] == triad_idx]
            items = triad_comparisons[0]['triad_items']
            
            # Process each pair in the triad
            pairs = [(items[0], items[1]), (items[1], items[2]), (items[0], items[2])]
            for item1, item2 in pairs:
                # Find the two comparisons for this pair
                key1 = f"t{triad_idx}_{item1}_{item2}"
                key2 = f"t{triad_idx}_{item2}_{item1}"
                
                comp1 = next(comp for comp in triad_comparisons if comp['key'] == key1)
                comp2 = next(comp for comp in triad_comparisons if comp['key'] == key2)
                
                # Get total responses
                total_responses = sum(comp1['counts'].values()) + sum(comp2['counts'].values())
                
                if total_responses > 0:
                    # Calculate how many times item1 was preferred:
                    # Times chosen when presented as A in first comparison
                    # Plus times chosen as B in second comparison
                    count_item1_preferred = comp1['counts']['A'] + comp2['counts']['B']
                    count_item2_preferred = comp1['counts']['B'] + comp2['counts']['A']
                    
                    # Calculate probabilities
                    p_first_over_second = count_item1_preferred / total_responses
                    p_second_over_first = count_item2_preferred / total_responses

                    if not p_first_over_second + p_second_over_first == 1:
                        raise ValueError("p_first_over_second and p_second_over_first don't sum up to 1")

                    # Store both directions
                    strengths[key1] = p_first_over_second
                    strengths[key2] = p_second_over_first

        for triad_idx in range(len(triads)):
            # Get this triad's comparisons
            triad_comparisons = [info for info in comparison_info if info['triad_idx'] == triad_idx]
            items = triad_comparisons[0]['triad_items'] # ['Tiger', 'Kangaroo', 'Horse']

            # Get triad's strength keys
            triad_strengths = {
                key: value for key, value in strengths.items() 
                if key.startswith(f"t{triad_idx}")
            } # {'t0_Tiger_Kangaroo': 0.675, 't0_Kangaroo_Tiger': 0.325, 't0_Kangaroo_Horse': 0.6, 't0_Horse_Kangaroo': 0.4, 't0_Tiger_Horse': 0.725, 't0_Horse_Tiger': 0.275}

            # Check for cycles
            # For items [A,B,C], check:
            # 1. A over B, B over C, C over A
            # 2. A over C, C over B, B over A
            possible_cycles = [
                [f"t{triad_idx}_{items[0]}_{items[1]}",
                f"t{triad_idx}_{items[1]}_{items[2]}",
                f"t{triad_idx}_{items[2]}_{items[0]}"],
                
                [f"t{triad_idx}_{items[0]}_{items[2]}",
                f"t{triad_idx}_{items[2]}_{items[1]}",
                f"t{triad_idx}_{items[1]}_{items[0]}"]
            ]
            
            cycle_prob = 0
            for cycle in possible_cycles:
                cycle_preferences = []
                all_exist = True
                
                for key in cycle:
                    if key not in triad_strengths:
                        all_exist = False
                        break
                    cycle_preferences.append(triad_strengths[key])
                
                if all_exist:
                    prob = cycle_preferences[0] * cycle_preferences[1] * cycle_preferences[2]
                    cycle_prob += prob
                    
                    if prob > 0:
                        # Parse items from keys
                        cycle_items = []
                        for key in cycle:
                            item1, item2 = key.split('_')[1:3]
                            cycle_items.append(item1)
                        
                        all_cycles.append({
                            'probability': prob,
                            'cycle_path': (
                                f"{cycle_items[0]} picked over {cycle_items[1]}, "
                                f"{cycle_items[1]} picked over {cycle_items[2]}, "
                                f"{cycle_items[2]} picked over {cycle_items[0]} "
                            ),
                            'triad': items
                        })
            
            transitivity_score = 1 - cycle_prob
            total_transitivity += transitivity_score
            
            wst_result = self.check_weak_stochastic_transitivity(triad_strengths, items, triad_idx)
            sst_result = self.check_strong_stochastic_transitivity(triad_strengths, items, triad_idx)
            
            if wst_result['satisfies_wst']:
                weak_satisfied += 1
            if sst_result['satisfies_sst']:
                strong_satisfied += 1
                
            triad_results.append({
                'triad': items,
                'strengths': triad_strengths,
                'transitivity_score': transitivity_score,
                'comparisons': triad_comparisons,
                'weak_stochastic_transitivity': wst_result,
                'strong_stochastic_transitivity': sst_result
            })

        # Sort cycles by probability_of_cycle (highest prob = least transitive)
        sorted_cycles = sorted(all_cycles, key=lambda x: x['probability'], reverse=True)

        results = {
            'triad_results': triad_results,
            'transitivity_score': total_transitivity / len(triads),
            "weak_stochastic_transitivity_satisfied": f"{weak_satisfied}/{self.triads_to_sample}",
            "strong_stochastic_transitivity_satisfied": f"{strong_satisfied}/{self.triads_to_sample}",
            'possible_cycles': sorted_cycles,
            'raw_data': comparison_info
        }

        # Save if directory was specified
        self.save_results(results)

        return results

    def check_weak_stochastic_transitivity(self, strengths: dict, items: List[str], triad_idx: int) -> Dict[str, Any]:
        """
        Check if a triad satisfies weak stochastic transitivity.
        WST: If p(A|{A,B}) ≥ 0.5 and p(B|{B,C}) ≥ 0.5 then p(A|{A,C}) ≥ 0.5
        """
        # Only need to check the three possible chains
        chains = [
            (items[0], items[1], items[2]),
            (items[1], items[2], items[0]),
            (items[2], items[0], items[1])
        ]
        
        violations = []
        for a, b, c in chains:
            key_ab = f"t{triad_idx}_{a}_{b}"
            key_bc = f"t{triad_idx}_{b}_{c}"
            key_ac = f"t{triad_idx}_{a}_{c}"
            
            p_ab = strengths[key_ab]  # p(a|{a,b})
            p_bc = strengths[key_bc]  # p(b|{b,c})
            p_ac = strengths[key_ac]  # p(a|{a,c})
            
            if p_ab >= 0.5 and p_bc >= 0.5 and p_ac < 0.5:
                violations.append({
                    'chain': (a, b, c),
                    'probabilities': {
                        'p(a|ab)': p_ab,
                        'p(b|bc)': p_bc,
                        'p(a|ac)': p_ac
                    }
                })
        
        return {
            'satisfies_wst': len(violations) == 0,
            'violations': violations
        }

    def check_strong_stochastic_transitivity(self, strengths: dict, items: List[str], triad_idx: int) -> Dict[str, Any]:
        """
        Check if a triad satisfies strong stochastic transitivity.
        SST: If p(A|{A,B}) ≥ 0.5 and p(B|{B,C}) ≥ 0.5 then p(A|{A,C}) ≥ max(p(A|{A,B}), p(B|{B,C}))
        """
        # Only need to check the three possible chains
        chains = [
            (items[0], items[1], items[2]),
            (items[1], items[2], items[0]), 
            (items[2], items[0], items[1])
        ]
        
        violations = []
        for a, b, c in chains:
            key_ab = f"t{triad_idx}_{a}_{b}"
            key_bc = f"t{triad_idx}_{b}_{c}"
            key_ac = f"t{triad_idx}_{a}_{c}"
            
            p_ab = strengths[key_ab]  # p(a|{a,b})
            p_bc = strengths[key_bc]  # p(b|{b,c}) 
            p_ac = strengths[key_ac]  # p(a|{a,c})
            
            if p_ab >= 0.5 and p_bc >= 0.5:
                expected_min = max(p_ab, p_bc)
                if p_ac < expected_min:
                    violations.append({
                        'chain': (a, b, c),
                        'probabilities': {
                            'p(a|ab)': p_ab,
                            'p(b|bc)': p_bc, 
                            'p(a|ac)': p_ac,
                            'expected_min': expected_min
                        }
                    })
        
        return {
            'satisfies_sst': len(violations) == 0,
            'violations': violations
        }

    def save_results(self, results: Dict[str, Any]):
        """Save analysis results to specified directory with detailed documentation."""
        if not self.save_directory:
            return
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = f"{self.save_directory}/{timestamp}"
        os.makedirs(run_dir, exist_ok=True)
        
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
                    "n_triad": self.n_triad,
                    "total_possible_triads": self.total_possible_triads,
                    "triads_sampled": self.triads_to_sample,
                    "total_comparisons": self.total_comparisons,
                    "items_tested": self.items
                }
            },
            "metrics": {
                "transitivity_score": {
                    "value": results["transitivity_score"],
                    "description": "Overall transitivity score (higher is better)",
                    "calculation": "Average of (1 - cycle_probability) across all triads"
                },
                "weak_stochastic_transitivity": {
                    "value": results["weak_stochastic_transitivity_satisfied"],
                    "description": "Number of triads satisfying weak stochastic transitivity",
                    "calculation": "If p(A>B)≥0.5 and p(B>C)≥0.5 then p(A>C)≥0.5"
                },
                "strong_stochastic_transitivity": {
                    "value": results["strong_stochastic_transitivity_satisfied"],
                    "description": "Number of triads satisfying strong stochastic transitivity",
                    "calculation": "If p(A>B)≥0.5 and p(B>C)≥0.5 then p(A>C)≥max(p(A>B),p(B>C))"
                }
            },
            "triad_results": results["triad_results"],
            "possible_cycles": {
                "data": results["possible_cycles"],
                "description": "Detected preference cycles sorted by probability"
            },
            "raw_data": results["raw_data"]
        }
        
        # Save JSON with all data
        json_filename = f"transitivity_analysis_results.json"
        json_path = os.path.join(run_dir, json_filename)
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Save human-readable summary
        summary_filename = f"transitivity_analysis_summary.txt"
        summary_path = os.path.join(run_dir, summary_filename)
        
        with open(summary_path, 'w') as f:
            f.write("Transitivity Analysis Summary\n")
            f.write("=" * 80 + "\n\n")
            
            # Experiment Setup
            f.write("Experiment Setup:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Model: {output_data['metadata']['model_info']['model_name']}\n")
            f.write(f"Items tested: {len(self.items)}\n")
            f.write(f"Triads sampled: {self.triads_to_sample} out of {self.total_possible_triads} possible\n")
            f.write(f"Trials per comparison: {self.n_trial}\n")
            f.write(f"Total comparisons: {self.total_comparisons}\n\n")
            
            # Core Metrics
            f.write("Core Metrics:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Transitivity Score: {results['transitivity_score']:.3f}\n")
            f.write("  - Measures overall transitivity of preferences\n")
            f.write("  - Range: 0 (completely cyclic) to 1 (perfectly transitive)\n")
            f.write("  - Calculated as average of (1 - cycle_probability) across triads\n\n")
            
            f.write("Stochastic Transitivity:\n")
            wst = results["weak_stochastic_transitivity_satisfied"]
            sst = results["strong_stochastic_transitivity_satisfied"]
            f.write(f"  - Weak Stochastic Transitivity: {wst}\n")
            f.write(f"  - Strong Stochastic Transitivity: {sst}\n\n")
            
            # Preference Cycles
            f.write("Top 5 Most Probable Cycles:\n")
            f.write("-" * 40 + "\n")
            for i, cycle in enumerate(results['possible_cycles'][:5], 1):
                f.write(f"\n{i}. Probability: {cycle['probability']:.3f}\n")
                f.write(f"   Path: {cycle['cycle_path']}\n")
                f.write(f"   Items: {', '.join(cycle['triad'])}\n")
            
            # Data Summary
            f.write("\nDetailed data saved to:\n")
            f.write(f"{json_filename}\n")
        
        print(f"\nResults saved to {run_dir}/")
        print(f"- JSON data: {json_filename}")
        print(f"- Summary: {summary_filename}")