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
from typing import cast

import matplotlib.pyplot as plt

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


class RsBpeParallelBatchAdapter(TokenizerBatchAdapter):
    """
    Adapter for rs_bpe with parallel batch processing.
    
    Parameters
    ----------
    None
    
    Attributes
    ----------
    tokenizer: The rs_bpe tokenizer instance
    parallel_options: Configuration for parallel processing

    """
    
    def __init__(self):
        """
        Initialize the rs_bpe parallel batch adapter.
        
        Execution Flow:
        1. The function initializes the parent class with the tokenizer name
        2. It loads the cl100k_base tokenizer from rs_bpe
        3. It configures parallel processing options
        """
        super().__init__("rs_bpe_parallel_batch")
        if not RS_BPE_AVAILABLE:
            raise ImportError("rs_bpe not available")
        self.tokenizer = rs_bpe.bpe.openai.cl100k_base()
        
        # Configure parallel options for optimal performance
        # These values were found to work well in previous testing
        self.parallel_options = rs_bpe.bpe.openai.ParallelOptions(  # type: ignore
            min_batch_size=10,
            chunk_size=10,
            max_threads=0  # Use all available threads
        )
        
        # Report how many threads are available
        num_threads = rs_bpe.bpe.openai.get_num_threads()  # type: ignore
        print(f"Parallel tokenizer using {num_threads} threads")
    
    def encode_batch(self, texts: "list[str]") -> "tuple[list[list[int]], float]":
        """
        Encode a batch of texts using rs_bpe parallel batch processing.
        
        Parameters
        ----------
        texts (List[str]): List of texts to encode
        
        Returns
        -------
        Tuple[List[List[int]], float]: The list of token ID lists and time taken
        
        Execution Flow:
        1. The function starts manual timing
        2. It calls the tokenizer's encode_batch_parallel method with parallel options
        3. It ends manual timing
        4. It returns the tokens and measured time

        """
        # Start manual timing
        import time
        start_time = time.time()
        
        # Call the parallel encode method
        tokens, _, _, _ = self.tokenizer.encode_batch_parallel(texts, self.parallel_options)
        
        # End manual timing
        end_time = time.time()
        manual_time = end_time - start_time
        
        # Use manual timing instead of reported time (which is 0.0 after our changes)
        return cast("list[list[int]]", tokens), manual_time
    
    def decode_batch(self, token_batches: "list[list[int]]") -> "tuple[list[str], float]":
        """
        Decode batches of token IDs using rs_bpe parallel batch processing.
        
        Parameters
        ----------
        token_batches (List[List[int]]): List of token ID lists to decode
        
        Returns
        -------
        Tuple[List[str], float]: The decoded texts and time taken
        
        Execution Flow:
        1. The function measures the start time
        2. It passes the token batches to the tokenizer's decode_batch_parallel method
        3. It measures the end time
        4. It returns the results and time taken

        """
        start_time = time.time()
        results = self.tokenizer.decode_batch_parallel(token_batches, self.parallel_options)
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
        
        # Create figures
        fig1, axs1 = plt.subplots(3, 1, figsize=(12, 15))
        fig2, axs2 = plt.subplots(3, 1, figsize=(12, 15))
        
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
            for tokenizer_name in tokenizer_names:
                axs1[i].plot(batch_sizes, time_data[tokenizer_name], marker='o', label=tokenizer_name)
            
            axs1[i].set_title(f"{operation.replace('_', ' ').title()} Time (LOWER IS BETTER)")
            axs1[i].set_xlabel("Batch Size")
            axs1[i].set_ylabel("Time (seconds)")
            axs1[i].grid(axis="y", linestyle="--", alpha=0.7)
            axs1[i].legend()
            
            # Plot throughput data
            for tokenizer_name in tokenizer_names:
                axs2[i].plot(batch_sizes, tps_data[tokenizer_name], marker='o', label=tokenizer_name)
            
            axs2[i].set_title(f"{operation.replace('_', ' ').title()} Throughput (HIGHER IS BETTER)")
            axs2[i].set_xlabel("Batch Size")
            axs2[i].set_ylabel("Tokens per Second")
            axs2[i].grid(axis="y", linestyle="--", alpha=0.7)
            axs2[i].legend()
        
        # Adjust layout
        fig1.tight_layout()
        fig2.tight_layout()
        
        # Save plots if requested
        if save_path:
            fig1.savefig(f"{save_path}_time.svg")
            fig2.savefig(f"{save_path}_throughput.svg")
        
        # Show plots
        plt.show()


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
            
            # Add parallel batch adapter
            tokenizers.append(RsBpeParallelBatchAdapter())
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
