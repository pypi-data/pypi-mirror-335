"""
Benchmark script for comparing rs_bpe against tiktoken and tokenizers libraries.

Key Components:
    BenchmarkRunner: Manages and executes benchmarking for different tokenizers
    TokenizerAdapter: Abstract class for providing a unified interface to different tokenizers
    run_benchmarks(): Main function to execute benchmarks and display results

Project Dependencies:
    This file uses: rs_bpe, tiktoken, tokenizers: For tokenization comparison
    This file uses: matplotlib, pandas: For results visualization and analysis
"""

import gc
import statistics
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
import tiktoken
from matplotlib.ticker import FuncFormatter
from tokenizers import Tokenizer as HFTokenizer

# Try to import rs_bpe, handle if not built
try:
    import rs_bpe
    RS_BPE_AVAILABLE = True
except ImportError:
    print("Warning: rs_bpe module not properly built.")
    print("Run 'maturin develop' to build the module before benchmarking.")
    RS_BPE_AVAILABLE = False

# Test data sizes
SMALL_TEXT = "This is a small test string for tokenization."
try:
    with open("README.md", "r") as f:
        MEDIUM_TEXT = f.read()
except FileNotFoundError:
    MEDIUM_TEXT = SMALL_TEXT * 20  # Fallback if README.md doesn't exist

LARGE_TEXT = MEDIUM_TEXT * 50  # Approximately 200KB

# Create test texts of different sizes
TEST_TEXTS = {
    "small": SMALL_TEXT,
    "medium": MEDIUM_TEXT,
    "large": LARGE_TEXT,
}


class TokenizerAdapter(ABC):
    """
    Abstract adapter class for tokenizers to provide a unified interface.
    """
    
    def __init__(self, name: str):
        """Initialize the TokenizerAdapter."""
        self.name = name
    
    @abstractmethod
    def encode(self, text: str) -> "list[int]":
        """Encode text into token IDs."""
    
    @abstractmethod
    def decode(self, tokens: "list[int]") -> str:
        """Decode token IDs back to text."""


class RsBpeAdapter(TokenizerAdapter):
    """Adapter for rs_bpe tokenizer (basic version)."""
    
    def __init__(self):
        """Initialize the rs_bpe tokenizer adapter."""
        super().__init__("rs_bpe_basic")
        if not RS_BPE_AVAILABLE:
            raise ImportError("rs_bpe module not available")
        
        # Initialize with cl100k_base model - explicitly recreate for each test
        self.tokenizer = rs_bpe.bpe.openai.cl100k_base()
    
    def encode(self, text: str) -> "list[int]":
        """Encode text using rs_bpe tokenizer."""
        return cast("list[int]", self.tokenizer.encode(text))
    
    def decode(self, tokens: "list[int]") -> str:
        """Decode token IDs using rs_bpe tokenizer."""
        result = self.tokenizer.decode(tokens)
        return result if result is not None else ""


class RsBpeCachedAdapter(TokenizerAdapter):
    """Adapter for cached rs_bpe tokenizer."""
    
    def __init__(self):
        """Initialize the cached rs_bpe tokenizer adapter."""
        super().__init__("rs_bpe_cached")
        if not RS_BPE_AVAILABLE:
            raise ImportError("rs_bpe module not available")
        
        # Check if the tokenizer is already cached
        is_cached = rs_bpe.bpe.openai.is_cached_cl100k()
        if is_cached:
            print("Using pre-cached tokenizer")
        
        # Use the cached global instance
        self.tokenizer = rs_bpe.bpe.openai.cl100k_base()
    
    def encode(self, text: str) -> "list[int]":
        """Encode text using cached rs_bpe tokenizer."""
        return cast("list[int]", self.tokenizer.encode(text))
    
    def decode(self, tokens: "list[int]") -> str:
        """Decode token IDs using cached rs_bpe tokenizer."""
        result = self.tokenizer.decode(tokens)
        return result if result is not None else ""


class TiktokenAdapter(TokenizerAdapter):
    """Adapter for tiktoken tokenizer."""
    
    def __init__(self):
        """Initialize the tiktoken tokenizer adapter."""
        super().__init__("tiktoken")
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def encode(self, text: str) -> "list[int]":
        """Encode text using tiktoken tokenizer."""
        return self.tokenizer.encode(text)
    
    def decode(self, tokens: "list[int]") -> str:
        """Decode token IDs using tiktoken tokenizer."""
        return self.tokenizer.decode(tokens)


class HFTokenizerAdapter(TokenizerAdapter):
    """Adapter for HuggingFace tokenizers library."""
    
    def __init__(self):
        """Initialize the HuggingFace tokenizer adapter."""
        super().__init__("tokenizers")
        # We'll use a simple BPE tokenizer for comparison
        self.tokenizer = HFTokenizer.from_pretrained("gpt2")
    
    def encode(self, text: str) -> "list[int]":
        """Encode text using HuggingFace tokenizer."""
        return self.tokenizer.encode(text).ids
    
    def decode(self, tokens: "list[int]") -> str:
        """Decode token IDs using HuggingFace tokenizer."""
        result = self.tokenizer.decode(tokens)
        return result if result is not None else ""


class BenchmarkRunner:
    """Runs benchmarks for different tokenizer implementations."""
    
    def __init__(self, tokenizers: "list[TokenizerAdapter]", num_runs: int = 5):
        """Initialize the benchmark runner."""
        self.tokenizers = tokenizers
        self.num_runs = num_runs
        self.results = {
            "encode": {},
            "decode": {},
            "roundtrip": {},
            "token_count": {}
        }
    
    def _time_function(self, func, *args) -> "tuple[float, Any]":
        """Time the execution of a function."""
        gc.collect()  # Force garbage collection before timing
        start_time = time.time()
        result = func(*args)
        end_time = time.time()
        return end_time - start_time, result
    
    def benchmark_encode(self, text_size: str) -> None:
        """Benchmark the encode method for all tokenizers."""
        text = TEST_TEXTS[text_size]
        
        for tokenizer in self.tokenizers:
            times = []
            tokens = None
            
            for _ in range(self.num_runs):
                execution_time, result = self._time_function(tokenizer.encode, text)
                times.append(execution_time)
                tokens = result
            
            # Store average time and token count
            avg_time = statistics.mean(times)
            if text_size not in self.results["encode"]:
                self.results["encode"][text_size] = {}
            self.results["encode"][text_size][tokenizer.name] = avg_time
            
            # Store token count for comparison
            if text_size not in self.results["token_count"]:
                self.results["token_count"][text_size] = {}
            if tokens is not None:
                self.results["token_count"][text_size][tokenizer.name] = len(tokens)
            else:
                self.results["token_count"][text_size][tokenizer.name] = 0
    
    def benchmark_decode(self, text_size: str) -> None:
        """Benchmark the decode method for all tokenizers."""
        text = TEST_TEXTS[text_size]
        
        for tokenizer in self.tokenizers:
            tokens = tokenizer.encode(text)
            times = []
            
            for _ in range(self.num_runs):
                execution_time, _ = self._time_function(tokenizer.decode, tokens)
                times.append(execution_time)
            
            # Store average time
            avg_time = statistics.mean(times)
            if text_size not in self.results["decode"]:
                self.results["decode"][text_size] = {}
            self.results["decode"][text_size][tokenizer.name] = avg_time
    
    def benchmark_roundtrip(self, text_size: str) -> None:
        """Benchmark the full encode-decode roundtrip for all tokenizers."""
        text = TEST_TEXTS[text_size]
        
        for tokenizer in self.tokenizers:
            times = []
            
            for _ in range(self.num_runs):
                start_time = time.time()
                tokens = tokenizer.encode(text)
                decoded_text = tokenizer.decode(tokens)
                end_time = time.time()
                times.append(end_time - start_time)
            
            # Store average time
            avg_time = statistics.mean(times)
            if text_size not in self.results["roundtrip"]:
                self.results["roundtrip"][text_size] = {}
            self.results["roundtrip"][text_size][tokenizer.name] = avg_time
    
    def run_benchmarks(self) -> dict:
        """Run all benchmarks for all text sizes."""
        for text_size in TEST_TEXTS.keys():
            print(f"Benchmarking with {text_size} text...")
            self.benchmark_encode(text_size)
            self.benchmark_decode(text_size)
            self.benchmark_roundtrip(text_size)
        
        return self.results
    
    def print_results(self) -> None:
        """Print benchmark results in a readable format."""
        print("\n===== BENCHMARK RESULTS =====")
        
        # Print encoding results
        print("\nENCODING TIMES (seconds):")
        for text_size, tokenizer_times in self.results["encode"].items():
            print(f"\n{text_size.upper()} TEXT:")
            for tokenizer_name, time_taken in tokenizer_times.items():
                print(f"  {tokenizer_name}: {time_taken:.6f}s")
        
        # Print decoding results
        print("\nDECODING TIMES (seconds):")
        for text_size, tokenizer_times in self.results["decode"].items():
            print(f"\n{text_size.upper()} TEXT:")
            for tokenizer_name, time_taken in tokenizer_times.items():
                print(f"  {tokenizer_name}: {time_taken:.6f}s")
        
        # Print roundtrip results
        print("\nROUNDTRIP TIMES (seconds):")
        for text_size, tokenizer_times in self.results["roundtrip"].items():
            print(f"\n{text_size.upper()} TEXT:")
            for tokenizer_name, time_taken in tokenizer_times.items():
                print(f"  {tokenizer_name}: {time_taken:.6f}s")
        
        # Print token counts
        print("\nTOKEN COUNTS:")
        for text_size, tokenizer_counts in self.results["token_count"].items():
            print(f"\n{text_size.upper()} TEXT:")
            for tokenizer_name, count in tokenizer_counts.items():
                print(f"  {tokenizer_name}: {count} tokens")
    
    def plot_results(self, save_path: "str | None" = None) -> None:
        """Generate and display plots of benchmark results."""
        # Create figures for time comparison
        fig, axs = plt.subplots(3, 1, figsize=(12, 15))
        fig.suptitle('Tokenizer Performance Comparison', fontsize=16, fontweight='bold')
        
        operations = ["encode", "decode", "roundtrip"]
        titles = ["Encoding Time (LOWER IS BETTER)",
                 "Decoding Time (LOWER IS BETTER)",
                 "Roundtrip Time (LOWER IS BETTER)"]
        
        # Get sorted sizes and tokenizer names
        sorted_sizes = sorted(TEST_TEXTS.keys(), key=lambda x: len(TEST_TEXTS[x]))
        tokenizer_names = [t.name for t in self.tokenizers]
        
        # Get actual byte sizes for x-axis labels
        byte_sizes = [len(TEST_TEXTS[size].encode('utf-8')) for size in sorted_sizes]
        readable_sizes = [f"{size}\n({self._format_byte_size(b)})" for size, b in zip(sorted_sizes, byte_sizes)]
        
        # Define markers and colors for each tokenizer
        markers = ['o', 's', 'd', '^', 'v', '<', '>', 'p', '*']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        
        # Create line graphs for each operation
        for i, (operation, title) in enumerate(zip(operations, titles)):
            ax = axs[i]
            
            # Set position for x-axis
            x = np.arange(len(sorted_sizes))
            
            # Prepare data and plot lines for each tokenizer
            max_time = 0
            min_time = float('inf')
            for j, tokenizer_name in enumerate(tokenizer_names):
                times = [self.results[operation][size][tokenizer_name] for size in sorted_sizes]
                max_time = max(max_time, max(times))
                min_time = min(min_time, min(t for t in times if t > 0))
                
                # Use modulo to cycle through markers and colors if there are more tokenizers than options
                marker = markers[j % len(markers)]
                color = colors[j % len(colors)]
                
                # Plot line with markers
                line = ax.plot(x, times, marker=marker, linestyle='-', linewidth=2,
                              markersize=8, label=tokenizer_name, color=color)
            
            # Set to log scale for better visibility of small values
            ax.set_yscale('log')
            
            # Find winner (fastest tokenizer) for each text size and mark with star
            for k, size in enumerate(sorted_sizes):
                times = [self.results[operation][size][tokenizer_name] for tokenizer_name in tokenizer_names]
                winner_idx = times.index(min(times))
                
                # Highlight winner with a star
                ax.annotate('★',
                           xy=(k, times[winner_idx]),
                           xytext=(0, -15),
                           textcoords="offset points",
                           ha='center', va='top',
                           fontsize=14, fontweight='bold',
                           color='green')
            
            # Set chart properties
            ax.set_title(title, fontsize=14)
            ax.set_ylabel("Time (seconds) - Log Scale")
            ax.set_xlabel("Input Size")
            ax.set_xticks(x)
            ax.set_xticklabels(readable_sizes)
            ax.grid(True, linestyle="--", alpha=0.7)
            
            # Add a legend with a shadow effect and place it at the upper right
            ax.legend(loc='upper left', fancybox=True, shadow=True)
        
        # Create a separate throughput chart (use linear scale for this one)
        fig2, axs2 = plt.subplots(1, 1, figsize=(12, 6))
        fig2.suptitle('Tokenization Speed (tokens/second)', fontsize=16, fontweight='bold')
        
        # Prepare throughput data (tokens per second)
        x = np.arange(len(sorted_sizes))
        
        # Plot line for each tokenizer's throughput
        for j, tokenizer_name in enumerate(tokenizer_names):
            tps_values = []
            for size in sorted_sizes:
                token_count = self.results["token_count"][size][tokenizer_name]
                encode_time = self.results["encode"][size][tokenizer_name]
                tps = token_count / encode_time if encode_time > 0 else 0
                tps_values.append(tps)
            
            # Use modulo to cycle through markers and colors
            marker = markers[j % len(markers)]
            color = colors[j % len(colors)]
            
            # Plot line with markers
            line = axs2.plot(x, tps_values, marker=marker, linestyle='-', linewidth=2,
                            markersize=8, label=tokenizer_name, color=color)
            
            # Add value labels at each data point with improved positioning
            for k, tps_val in enumerate(tps_values):
                # Offset each tokenizer's labels differently
                vert_offset = 10 + (j * 15)
                horiz_offset = j * 5
                
                axs2.annotate(f'{int(tps_val):,}',
                             xy=(k, tps_val),
                             xytext=(horiz_offset, vert_offset),
                             textcoords="offset points",
                             ha='center', va='bottom',
                             fontsize=8,
                             bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "gray", "alpha": 0.8})
        
        # Find winner (highest throughput) for each text size
        for k, size in enumerate(sorted_sizes):
            tps_values = []
            for tokenizer_name in tokenizer_names:
                token_count = self.results["token_count"][size][tokenizer_name]
                encode_time = self.results["encode"][size][tokenizer_name]
                tps = token_count / encode_time if encode_time > 0 else 0
                tps_values.append(tps)
            
            winner_idx = tps_values.index(max(tps_values))
            
            # Highlight winner with a star
            axs2.annotate('★',
                         xy=(k, tps_values[winner_idx]),
                         xytext=(0, -20),
                         textcoords="offset points",
                         ha='center', va='top',
                         fontsize=14, fontweight='bold',
                         color='green')
        
        # Set chart properties
        axs2.set_title("Encoding Speed (HIGHER IS BETTER)", fontsize=14)
        axs2.set_ylabel("Tokens per Second")
        axs2.set_xlabel("Input Size")
        axs2.set_xticks(x)
        axs2.set_xticklabels(readable_sizes)
        axs2.grid(True, linestyle="--", alpha=0.7)
        axs2.legend(loc='upper left', fancybox=True, shadow=True)
        axs2.set_ylim(bottom=0)

        # Format y-axis tick labels with comma separators
        axs2.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, loc: f"{int(x):,}")
        )
        
        # Create separate charts for each operation to show detail
        # This gives a clearer view for each operation
        detailed_fig, detailed_axs = plt.subplots(len(sorted_sizes), 3, figsize=(15, 12))
        detailed_fig.suptitle('Detailed Performance by Text Size', fontsize=16, fontweight='bold')
        
        # Set column titles
        for j, op in enumerate(operations):
            detailed_axs[0, j].set_title(f"{op.capitalize()}", fontsize=14)
        
        # Create bar charts for each text size and operation
        for i, size in enumerate(sorted_sizes):
            for j, operation in enumerate(operations):
                ax = detailed_axs[i, j]
                
                # Get data for this size and operation
                data = []
                for tokenizer_name in tokenizer_names:
                    data.append(self.results[operation][size][tokenizer_name])
                
                # Create bar chart
                bars = ax.bar(tokenizer_names, data, color=colors[:len(tokenizer_names)])
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    # Use consistent decimal format
                    value_str = f'{height:.6f}'
                    ax.annotate(value_str,
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom',
                               fontsize=8, rotation=45)
                
                # Highlight winner with a green bar
                winner_idx = data.index(min(data))
                bars[winner_idx].set_color('green')
                
                # Set chart properties
                ax.set_ylabel("Time (seconds)")
                ax.set_title(f"{size} ({self._format_byte_size(len(TEST_TEXTS[size].encode('utf-8')))})", fontsize=10)
                ax.tick_params(axis='x', rotation=45)
                
                # Adjust y-axis for better visibility
                max_val = max(data)
                ax.set_ylim(0, max_val * 1.2)
        
        # Add a legend explaining the bar chart
        detailed_fig.text(0.5, 0.01, "Green bar = Best performer for this operation and text size",
                         ha='center', fontsize=12, fontweight='bold')
        
        # Calculate and add speedup information as text
        baseline_tokenizer = self.tokenizers[0].name
        speedup_fig = plt.figure(figsize=(12, 6))
        speedup_ax = speedup_fig.add_subplot(111)
        speedup_fig.suptitle('Performance Increase vs. ' + baseline_tokenizer, fontsize=16, fontweight='bold')
        
        # Calculate speedups for each tokenizer
        speedup_data = []
        speedup_tokenizers = []
        for tokenizer_name in tokenizer_names:
            if tokenizer_name == baseline_tokenizer:
                continue
            
            speedup_tokenizers.append(tokenizer_name)
            operation_speedups = []
            for operation in operations:
                # Calculate average speedup across all sizes
                speedup = 0
                for size in sorted_sizes:
                    baseline_time = self.results[operation][size][baseline_tokenizer]
                    tokenizer_time = self.results[operation][size][tokenizer_name]
                    ratio = baseline_time / tokenizer_time if tokenizer_time > 0 else 0
                    speedup += ratio
                speedup /= len(sorted_sizes)
                operation_speedups.append(speedup)
            
            speedup_data.append(operation_speedups)
        
        # Plot bar chart for speedup comparison (keeping this as bar chart for clarity)
        x = np.arange(len(operations))
        width = 0.8 / len(speedup_tokenizers) if speedup_tokenizers else 0.8
        offsets = [(j - len(speedup_tokenizers) / 2 + 0.5) * width for j in range(len(speedup_tokenizers))]
        
        for j, (tokenizer_name, speedups, offset) in enumerate(zip(speedup_tokenizers, speedup_data, offsets)):  # noqa: B007
            bars = speedup_ax.bar(x + offset, speedups, width, label=tokenizer_name)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                speedup_ax.annotate(f'{height:.2f}x',
                                  xy=(bar.get_x() + bar.get_width() / 2, height),
                                  xytext=(0, 3),
                                  textcoords="offset points",
                                  ha='center', va='bottom',
                                  fontsize=9)
        
        # Set chart properties
        speedup_ax.set_title("Average Speedup Ratio (HIGHER IS BETTER)", fontsize=14)
        speedup_ax.set_ylabel("Speedup Ratio")
        speedup_ax.set_xlabel("Operation")
        speedup_ax.set_xticks(x)
        speedup_ax.set_xticklabels([op.capitalize() for op in operations])
        speedup_ax.grid(axis="y", linestyle="--", alpha=0.7)
        speedup_ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)  # Reference line
        speedup_ax.set_ylim(bottom=0)
        speedup_ax.legend(loc='upper right', fancybox=True, shadow=True)
        
        # Adjust layout for all figures
        for fig_item in [fig, fig2, detailed_fig, speedup_fig]:
            fig_item.tight_layout(rect=(0, 0.03, 1, 0.95))
        
        # Save plots if requested
        if save_path:
            fig.savefig(f"{save_path}_time.svg", dpi=300, format='svg', bbox_inches='tight')
            fig2.savefig(f"{save_path}_throughput.svg", dpi=300, format='svg', bbox_inches='tight')
            detailed_fig.savefig(f"{save_path}_detailed.svg", dpi=300, format='svg', bbox_inches='tight')
            speedup_fig.savefig(f"{save_path}_speedup.svg", dpi=300, format='svg', bbox_inches='tight')
        
        # Show plots
        plt.show()
    
    def _format_byte_size(self, size_bytes: int) -> str:
        """Format byte size into a human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


def run_benchmarks() -> None:
    """Main function to run all benchmarks and display results."""
    print("Initializing tokenizers...")
    tokenizers = []
    
    # Add tiktoken adapter
    tokenizers.append(TiktokenAdapter())
    
    # Add HuggingFace tokenizers adapter
    tokenizers.append(HFTokenizerAdapter())
    
    # Add rs_bpe adapters if available
    if RS_BPE_AVAILABLE:
        try:
            # Add basic rs_bpe adapter
            tokenizers.append(RsBpeAdapter())
            
            # Add cached rs_bpe adapter
            tokenizers.append(RsBpeCachedAdapter())
            
        except ImportError:
            print("Warning: Failed to initialize rs_bpe adapters.")
    else:
        print("Skipping rs_bpe adapters as the module is not available.")
    
    if not tokenizers:
        print("Error: No tokenizers available for benchmarking.")
        sys.exit(1)
    
    print("Running benchmarks...")
    runner = BenchmarkRunner(tokenizers, num_runs=3)
    results = runner.run_benchmarks()
    
    # Print raw benchmark results
    runner.print_results()
    
    # Generate and display plots
    print("\nGenerating performance plots...")
    runner.plot_results(save_path="tokenizer_benchmark_results")
    
    print("\nBenchmark completed!")


if __name__ == "__main__":
    run_benchmarks()
