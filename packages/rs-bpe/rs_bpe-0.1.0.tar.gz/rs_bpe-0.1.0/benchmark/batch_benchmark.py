"""
Batch processing benchmark script for tokenizer libraries.

Key Components:
    BatchBenchmarkRunner: Manages and executes batch processing benchmarks for different tokenizers
    TokenizerBatchAdapter: Interface for tokenizers with batch processing capabilities
    run_batch_benchmarks(): Main function to execute benchmarks and display results

Project Dependencies:
    This file uses: rs_bpe, tiktoken: For tokenization comparison
    This file uses: matplotlib, pandas: For results visualization and analysis
"""

import gc
import random
import statistics
import sys
import time
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Try to import rs_bpe, handle if not built
try:
    import rs_bpe
    RS_BPE_AVAILABLE = True
except ImportError:
    print("Warning: rs_bpe module not properly built.")
    print("Run 'maturin develop' to build the module before benchmarking.")
    RS_BPE_AVAILABLE = False

# Try to import tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    print("Warning: tiktoken not available.")
    TIKTOKEN_AVAILABLE = False


def generate_test_data(num_texts: int = 1000, text_length_range: "tuple[int, int]" = (50, 500)) -> "list[str]":
    """
    Generate random test data for benchmarking.
    
    Parameters
    ----------
    num_texts (int): Number of texts to generate
    text_length_range (Tuple[int, int]): Min and max length of each text
    
    Returns
    -------
    List[str]: List of randomly generated texts
    
    Execution Flow:
    1. The function generates a list of common words and punctuation
    2. It creates random texts of varying lengths
    3. It returns the list of generated texts

    """
    words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "I",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
        "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
        "Python", "Rust", "encoding", "tokenization", "performance", "optimization",
        "batch", "processing", "algorithm", "implementation", "benchmark", "test"
    ]
    
    punctuation = [",", ".", "!", "?", ";", ":", "-", "(", ")", '"', "'"]
    
    result = []
    for _ in range(num_texts):
        length = random.randint(*text_length_range)
        text = []
        
        while len(" ".join(text)) < length:
            # Add word
            text.append(random.choice(words))
            
            # Maybe add punctuation (20% chance)
            if random.random() < 0.2:
                text.append(random.choice(punctuation))
                
            # Maybe add newline (5% chance)
            if random.random() < 0.05:
                text.append("\n")
        
        result.append(" ".join(text))
    
    return result


class TokenizerBatchAdapter(ABC):
    """
    Abstract adapter class for tokenizers with batch processing capabilities.
    
    Parameters
    ----------
    name (str): Name of the tokenizer implementation
    
    Attributes
    ----------
    name (str): Name of the tokenizer implementation

    """
    
    def __init__(self, name: str):
        """
        Initialize the TokenizerBatchAdapter.
        
        Parameters
        ----------
        name (str): Name of the tokenizer implementation
        
        Execution Flow:
        1. The function stores the provided name

        """
        self.name = name
    
    @abstractmethod
    def encode_batch(self, texts: "list[str]") -> "tuple[list[list[int]], float]":
        """
        Encode a batch of texts into token IDs.
        
        Parameters
        ----------
        texts (List[str]): List of texts to encode
        
        Returns
        -------
        Tuple[List[List[int]], float]: The list of token ID lists and time taken

        """
    
    @abstractmethod
    def decode_batch(self, token_batches: "list[list[int]]") -> "tuple[list[str], float]":
        """
        Decode batches of token IDs back to text.
        
        Parameters
        ----------
        token_batches (List[List[int]]): List of token ID lists to decode
        
        Returns
        -------
        Tuple[List[str], float]: The decoded texts and time taken

        """


class TiktokenBatchAdapter(TokenizerBatchAdapter):
    """
    Adapter for tiktoken with batch processing.
    
    Parameters
    ----------
    None
    
    Attributes
    ----------
    tokenizer: The tiktoken tokenizer instance

    """
    
    def __init__(self):
        """
        Initialize the tiktoken batch adapter.
        
        Execution Flow:
        1. The function initializes the parent class with the tokenizer name
        2. It loads the cl100k_base tokenizer from tiktoken
        """
        super().__init__("tiktoken")
        if not TIKTOKEN_AVAILABLE:
            raise ImportError("tiktoken not available")
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def encode_batch(self, texts: "list[str]") -> "tuple[list[list[int]], float]":
        """
        Encode a batch of texts using tiktoken.
        
        Parameters
        ----------
        texts (List[str]): List of texts to encode
        
        Returns
        -------
        Tuple[List[List[int]], float]: The list of token ID lists and time taken
        
        Execution Flow:
        1. The function measures the start time
        2. It encodes each text in the batch
        3. It measures the end time
        4. It returns the results and time taken

        """
        start_time = time.time()
        
        results = []
        for text in texts:
            tokens = self.tokenizer.encode(text)
            results.append(tokens)
        
        end_time = time.time()
        return results, end_time - start_time
    
    def decode_batch(self, token_batches: "list[list[int]]") -> "tuple[list[str], float]":
        """
        Decode batches of token IDs using tiktoken.
        
        Parameters
        ----------
        token_batches (List[List[int]]): List of token ID lists to decode
        
        Returns
        -------
        Tuple[List[str], float]: The decoded texts and time taken
        
        Execution Flow:
        1. The function measures the start time
        2. It decodes each batch of tokens
        3. It measures the end time
        4. It returns the results and time taken

        """
        start_time = time.time()
        
        results = []
        for tokens in token_batches:
            text = self.tokenizer.decode(tokens)
            results.append(text)
        
        end_time = time.time()
        return results, end_time - start_time


class RsBpeStandardBatchAdapter(TokenizerBatchAdapter):
    """
    Adapter for rs_bpe with standard batch processing.
    
    Parameters
    ----------
    None
    
    Attributes
    ----------
    tokenizer: The rs_bpe tokenizer instance

    """
    
    def __init__(self):
        """
        Initialize the rs_bpe standard batch adapter.
        
        Execution Flow:
        1. The function initializes the parent class with the tokenizer name
        2. It loads the cl100k_base tokenizer from rs_bpe
        """
        super().__init__("rs_bpe_standard_batch")
        if not RS_BPE_AVAILABLE:
            raise ImportError("rs_bpe not available")
        self.tokenizer = rs_bpe.bpe.openai.cl100k_base()
    
    def encode_batch(self, texts: "list[str]") -> "tuple[list[list[int]], float]":
        """
        Encode a batch of texts using rs_bpe standard batch processing.
        
        Parameters
        ----------
        texts (List[str]): List of texts to encode
        
        Returns
        -------
        Tuple[List[List[int]], float]: The list of token ID lists and time taken
        
        Execution Flow:
        1. The function passes the texts to the tokenizer's encode_batch method
        2. It extracts and returns the results and time taken

        """
        tokens, _, time_taken = self.tokenizer.encode_batch(texts)  # type: ignore
        return tokens, time_taken
    
    def decode_batch(self, token_batches: "list[list[int]]") -> "tuple[list[str], float]":
        """
        Decode batches of token IDs using rs_bpe standard batch processing.
        
        Parameters
        ----------
        token_batches (List[List[int]]): List of token ID lists to decode
        
        Returns
        -------
        Tuple[List[str], float]: The decoded texts and time taken
        
        Execution Flow:
        1. The function measures the start time
        2. It passes the token batches to the tokenizer's decode_batch method
        3. It measures the end time
        4. It returns the results and time taken

        """
        start_time = time.time()
        results = self.tokenizer.decode_batch(token_batches)  # type: ignore
        end_time = time.time()
        
        # Convert Optional[str] to str, replacing None with empty string
        results = [text if text is not None else "" for text in results]
        
        return results, end_time - start_time


class BatchBenchmarkRunner:
    """
    Runs batch processing benchmarks for different tokenizer implementations.
    
    Parameters
    ----------
    tokenizers (List[TokenizerBatchAdapter]): List of tokenizer adapters to benchmark
    num_runs (int): Number of benchmark runs per operation
    
    Attributes
    ----------
    tokenizers (List[TokenizerBatchAdapter]): List of tokenizer adapters
    num_runs (int): Number of benchmark runs per operation
    results (Dict): Results of the benchmark runs

    """
    
    def __init__(self, tokenizers: "list[TokenizerBatchAdapter]", num_runs: int = 3):
        """
        Initialize the batch benchmark runner.
        
        Parameters
        ----------
        tokenizers (List[TokenizerBatchAdapter]): List of tokenizer adapters to benchmark
        num_runs (int): Number of benchmark runs per operation
        
        Execution Flow:
        1. The function stores the tokenizers and number of runs
        2. It initializes an empty results dictionary

        """
        self.tokenizers = tokenizers
        self.num_runs = num_runs
        self.results = {
            "encode_batch": {},
            "decode_batch": {},
            "roundtrip_batch": {},
            "token_count": {}
        }
    
    def benchmark_encode_batch(self, batch_size: int, test_data: "list[str]") -> None:
        """
        Benchmark the encode_batch method for all tokenizers.
        
        Parameters
        ----------
        batch_size (int): Size of batch to test
        test_data (List[str]): Test data to use
        
        Execution Flow:
        1. The function takes a subset of test data based on batch size
        2. For each tokenizer, it times the encode_batch method multiple times
        3. It calculates and stores the average encoding time and tokens per second

        """
        texts = test_data[:batch_size]
        
        for tokenizer in self.tokenizers:
            times = []
            token_counts = []
            
            for _ in range(self.num_runs):
                # Force garbage collection before timing
                gc.collect()
                
                # Run batch encoding
                tokens, execution_time = tokenizer.encode_batch(texts)
                times.append(execution_time)
                
                # Count tokens
                total_tokens = sum(len(t) for t in tokens)
                token_counts.append(total_tokens)
            
            # Store average time and token count
            avg_time = statistics.mean(times)
            avg_token_count = statistics.mean(token_counts)
            tokens_per_second = avg_token_count / avg_time if avg_time > 0 else 0
            
            if batch_size not in self.results["encode_batch"]:
                self.results["encode_batch"][batch_size] = {}
            self.results["encode_batch"][batch_size][tokenizer.name] = {
                "time": avg_time,
                "tokens_per_second": tokens_per_second
            }
            
            # Store token count
            if batch_size not in self.results["token_count"]:
                self.results["token_count"][batch_size] = {}
            self.results["token_count"][batch_size][tokenizer.name] = avg_token_count
    
    def benchmark_decode_batch(self, batch_size: int, test_data: "list[str]") -> None:
        """
        Benchmark the decode_batch method for all tokenizers.
        
        Parameters
        ----------
        batch_size (int): Size of batch to test
        test_data (List[str]): Test data to use
        
        Execution Flow:
        1. The function takes a subset of test data based on batch size
        2. For each tokenizer, it first encodes the texts to get tokens
        3. It then times the decode_batch method multiple times
        4. It calculates and stores the average decoding time and tokens per second

        """
        texts = test_data[:batch_size]
        
        for tokenizer in self.tokenizers:
            # Get token batches to decode
            tokens, _ = tokenizer.encode_batch(texts)
            times = []
            
            for _ in range(self.num_runs):
                # Force garbage collection before timing
                gc.collect()
                
                # Run batch decoding
                _, execution_time = tokenizer.decode_batch(tokens)
                times.append(execution_time)
            
            # Store average time and tokens per second
            avg_time = statistics.mean(times)
            token_count = sum(len(t) for t in tokens)
            tokens_per_second = token_count / avg_time if avg_time > 0 else 0
            
            if batch_size not in self.results["decode_batch"]:
                self.results["decode_batch"][batch_size] = {}
            self.results["decode_batch"][batch_size][tokenizer.name] = {
                "time": avg_time,
                "tokens_per_second": tokens_per_second
            }
    
    def benchmark_roundtrip_batch(self, batch_size: int, test_data: "list[str]") -> None:
        """
        Benchmark the full encode-decode batch roundtrip for all tokenizers.
        
        Parameters
        ----------
        batch_size (int): Size of batch to test
        test_data (List[str]): Test data to use
        
        Execution Flow:
        1. The function takes a subset of test data based on batch size
        2. For each tokenizer, it times the full encode-decode batch cycle
        3. It calculates and stores the average roundtrip time and tokens per second

        """
        texts = test_data[:batch_size]
        
        for tokenizer in self.tokenizers:
            times = []
            token_counts = []
            
            for _ in range(self.num_runs):
                # Force garbage collection before timing
                gc.collect()
                
                # Measure encode-decode roundtrip time
                start_time = time.time()
                tokens, _ = tokenizer.encode_batch(texts)
                _, _ = tokenizer.decode_batch(tokens)
                end_time = time.time()
                
                times.append(end_time - start_time)
                token_counts.append(sum(len(t) for t in tokens))
            
            # Store average time and tokens per second
            avg_time = statistics.mean(times)
            avg_token_count = statistics.mean(token_counts)
            tokens_per_second = avg_token_count / avg_time if avg_time > 0 else 0
            
            if batch_size not in self.results["roundtrip_batch"]:
                self.results["roundtrip_batch"][batch_size] = {}
            self.results["roundtrip_batch"][batch_size][tokenizer.name] = {
                "time": avg_time,
                "tokens_per_second": tokens_per_second
            }
    
    def run_benchmarks(self, batch_sizes: "list[int]") -> "dict":
        """
        Run all benchmarks for all batch sizes.
        
        Parameters
        ----------
        batch_sizes (List[int]): List of batch sizes to test
        
        Returns
        -------
        Dict: Dictionary containing benchmark results
        
        Execution Flow:
        1. The function generates test data
        2. It iterates through all batch sizes
        3. For each size, it runs all benchmark types
        4. It returns the complete results dictionary

        """
        # Generate test data
        print("Generating test data...")
        test_data = generate_test_data(num_texts=max(batch_sizes) + 10)
        
        for batch_size in batch_sizes:
            print(f"Benchmarking with batch size {batch_size}...")
            self.benchmark_encode_batch(batch_size, test_data)
            self.benchmark_decode_batch(batch_size, test_data)
            self.benchmark_roundtrip_batch(batch_size, test_data)
        
        return self.results
    
    def print_results(self) -> None:
        """
        Print benchmark results in a readable format.
        
        Execution Flow:
        1. The function formats and prints the results for each benchmark type
        2. For each batch size, it shows the times for all tokenizers
        """
        print("\n===== BATCH BENCHMARK RESULTS =====")
        
        # Print encoding results
        print("\nENCODING BATCH TIMES (seconds):")
        for batch_size, tokenizer_results in sorted(self.results["encode_batch"].items()):
            print(f"\nBATCH SIZE {batch_size}:")
            for tokenizer_name, metrics in tokenizer_results.items():
                print(f"  {tokenizer_name}: {metrics['time']:.6f}s, {metrics['tokens_per_second']:.2f} tokens/sec")
        
        # Print decoding results
        print("\nDECODING BATCH TIMES (seconds):")
        for batch_size, tokenizer_results in sorted(self.results["decode_batch"].items()):
            print(f"\nBATCH SIZE {batch_size}:")
            for tokenizer_name, metrics in tokenizer_results.items():
                print(f"  {tokenizer_name}: {metrics['time']:.6f}s, {metrics['tokens_per_second']:.2f} tokens/sec")
        
        # Print roundtrip results
        print("\nROUNDTRIP BATCH TIMES (seconds):")
        for batch_size, tokenizer_results in sorted(self.results["roundtrip_batch"].items()):
            print(f"\nBATCH SIZE {batch_size}:")
            for tokenizer_name, metrics in tokenizer_results.items():
                print(f"  {tokenizer_name}: {metrics['time']:.6f}s, {metrics['tokens_per_second']:.2f} tokens/sec")
    
    def plot_results(self, save_path: "str | None" = None) -> None:
        """
        Generate and display plots of benchmark results.
        
        Parameters
        ----------
        save_path (Optional[str]): Path to save the plots, if provided
        
        Execution Flow:
        1. The function creates figures for timing and throughput plots
        2. It creates line plots for each metric across batch sizes
        3. It displays and optionally saves the plots

        """
        # Get batch sizes and tokenizer names
        batch_sizes = sorted(self.results["encode_batch"].keys())
        tokenizer_names = [t.name for t in self.tokenizers]
        
        # Format batch sizes to include total token estimate
        readable_sizes = [f"{size}\n(~{self._format_token_count(size)})" for size in batch_sizes]
        
        # Create figures with better sizing and titles
        fig1, axs1 = plt.subplots(3, 1, figsize=(12, 15))
        fig1.suptitle('Batch Processing Time Comparison', fontsize=16, fontweight='bold')
        
        fig2, axs2 = plt.subplots(3, 1, figsize=(12, 15))
        fig2.suptitle('Batch Processing Throughput Comparison', fontsize=16, fontweight='bold')
        
        # Add operation titles
        operation_titles = {
            "encode_batch": "Encoding",
            "decode_batch": "Decoding",
            "roundtrip_batch": "Roundtrip (Encode+Decode)"
        }
        
        # Define consistent colors for each tokenizer
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        markers = ['o', 's', 'd', '^', 'v']
        
        # Prepare data for plotting
        for i, operation in enumerate(["encode_batch", "decode_batch", "roundtrip_batch"]):
            # Time data
            time_data = {tokenizer_name: [] for tokenizer_name in tokenizer_names}
            
            # Throughput data (tokens per second)
            tps_data = {tokenizer_name: [] for tokenizer_name in tokenizer_names}
            
            for batch_size in batch_sizes:
                for tokenizer_name in tokenizer_names:
                    if batch_size in self.results[operation] and tokenizer_name in self.results[operation][batch_size]:
                        time_data[tokenizer_name].append(self.results[operation][batch_size][tokenizer_name]["time"])
                        tps_data[tokenizer_name].append(self.results[operation][batch_size][tokenizer_name]["tokens_per_second"])
            
            # Plot time data
            for j, tokenizer_name in enumerate(tokenizer_names):
                color = colors[j % len(colors)]
                marker = markers[j % len(markers)]
                
                axs1[i].plot(
                    batch_sizes,
                    time_data[tokenizer_name],
                    marker=marker,
                    label=tokenizer_name,
                    color=color,
                    linewidth=2,
                    markersize=8
                )
                
                # Add data point labels for time values
                for k, time_val in enumerate(time_data[tokenizer_name]):
                    axs1[i].annotate(
                        f'{time_val:.5f}s',
                        xy=(batch_sizes[k], time_val),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=8,
                        alpha=0.8
                    )
            
            axs1[i].set_title(f"{operation_titles[operation]} Time (LOWER IS BETTER)", fontsize=14)
            axs1[i].set_xlabel("Batch Size (samples)")
            axs1[i].set_ylabel("Time (seconds)")
            axs1[i].set_xscale('log')  # Log scale makes it easier to see differences
            axs1[i].grid(axis="both", linestyle="--", alpha=0.7)
            axs1[i].legend(loc='upper left', fancybox=True, shadow=True)
            
            # Find and highlight the winner for each batch size
            for k, batch_size in enumerate(batch_sizes):
                batch_times = [time_data[name][k] for name in tokenizer_names if k < len(time_data[name])]
                if batch_times:
                    min_time_idx = batch_times.index(min(batch_times))
                    min_time = batch_times[min_time_idx]
                    win_tokenizer = tokenizer_names[min_time_idx]
                    
                    axs1[i].plot(
                        batch_size,
                        min_time,
                        'o',
                        markersize=12,
                        markerfacecolor='none',
                        markeredgecolor='green',
                        markeredgewidth=2
                    )
            
            # Plot throughput data
            for j, tokenizer_name in enumerate(tokenizer_names):
                color = colors[j % len(colors)]
                marker = markers[j % len(markers)]
                
                axs2[i].plot(
                    batch_sizes,
                    tps_data[tokenizer_name],
                    marker=marker,
                    label=tokenizer_name,
                    color=color,
                    linewidth=2,
                    markersize=8
                )
                
                # Add data point labels for throughput values
                for k, tps_val in enumerate(tps_data[tokenizer_name]):
                    axs2[i].annotate(
                        f'{int(tps_val):,}',
                        xy=(batch_sizes[k], tps_val),
                        xytext=(5, 5),
                        textcoords="offset points",
                        fontsize=8,
                        alpha=0.8
                    )
            
            axs2[i].set_title(f"{operation_titles[operation]} Throughput (HIGHER IS BETTER)", fontsize=14)
            axs2[i].set_xlabel("Batch Size (samples)")
            axs2[i].set_ylabel("Tokens per Second")
            axs2[i].set_xscale('log')  # Log scale makes more sense for batch sizes
            axs2[i].grid(axis="both", linestyle="--", alpha=0.7)
            axs2[i].legend(loc='upper left', fancybox=True, shadow=True)
            
            # Format y-axis with commas for thousands
            axs2[i].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
            
            # Find and highlight the winner for each batch size
            for k, batch_size in enumerate(batch_sizes):
                batch_tps = [tps_data[name][k] for name in tokenizer_names if k < len(tps_data[name])]
                if batch_tps:
                    max_tps_idx = batch_tps.index(max(batch_tps))
                    max_tps = batch_tps[max_tps_idx]
                    win_tokenizer = tokenizer_names[max_tps_idx]
                    
                    axs2[i].plot(
                        batch_size,
                        max_tps,
                        'o',
                        markersize=12,
                        markerfacecolor='none',
                        markeredgecolor='green',
                        markeredgewidth=2
                    )
                    
                    # Add 'BEST' label to the winner
                    axs2[i].annotate(
                        'BEST',
                        xy=(batch_size, max_tps),
                        xytext=(0, 10),
                        textcoords="offset points",
                        fontsize=8,
                        color='green',
                        weight='bold',
                        ha='center'
                    )
        
        # Create a speedup comparison chart
        speedup_fig, _speedup_ax = plt.subplots(figsize=(14, 8))
        speedup_fig.suptitle('Performance Speedup by Batch Size', fontsize=16, fontweight='bold')
        
        # Calculate and plot speedup ratios
        reference_tokenizer = "tiktoken" if "tiktoken" in tokenizer_names else tokenizer_names[0]
        speedup_data = {}
        
        bar_width = 0.25
        bar_positions = {}
        
        for i, operation in enumerate(["encode_batch", "decode_batch", "roundtrip_batch"]):
            bar_positions[operation] = np.arange(len(batch_sizes)) + (i - 1) * bar_width
        
        for _j, tokenizer_name in enumerate(tokenizer_names):
            if tokenizer_name == reference_tokenizer:
                continue
                
            speedup_data[tokenizer_name] = {}
            
            for operation in ["encode_batch", "decode_batch", "roundtrip_batch"]:
                speedup_data[tokenizer_name][operation] = []
                
                for batch_size in batch_sizes:
                    if (batch_size in self.results[operation] and
                        tokenizer_name in self.results[operation][batch_size] and
                        reference_tokenizer in self.results[operation][batch_size]):
                        
                        ref_time = self.results[operation][batch_size][reference_tokenizer]["time"]
                        tokenizer_time = self.results[operation][batch_size][tokenizer_name]["time"]
                        speedup = ref_time / tokenizer_time if tokenizer_time > 0 else 0
                        speedup_data[tokenizer_name][operation].append(speedup)
                    else:
                        speedup_data[tokenizer_name][operation].append(0)
        
        # Create separate subplots for each operation's speedup
        speedup_fig, speedup_axs = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
        speedup_fig.suptitle(f'Performance Speedup Relative to {reference_tokenizer} (Higher is Better)',
                            fontsize=16, fontweight='bold')
        
        for i, (operation, title) in enumerate(operation_titles.items()):
            ax = speedup_axs[i]
            
            x = np.arange(len(batch_sizes))
            width = 0.8 / (len(tokenizer_names) - 1) if len(tokenizer_names) > 1 else 0.4
            
            for j, tokenizer_name in enumerate(tokenizer_names):
                if tokenizer_name == reference_tokenizer:
                    continue
                
                # Use consistent color for each tokenizer
                color = colors[(j) % len(colors)]
                
                # Calculate the offset for this tokenizer's bars
                offsets = [(k - (len(tokenizer_names) - 1) / 2 + 0.5) * width
                        for k in range(len(tokenizer_names) - 1)]
                offset_idx = [token for token in tokenizer_names if token != reference_tokenizer].index(tokenizer_name)
                offset = offsets[offset_idx]
                
                # Plot the bars
                bars = ax.bar(x + offset, speedup_data[tokenizer_name][operation],
                            width, label=tokenizer_name, color=color)
                
                # Add value labels on top of bars
                for _bar_idx, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:
                        ax.annotate(f'{height:.2f}x',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom',
                                fontsize=8)
            
            # Set chart properties
            ax.set_title(f"{title}", fontsize=14)
            ax.set_xlabel("Batch Size")
            ax.set_xticks(x)
            ax.set_xticklabels(readable_sizes)
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            
            # Add a reference line at 1.0
            ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.6)
            
            # Only show legend on the first subplot to avoid duplication
            if i == 0:
                ax.legend(loc='upper left', fancybox=True, shadow=True)
        
        # Set common y-axis label
        speedup_fig.text(0.04, 0.5, 'Speedup Ratio (x times faster)',
                        va='center', rotation='vertical', fontsize=12)
        
        # Adjust layout
        fig1.tight_layout(rect=(0, 0.03, 1, 0.95))
        fig2.tight_layout(rect=(0, 0.03, 1, 0.95))
        speedup_fig.tight_layout(rect=(0, 0.03, 1, 0.95))
        
        # Save plots if requested
        if save_path:
            fig1.savefig(f"{save_path}_time.svg", dpi=300, format='svg', bbox_inches='tight')
            fig2.savefig(f"{save_path}_throughput.svg", dpi=300, format='svg', bbox_inches='tight')
            speedup_fig.savefig(f"{save_path}_speedup_by_batch.svg", dpi=300, format='svg', bbox_inches='tight')
        
        # Show plots
        plt.show()
    
    def _format_token_count(self, batch_size: int) -> str:
        """Format total token estimate for batch sizes."""
        # Get the average tokens per text from the results
        avg_tokens = 0
        tokenizer_count = 0
        
        for tokenizer_name in self.results["token_count"][batch_size]:
            avg_tokens += self.results["token_count"][batch_size][tokenizer_name]
            tokenizer_count += 1
        
        if tokenizer_count > 0:
            avg_tokens = avg_tokens / tokenizer_count
        
        # Format appropriately
        if avg_tokens < 1000:
            return f"{int(avg_tokens)} tokens"
        else:
            return f"{avg_tokens / 1000:.1f}K tokens"


def calculate_speedup(results: dict, operation: str, reference_tokenizer: str = "tiktoken") -> dict:
    """
    Calculate speedup ratios relative to a reference tokenizer.
    
    Parameters
    ----------
    results (Dict): Benchmark results dictionary
    operation (str): Operation type ("encode_batch", "decode_batch", "roundtrip_batch")
    reference_tokenizer (str): Name of the reference tokenizer for comparison
    
    Returns
    -------
    Dict: Dictionary with batch sizes and tokenizers, containing speedup ratios
    
    Execution Flow:
    1. The function iterates through the results for the specified operation
    2. For each batch size and tokenizer, it calculates the speedup ratio
    3. It returns a dictionary with the calculated ratios

    """
    speedups = {}
    
    for batch_size, tokenizer_results in results[operation].items():
        if reference_tokenizer in tokenizer_results:
            reference_time = tokenizer_results[reference_tokenizer]["time"]
            
            if batch_size not in speedups:
                speedups[batch_size] = {}
            
            for tokenizer_name, metrics in tokenizer_results.items():
                # Calculate speedup ratio (HIGHER IS BETTER)
                ratio = reference_time / metrics["time"] if metrics["time"] > 0 else float('inf')
                speedups[batch_size][tokenizer_name] = ratio
    
    return speedups


def print_speedup_summary(all_speedups: "dict[str, dict]") -> None:
    """
    Print a summary of speedup results.
    
    Parameters
    ----------
    all_speedups (Dict[str, Dict]): Dictionary with operations and their speedup results
    
    Execution Flow:
    1. The function formats and prints speedup results for each operation
    2. For each batch size, it shows the speedup ratio for all tokenizers

    """
    print("\n===== SPEEDUP SUMMARY =====")
    print("(Higher values indicate faster performance relative to reference tokenizer)")
    
    for operation, speedups in all_speedups.items():
        print(f"\n{operation.replace('_', ' ').upper()} SPEEDUP:")
        
        for batch_size, tokenizer_ratios in sorted(speedups.items()):
            print(f"\nBATCH SIZE {batch_size}:")
            for tokenizer_name, ratio in tokenizer_ratios.items():
                print(f"  {tokenizer_name}: {ratio:.2f}x")


def run_batch_benchmarks() -> None:
    """
    Main function to run all batch benchmarks and display results.
    
    Execution Flow:
    1. The function creates tokenizer adapters
    2. It initializes and runs the batch benchmark runner
    3. It prints and plots the benchmark results
    4. It calculates and prints speedup ratios
    """
    print("Initializing tokenizers...")
    tokenizers = []
    
    # Add tiktoken adapter if available
    if TIKTOKEN_AVAILABLE:
        try:
            tokenizers.append(TiktokenBatchAdapter())
        except ImportError:
            print("Warning: Failed to initialize tiktoken adapter.")
    
    # Add rs_bpe adapters if available
    if RS_BPE_AVAILABLE:
        try:
            # Add standard batch adapter
            tokenizers.append(RsBpeStandardBatchAdapter())

        except ImportError:
            print("Warning: Failed to initialize rs_bpe adapters.")
    
    if not tokenizers:
        print("Error: No tokenizers available for benchmarking.")
        sys.exit(1)
    
    # Define batch sizes to test
    batch_sizes = [1, 10, 100, 1000]
    
    print("Running batch benchmarks...")
    runner = BatchBenchmarkRunner(tokenizers, num_runs=3)
    results = runner.run_benchmarks(batch_sizes)
    
    # Print raw benchmark results
    runner.print_results()
    
    # Calculate speedup ratios for all operations
    reference_tokenizer = "tiktoken" if TIKTOKEN_AVAILABLE else tokenizers[0].name
    all_speedups = {}
    for operation in ["encode_batch", "decode_batch", "roundtrip_batch"]:
        all_speedups[operation] = calculate_speedup(results, operation, reference_tokenizer)
    
    # Print speedup summary
    print_speedup_summary(all_speedups)
    
    # Generate and display plots
    print("\nGenerating performance plots...")
    runner.plot_results(save_path="batch_benchmark_results")
    
    print("\nBatch benchmark completed!")


if __name__ == "__main__":
    run_batch_benchmarks()
