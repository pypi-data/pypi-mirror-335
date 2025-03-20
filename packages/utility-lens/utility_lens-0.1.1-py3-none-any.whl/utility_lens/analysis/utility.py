import numpy as np
import torch
import torch.nn.functional as F
from typing import List, Dict, Any, Optional, Union
import os
from tqdm import tqdm
import json
import random
import itertools
from datetime import datetime
from ..models.base import BaseModel, convert_numpy

class UtilityAnalyzer:
    def __init__(
        self,
        model: BaseModel,
        items: List[str],
        n_trial: int = 10,
        n_pairs: int = 200,
        seed: int = 42,
        save_directory: Optional[str] = None
    ):
        """Initialize utility analyzer.
        
        Args:
            model: Model instance for comparisons
            items: List of items to compare
            n_trial: Number of trials per pair
            n_pairs: Number of pairs to sample (-1 for all pairs)
            seed: Random seed
            save_directory: Optional directory to save results
        """
        self.model = model
        self.items = items
        self.n_trial = n_trial
        self.n_pairs = n_pairs if n_pairs != -1 else None
        self.seed = seed
        self.save_directory = save_directory

        random.seed(seed)
        np.random.seed(seed)

        # Create options with IDs
        self.options = [{'id': idx, 'description': desc} for idx, desc in enumerate(items)]
        self.option_id_to_idx = {opt['id']: idx for idx, opt in enumerate(self.options)}

    def _generate_pairs(self) -> Dict[str, Any]:
        """Generate pairs for comparison."""
        all_pairs = list(itertools.combinations(range(len(self.items)), 2))
        n_possible_pairs = len(all_pairs)
        n_pairs = min(self.n_pairs or n_possible_pairs, n_possible_pairs)

        print(f"> Processing {len(self.items)} items")
        print(f"> Sampling {n_pairs} unique item pairs out of {n_possible_pairs} possible pairs")
        print(f"> Each pair will be compared in both directions (A vs B, B vs A)")
        print(f"> Total comparisons needed: {n_pairs} (pairs) × 2 (directions) = {2 * n_pairs} comparisons")
        print(f"> Each comparison repeated {self.n_trial} times for reliability")
        print(f"> Total API calls required: {2 * n_pairs} (comparisons) × {self.n_trial} (trials) = {2 * n_pairs * self.n_trial} calls")

        sampled_pairs = random.sample(all_pairs, n_pairs)

        # Generate pairs data structure
        pairs_data = {'pairs': []}
        prompt_list = []
        prompt_idx = 0

        for pair_idx, (A_idx, B_idx) in enumerate(sampled_pairs):
            option_A = self.options[A_idx]
            option_B = self.options[B_idx]

            pair_data = {
                'pair_id': pair_idx,
                'option_A': option_A,
                'option_B': option_B,
                'prompts': []
            }

            # Generate both directions
            for direction in ['original', 'flipped']:
                if direction == 'original':
                    option1, option2 = option_A['description'], option_B['description']
                else:
                    option1, option2 = option_B['description'], option_A['description']

                pair_data['prompts'].append({
                    'prompt_idx': prompt_idx,
                    'direction': direction,
                    'responses': []
                })
                prompt_list.append((option1, option2))
                prompt_idx += 1

            pairs_data['pairs'].append(pair_data)

        return pairs_data, prompt_list

    def _process_model_responses(self, pairs_data: Dict[str, Any], model_results: List[Any]) -> Dict[str, Any]:
        """Process raw model responses into counts and probabilities."""
        for pair_data in pairs_data['pairs']:
            counts = {'A': 0, 'B': 0}
            total_responses = 0
            
            for prompt_data in pair_data['prompts']:
                prompt_idx = prompt_data['prompt_idx']
                direction = prompt_data['direction']
                
                # Unpack all three values now
                pair, pair_counts, raw_responses = model_results[prompt_idx]
                
                if direction == 'original':
                    prompt_data['responses'] = raw_responses
                    counts['A'] += pair_counts['A']
                    counts['B'] += pair_counts['B']
                else:
                    prompt_data['responses'] = raw_responses
                    counts['A'] += pair_counts['B']
                    counts['B'] += pair_counts['A']
                
                total_responses += sum(pair_counts[k] for k in ['A', 'B'])

            pair_data['counts'] = counts
            pair_data['total_responses'] = total_responses
            
            if total_responses > 0:
                pair_data['probabilities'] = {
                    'A': counts['A'] / total_responses,
                    'B': counts['B'] / total_responses
                }
            else:
                pair_data['probabilities'] = {'A': 0, 'B': 0}

        return pairs_data

    def _extract_preference_counts(self, pairs_data: Dict[str, Any]) -> Dict[Any, Dict[int, int]]:
        """Extract preference counts for model fitting."""
        preference_counts = {}
        
        for pair_data in pairs_data['pairs']:
            A_idx = pair_data['option_A']['id']
            B_idx = pair_data['option_B']['id']
            counts = pair_data.get('counts', {'A': 0, 'B': 0})
            
            if sum(counts.values()) > 0:
                preference_counts[(A_idx, B_idx)] = {
                    A_idx: counts['A'],
                    B_idx: counts['B']
                }

        return preference_counts

    def _fit_bradley_terry(self, preference_counts: Dict, num_epochs: int = 1000, 
                          learning_rate: float = 0.01, use_soft_labels: bool = True):
        """Fit Bradley-Terry model to get utilities."""
        n_options = len(self.options)
        
        # Initialize parameters with small random values
        utilities = torch.randn(n_options) * 0.01
        utilities = torch.nn.Parameter(utilities)
        optimizer = torch.optim.Adam([utilities], lr=learning_rate)

        # Prepare data
        idx_A_list = []
        idx_B_list = []
        counts_A_list = []
        counts_B_list = []
        total_counts_list = []
        p_A_list = []

        for (A_idx, B_idx), counts in preference_counts.items():
            idx_A = self.option_id_to_idx[A_idx]
            idx_B = self.option_id_to_idx[B_idx]
            count_A = counts.get(A_idx, 0)
            count_B = counts.get(B_idx, 0)
            total = count_A + count_B
            if total == 0:
                continue
            idx_A_list.append(idx_A)
            idx_B_list.append(idx_B)
            counts_A_list.append(count_A)
            counts_B_list.append(count_B)
            total_counts_list.append(total)
            p_A_list.append(count_A / total)

        # Convert to tensors
        idx_A_tensor = torch.tensor(idx_A_list)
        idx_B_tensor = torch.tensor(idx_B_list)
        counts_A_tensor = torch.tensor(counts_A_list, dtype=torch.float32)
        counts_B_tensor = torch.tensor(counts_B_list, dtype=torch.float32)
        total_counts_tensor = counts_A_tensor + counts_B_tensor

        # Empirical probabilities
        p_A_tensor = counts_A_tensor / total_counts_tensor

        # Labels based on mode
        if not use_soft_labels:
            labels_tensor = (p_A_tensor >= 0.5).float()
        else:
            labels_tensor = p_A_tensor

        # Training loop
        for epoch in range(num_epochs):
            optimizer.zero_grad()

            # Normalize utilities
            utilities_mean = torch.mean(utilities)
            utilities_std = torch.std(utilities) + 1e-8
            utilities_normalized = (utilities - utilities_mean) / utilities_std

            # Get pair utilities
            u_A = utilities_normalized[idx_A_tensor]
            u_B = utilities_normalized[idx_B_tensor]
            delta_u = u_A - u_B

            # Get probabilities
            prob_A = torch.sigmoid(delta_u)

            # Loss
            loss = F.binary_cross_entropy(prob_A, labels_tensor, reduction='mean')
            
            loss.backward()
            optimizer.step()

            #if epoch % 100 == 0:
            #    print(f"Epoch {epoch}, Loss: {loss.item()}")

        # Final normalization
        with torch.no_grad():
            utilities_mean = torch.mean(utilities)
            utilities_std = torch.std(utilities) + 1e-8
            utilities_normalized = (utilities - utilities_mean) / utilities_std
            utilities_np = utilities_normalized.detach().numpy()

        # Map to option IDs
        utilities_dict = {
            opt['id']: float(utilities_np[idx])
            for idx, opt in enumerate(self.options)
        }

        # Calculate metrics
        u_A = utilities_np[idx_A_list]
        u_B = utilities_np[idx_B_list]
        delta_u = u_A - u_B
        prob_A = 1 / (1 + np.exp(-delta_u))

        # Log loss
        y_true = labels_tensor.numpy()
        eps = 1e-8
        prob_A = np.clip(prob_A, eps, 1 - eps)
        model_log_loss = -np.mean(
            y_true * np.log(prob_A) + (1 - y_true) * np.log(1 - prob_A)
        )

        # Accuracy
        y_pred = (prob_A >= 0.5).astype(float)
        model_accuracy = np.mean(y_pred == (y_true >= 0.5))

        return utilities_dict, model_log_loss, model_accuracy

    def _fit_thurstonian(self, preference_counts: Dict, num_epochs: int = 1000,
                        learning_rate: float = 0.01, use_soft_labels: bool = True):
        """Fit Thurstonian model to get means and variances."""
        n_options = len(self.options)
        
        # Initialize parameters
        mu = torch.randn(n_options) * 0.01
        s = torch.randn(n_options) * 0.01
        mu = torch.nn.Parameter(mu)
        s = torch.nn.Parameter(s)
        optimizer = torch.optim.Adam([mu, s], lr=learning_rate)

        # Prepare data
        idx_A_list = []
        idx_B_list = []
        counts_A_list = []
        counts_B_list = []

        for (A_idx, B_idx), counts in preference_counts.items():
            idx_A = self.option_id_to_idx[A_idx]
            idx_B = self.option_id_to_idx[B_idx]
            count_A = counts.get(A_idx, 0)
            count_B = counts.get(B_idx, 0)
            total = count_A + count_B
            if total == 0:
                continue
            idx_A_list.append(idx_A)
            idx_B_list.append(idx_B)
            counts_A_list.append(count_A)
            counts_B_list.append(count_B)

        # Convert to tensors
        idx_A_tensor = torch.tensor(idx_A_list)
        idx_B_tensor = torch.tensor(idx_B_list)
        counts_A_tensor = torch.tensor(counts_A_list, dtype=torch.float32)
        counts_B_tensor = torch.tensor(counts_B_list, dtype=torch.float32)
        total_counts_tensor = counts_A_tensor + counts_B_tensor

        # Empirical probabilities
        p_A_tensor = counts_A_tensor / total_counts_tensor

        if not use_soft_labels:
            labels_tensor = (p_A_tensor >= 0.5).float()
        else:
            labels_tensor = p_A_tensor

        normal = torch.distributions.Normal(0, 1)

        # Training loop
        for epoch in range(num_epochs):
            optimizer.zero_grad()

            # Normalize mu
            mu_mean = torch.mean(mu)
            mu_std = torch.std(mu) + 1e-8
            mu_normalized = (mu - mu_mean) / mu_std

            # Get variances
            sigma2 = torch.exp(s)  # ensure positive
            sigma2_normalized = sigma2 * (1 / (mu_std + 1e-8)) ** 2

            # Get pair parameters
            mu_A = mu_normalized[idx_A_tensor]
            mu_B = mu_normalized[idx_B_tensor]
            sigma2_A = sigma2_normalized[idx_A_tensor]
            sigma2_B = sigma2_normalized[idx_B_tensor]

            # Calculate probabilities
            variance = sigma2_A + sigma2_B + 1e-8
            delta = mu_A - mu_B
            z = delta / torch.sqrt(variance)
            prob_A = normal.cdf(z)

            # Loss
            loss = F.binary_cross_entropy(prob_A, labels_tensor, reduction='mean')
            
            loss.backward()
            optimizer.step()

            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss.item()}")

        # Final normalization
        with torch.no_grad():
            mu_mean = torch.mean(mu)
            mu_std = torch.std(mu) + 1e-8
            mu_normalized = (mu - mu_mean) / mu_std
            sigma2 = torch.exp(s)
            sigma2_normalized = sigma2 * (1 / (mu_std + 1e-8)) ** 2

            mu_np = mu_normalized.detach().numpy()
            sigma2_np = sigma2_normalized.detach().numpy()

        # Map to option IDs
        utilities_dict = {
            opt['id']: {
                'mean': float(mu_np[idx]), 
                'variance': float(sigma2_np[idx])
            }
            for idx, opt in enumerate(self.options)
        }

        # Calculate metrics
        mu_A = mu_np[idx_A_list]
        mu_B = mu_np[idx_B_list]
        sigma2_A = sigma2_np[idx_A_list]
        sigma2_B = sigma2_np[idx_B_list]
        
        variance = sigma2_A + sigma2_B + 1e-8
        delta = mu_A - mu_B
        z = delta / np.sqrt(variance)
        prob_A = normal.cdf(torch.tensor(z)).numpy()

        # Log loss
        y_true = labels_tensor.numpy()
        eps = 1e-8
        prob_A = np.clip(prob_A, eps, 1 - eps)
        model_log_loss = -np.mean(
            y_true * np.log(prob_A) + (1 - y_true) * np.log(1 - prob_A)
        )

        # Accuracy
        y_pred = (prob_A >= 0.5).astype(float)
        model_accuracy = np.mean(y_pred == (y_true >= 0.5))

        return utilities_dict, model_log_loss, model_accuracy

    def run(
        self,
        method: str = "bradley-terry",
        use_soft_labels: bool = True,
        num_epochs: int = 1000,
        learning_rate: float = 0.01,
        use_async: bool = True
        ) -> Dict[str, Any]:
        """Run utility analysis.
        
        Args:
            method: "bradley-terry" or "thurstonian"
            use_soft_labels: Use probability ratios vs binary labels
            num_epochs: Number of training epochs
            learning_rate: Learning rate for optimization
            use_async: Use async processing mode
            
        Returns:
            Dictionary containing analysis results
        """
        # Generate pairs
        pairs_data, prompt_list = self._generate_pairs()
        
        # Get model responses - handle async internally
        if use_async:
            import asyncio
            
            async def process_async():
                # Process in chunks for better progress tracking while maintaining concurrency
                chunk_size = self.model.concurrency_limit  # Adjust based on API limits
                results = []
                
                # Initialize progress bar
                pbar = tqdm(total=len(prompt_list), desc="Processing pairs", unit="pair")
                
                # Process chunks
                for i in range(0, len(prompt_list), chunk_size):
                    chunk = prompt_list[i:i + chunk_size]
                    
                    # Process chunk concurrently
                    chunk_results = await self.model.batch_compare_pairs_async(
                        chunk,
                        self.n_trial,
                        quiet=True
                    )
                    
                    results.extend(chunk_results)
                    pbar.update(len(chunk))
                
                pbar.close()
                return results
                
            model_results = asyncio.run(process_async())
        else:
            model_results = self.model.batch_compare_pairs(
                prompt_list, self.n_trial
            )
            
        pairs_data = self._process_model_responses(pairs_data, model_results)
        preference_counts = self._extract_preference_counts(pairs_data)
        
        if method == "bradley-terry":
            utilities, log_loss, accuracy = self._fit_bradley_terry(
                preference_counts,
                num_epochs=num_epochs,
                learning_rate=learning_rate,
                use_soft_labels=use_soft_labels
            )
        else:
            utilities, log_loss, accuracy = self._fit_thurstonian(
                preference_counts,
                num_epochs=num_epochs,
                learning_rate=learning_rate,
                use_soft_labels=use_soft_labels
            )
            
        # Format results based on method
        if method == "bradley-terry":
            # Each utility should be a float
            rankings = [
                (self.items[self.option_id_to_idx[idx]], float(util))  # Ensure float
                for idx, util in sorted(utilities.items(), key=lambda x: x[1], reverse=True)
            ]
            
            # Store raw utilities for later use
            results = {
                'utilities': {k: float(v) for k, v in utilities.items()},
                'rankings': rankings,
                'accuracy': accuracy,
                'log_loss': log_loss,
                'raw_data': pairs_data
            }
        else:
            # Thurstonian format
            rankings = [
                (self.items[self.option_id_to_idx[idx]], stats)
                for idx, stats in sorted(utilities.items(), key=lambda x: x[1]['mean'], reverse=True)
            ]
            
            results = {
                'utilities': utilities,
                'rankings': rankings,
                'accuracy': accuracy,
                'log_loss': log_loss,
                'raw_data': pairs_data
            }
            
        if self.save_directory:
            self._save_results(results, method)
            
        return results

    def _save_results(self, results: Dict[str, Any], method: str):
        """Save analysis results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(f"{self.save_directory}/{timestamp}", exist_ok=True)
        
        # Save JSON results
        results_data = {
            'metadata': {
                'timestamp': timestamp,
                'method': method,
                'n_items': len(self.items),
                'n_trial': self.n_trial,
                'n_pairs': self.n_pairs,
                'seed': self.seed
            },
            'results': convert_numpy(results)  # Convert numpy types for JSON serialization
        }
        
        filename = "utility_analysis_results.json"
        save_path = os.path.join(f"{self.save_directory}/{timestamp}", filename)
        
        with open(save_path, 'w') as f:
            json.dump(results_data, f, indent=2)
            
        # Save human-readable summary with metric explanations
        summary_filename = "utility_analysis_summary.txt"
        summary_path = os.path.join(f"{self.save_directory}/{timestamp}", summary_filename)
        
        with open(summary_path, 'w') as f:
            f.write(f"Method: {method}\n\n")
            f.write("Performance Metrics:\n")
            f.write("-----------------\n")
            f.write(f"Accuracy: {results['accuracy']:.4f}\n")
            f.write("- Fraction of correctly predicted preferences\n")
            f.write("- Higher is better (range: 0-1)\n")
            f.write("- For each pair (A,B), checks if model predicts the majority preference\n\n")
            
            f.write(f"Log Loss: {results['log_loss']:.4f}\n")
            f.write("- Measures prediction confidence and accuracy\n")
            f.write("- Lower is better (range: 0-∞)\n")
            f.write("- Calculated as: -mean(y*log(p) + (1-y)*log(1-p))\n")
            f.write("  where y is true preference and p is predicted probability\n\n")
            
            f.write("Rankings:\n")
            f.write("-----------------\n")
            for item, stats in results['rankings']:
                if method == "bradley-terry":
                    f.write(f"{item}: {stats:.4f}\n")
                else:
                    mean = stats['mean']
                    std = np.sqrt(stats['variance'])
                    f.write(f"{item}: {mean:.4f} ± {std:.4f}\n")
                    
        print(f"\nResults saved to {save_path}")
        print(f"Summary saved to {summary_path}")