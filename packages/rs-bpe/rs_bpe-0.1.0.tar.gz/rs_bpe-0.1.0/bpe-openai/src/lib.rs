use std::sync::LazyLock;
use std::sync::Arc;
use std::cell::RefCell;

use bpe::byte_pair_encoding::BytePairEncoding;
use either::Either;
use regex_automata::{
    meta::{BuildError, Regex},
    util::captures::Captures,
    Anchored, Input,
};
use rayon::prelude::*;
use rayon::ThreadPoolBuilder;
use once_cell::sync::Lazy;

// Global thread pool optimized for tokenization workloads
static TOKENIZER_POOL: Lazy<rayon::ThreadPool> = Lazy::new(|| {
    ThreadPoolBuilder::new()
        .num_threads(get_optimal_thread_count())
        .thread_name(|i| format!("tokenizer-{}", i))
        .stack_size(2 * 1024 * 1024) // 2MB stack size
        .build()
        .expect("Failed to build tokenizer thread pool")
});

// Thread-local cache for pre-split regex matches
thread_local! {
    static TEXT_CHUNK_CACHE: RefCell<Vec<Vec<u8>>> = RefCell::new(Vec::with_capacity(1024));
}

// Returns optimal thread count for tokenization workloads
fn get_optimal_thread_count() -> usize {
    let physical_cores = num_cpus::get_physical();
    let logical_cores = num_cpus::get();
    
    // Heuristic: For tokenization, using physical core count often gives better 
    // performance due to reduced cache contention
    std::cmp::max(1, std::cmp::min(physical_cores, logical_cores / 2))
}

// Note: Below we rewrite the negative look-ahead with a positive pseudo look-ahead.
// The look-ahead character is dropped from the match by the Pretokenizer iterator.
// Note: The negative look-ahead `\\s+(?!\\S)` requires `\\s+\\s` but also `\\s+$` to handle end of file without dropping a character!

static BPE_CL100K_BASE: LazyLock<Tokenizer> = LazyLock::new(|| {
    let bytes = include_bytes!(concat!(env!("OUT_DIR"), "/bpe_cl100k_base.dict"));
    let bpe = rmp_serde::from_slice(bytes).expect("valid bpe data");
    let pat1 = "(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\\r\\n\\p{L}\\p{N}]?\\p{L}+|\\p{N}{1,3}| ?[^\\s\\p{L}\\p{N}]+[\\r\\n]*|\\s*[\\r\\n]+|\\s+$";
    let pat2 = "\\s+\\s";
    let pat3 = "\\s+";
    Tokenizer::new_lookahead(bpe, &[(pat1, false), (pat2, true), (pat3, false)])
        .expect("valid regex")
});

static BPE_O200K_BASE: LazyLock<Tokenizer> = LazyLock::new(|| {
    let bytes = include_bytes!(concat!(env!("OUT_DIR"), "/bpe_o200k_base.dict"));
    let bpe = rmp_serde::from_slice(bytes).expect("valid bpe data");
    let pat1 = [
        "[^\\r\\n\\p{L}\\p{N}]?[\\p{Lu}\\p{Lt}\\p{Lm}\\p{Lo}\\p{M}]*[\\p{Ll}\\p{Lm}\\p{Lo}\\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?",
        "[^\\r\\n\\p{L}\\p{N}]?[\\p{Lu}\\p{Lt}\\p{Lm}\\p{Lo}\\p{M}]+[\\p{Ll}\\p{Lm}\\p{Lo}\\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?",
        "\\p{N}{1,3}",
        " ?[^\\s\\p{L}\\p{N}]+[\\r\\n/]*",
        "\\s*[\\r\\n]+",
        "\\s+$",
    ].join("|");
    let pat2 = "\\s+\\s";
    let pat3 = "\\s+";
    Tokenizer::new_lookahead(bpe, &[(&pat1, false), (pat2, true), (pat3, false)])
        .expect("valid regex")
});

pub use bpe::*;

/// A byte-pair encoding tokenizer that supports a pre-tokenization regex.
/// The direct methods on this type pre-tokenize the input text and should
/// produce the same output as the tiktoken tokenizers. The type gives access
/// to the regex and underlying byte-pair encoding if needed. Note that using
/// the byte-pair encoding directly does not take the regex into account and
/// may result in output that differs from tiktoken.
#[derive(Clone)]
pub struct Tokenizer {
    /// The byte-pair encoding for this tokenizer.
    pub bpe: BytePairEncoding,
    /// The pattern regex used to split the input.
    pub pre: Option<Pretokenizer>,
}

#[derive(Clone)]
pub struct Pretokenizer {
    /// The pattern regex used to split the input.
    pat: Regex,
    /// For each pattern in the regex a boolean whether the last character is a look-ahead.
    lookahead: Vec<bool>,
}

/// Result of batch encoding operation
#[derive(Debug)]
pub struct BatchEncodeResult {
    /// The encoded tokens for each input text
    pub tokens: Vec<Vec<u32>>,
    /// Total number of tokens across all texts
    pub total_tokens: usize,
    /// Time taken for the batch operation in seconds
    pub time_taken: f64,
}

/// Processing options for parallel encoding
#[derive(Debug, Clone, Copy)]
pub struct ParallelOptions {
    /// Minimum batch size to trigger parallel processing
    pub min_batch_size: usize,
    /// Target chunk size for each thread
    pub chunk_size: usize,
    /// Maximum number of threads to use (0 for unlimited)
    pub max_threads: usize,
    /// Use thread pool for processing (more efficient for repeated calls)
    pub use_thread_pool: bool,
}

impl Default for ParallelOptions {
    fn default() -> Self {
        Self {
            min_batch_size: 20, // Increased from previous value based on benchmarks
            chunk_size: 100,
            max_threads: 0,
            use_thread_pool: true,
        }
    }
}

impl Tokenizer {
    /// Build a tokenizer with an optional pretokenization regex pattern.
    #[allow(clippy::result_large_err)]
    pub fn new(bpe: BytePairEncoding, pat: Option<&str>) -> Result<Self, BuildError> {
        let pre = pat.map(Pretokenizer::new).transpose()?;
        Ok(Self { bpe, pre })
    }

    /// Build a tokenizer with pretokenization regex patterns. If the boolean for a pattern is true,
    /// the pattern is assumed to be a look-ahead pattern with exactly one look-ahead character!
    #[allow(clippy::result_large_err)]
    pub fn new_lookahead(
        bpe: BytePairEncoding,
        patterns: &[(&str, bool)],
    ) -> Result<Self, BuildError> {
        let pre = Some(Pretokenizer::new_lookahead(patterns)?);
        Ok(Self { bpe, pre })
    }

    /// Count the number of tokens produced when encoding the text. Applies pre-tokenization
    /// before counting.
    pub fn count(&self, text: &str) -> usize {
        self.split(text)
            .map(|piece| self.bpe.count(piece.as_bytes()))
            .sum()
    }

    /// Returns the token count iff the total token count stays below the specified token_limit.
    /// Otherwise, it returns none. This function can be faster than [`Self::count`]` when the
    /// token limit is much smaller than the provided text. Applies pre-tokenization before counting.
    pub fn count_till_limit(&self, text: &str, token_limit: usize) -> Option<usize> {
        self.split(text).try_fold(0, |consumed, piece| {
            self.bpe
                .count_till_limit(piece.as_bytes(), token_limit - consumed)
                .map(|piece_count| consumed + piece_count)
        })
    }

    /// Returns the tokens for the encoding of the given text. Applies pre-tokenization before
    /// encoding.
    pub fn encode(&self, text: &str) -> Vec<u32> {
        self.split(text)
            .flat_map(|piece| self.bpe.encode_via_backtracking(piece.as_bytes()))
            .collect()
    }

    /// Encodes multiple texts efficiently in a single batch operation.
    /// This avoids repeated initialization overhead and is more efficient for processing
    /// multiple texts.
    ///
    /// # Arguments
    /// * `texts` - A slice of strings to encode
    ///
    /// # Returns
    /// A `BatchEncodeResult` containing the encoded tokens and timing information
    pub fn encode_batch(&self, texts: &[&str]) -> BatchEncodeResult {
        use std::time::Instant;
        
        let start = Instant::now();
        let mut tokens = Vec::with_capacity(texts.len());
        let mut total_tokens = 0;
        
        for &text in texts {
            let encoded = self.encode(text);
            total_tokens += encoded.len();
            tokens.push(encoded);
        }
        
        let time_taken = start.elapsed().as_secs_f64();
        
        BatchEncodeResult {
            tokens,
            total_tokens,
            time_taken,
        }
    }
    
    /// Encodes multiple texts in parallel using multiple threads.
    ///
    /// This method provides improved performance when encoding larger batches of text.
    /// Internally uses Rayon for parallel processing.
    ///
    /// # Arguments
    ///
    /// * `texts` - Slice of string references to encode
    /// * `options` - Options for parallel processing
    ///
    /// # Returns
    ///
    /// Struct containing the encoded tokens and performance statistics
    #[allow(unused_variables)]
    pub fn encode_batch_parallel(&self, texts: &[&str], options: Option<ParallelOptions>) -> Vec<Vec<u32>> {
        let options = options.unwrap_or_default();
        
        // Debug print for start time and batch size
        // println!("Rust DEBUG: Starting parallel encode for {} texts", texts.len());
        let start_time = std::time::Instant::now();
        
        // If batch is too small, use regular sequential processing
        if texts.len() < options.min_batch_size {
            // println!("Rust DEBUG: Batch too small, using sequential processing");
            let sequential_result = self.encode_batch(texts);
            let elapsed = start_time.elapsed();
            // println!("Rust DEBUG: Sequential completed in {:?}", elapsed);
            return sequential_result.tokens;
        }
        
        // Determine thread count based on options
        let available_threads = rayon::current_num_threads();
        let threads_used = if options.max_threads > 0 {
            std::cmp::min(options.max_threads, available_threads)
        } else {
            available_threads
        };
        
        // println!("Rust DEBUG: Using {} threads of {} available", threads_used, available_threads);
        
        // Create immutable reference for thread safety
        let tokenizer = Arc::new(self.clone());
        
        // Pre-allocate result vector to avoid resizing
        let mut tokens = Vec::with_capacity(texts.len());
        
        if options.use_thread_pool {
            // Use our optimized thread pool
            // println!("Rust DEBUG: Using optimized thread pool");
            let pool_start = std::time::Instant::now();
            
            TOKENIZER_POOL.install(|| {
                // Process all inputs in parallel and collect results
                tokens = texts.par_iter()
                    .map(|&text| {
                        let tokenizer = &tokenizer;
                        tokenizer.encode_cached(text)
                    })
                    .collect();
            });
            
            // println!("Rust DEBUG: Thread pool processing took {:?}", pool_start.elapsed());
        } else {
            // Use default Rayon parallelism
            // println!("Rust DEBUG: Using default Rayon parallelism");
            let rayon_start = std::time::Instant::now();
            
            tokens = texts.par_iter()
                .map(|&text| {
                    let tokenizer = &tokenizer;
                    tokenizer.encode(text)
                })
                .collect();
                
            // println!("Rust DEBUG: Rayon processing took {:?}", rayon_start.elapsed());
        }
        
        let total_tokens: usize = tokens.iter().map(|t| t.len()).sum();
        let elapsed = start_time.elapsed();
        // println!("Rust DEBUG: Total parallel encode completed in {:?}, produced {} tokens", elapsed, total_tokens);
        
        tokens
    }
    
    /// Optimized encoding with thread-local caching for parallel workloads
    fn encode_cached(&self, text: &str) -> Vec<u32> {
        if let Some(pre) = &self.pre {
            let mut result = Vec::new();
            
            // Use thread-local cache for the chunks
            TEXT_CHUNK_CACHE.with(|cache| {
                let mut chunks = cache.borrow_mut();
                chunks.clear();
                
                // Collect all chunks using split instead of matches
                for piece in pre.split(text) {
                    chunks.push(piece.as_bytes().to_vec());
                }
                
                // Process all chunks
                for piece in chunks.iter() {
                    if let Some(token) = self.bpe.token(piece) {
                        result.push(token);
                    } else {
                        let mut encoded = self.bpe.encode_bytes(piece);
                        result.append(&mut encoded);
                    }
                }
            });
            
            result
        } else {
            self.bpe.encode(text)
        }
    }

    /// Returns the text corresponding to the given encoding if it is valid UTF-8. Otherwise,
    /// returns none.
    pub fn decode(&self, tokens: &[u32]) -> Option<String> {
        String::from_utf8(self.bpe.decode_tokens(tokens)).ok()
    }
    
    /// Decodes multiple token sequences efficiently in a single batch operation.
    ///
    /// # Arguments
    /// * `batch_tokens` - A slice of token sequences to decode
    ///
    /// # Returns
    /// A vector of optional strings (None for invalid UTF-8)
    pub fn decode_batch(&self, batch_tokens: &[Vec<u32>]) -> Vec<Option<String>> {
        batch_tokens.iter()
            .map(|tokens| self.decode(tokens))
            .collect()
    }
    
    /// Decodes multiple token sequences in parallel for improved performance.
    ///
    /// # Arguments
    ///
    /// * `batch_tokens` - Slice of token vectors to decode
    /// * `options` - Options for parallel processing
    ///
    /// # Returns
    ///
    /// Vector of decoded strings (None for invalid UTF-8)
    pub fn decode_batch_parallel(&self, batch_tokens: &[Vec<u32>], options: Option<ParallelOptions>) -> Vec<Option<String>> {
        let options = options.unwrap_or_default();
        
        // If batch is too small, use regular sequential processing
        if batch_tokens.len() < options.min_batch_size {
            return self.decode_batch(batch_tokens);
        }
        
        // Clone for parallel usage
        let tokenizer = Arc::new(self.clone());
        
        let mut results = Vec::with_capacity(batch_tokens.len());
        
        if options.use_thread_pool {
            // Use our optimized thread pool
            TOKENIZER_POOL.install(|| {
                // Process in parallel
                results = batch_tokens.par_iter()
                    .map(|tokens| {
                        let tokenizer = &tokenizer;
                        tokenizer.decode(tokens)
                    })
                    .collect();
            });
        } else {
            // Use default Rayon parallelism
            results = batch_tokens.par_iter()
                .map(|tokens| {
                    let tokenizer = &tokenizer;
                    tokenizer.decode(tokens)
                })
                .collect();
        }
        
        results
    }

    /// Returns an iterator with the text pieces resulting from pre-tokenization. If this
    /// tokenizer does not have pre-tokenization, the iterator returns the full text.
    pub fn split<'a>(&'a self, text: &'a str) -> impl Iterator<Item = &'a str> + 'a {
        match &self.pre {
            Some(pre) => Either::Left(pre.split(text)),
            None => Either::Right(std::iter::once(text)),
        }
    }
}

impl Pretokenizer {
    /// Build a pretokenizer from the given regex pattern.
    #[allow(clippy::result_large_err)]
    fn new(pat: &str) -> Result<Self, BuildError> {
        let pat = Regex::new(pat)?;
        Ok(Self {
            pat,
            lookahead: vec![false],
        })
    }

    /// Build a pretokenizer from the given regex patterns. If the boolean for a pattern is true,
    /// the pattern is assumed to be a look-ahead pattern with exactly one look-ahead character!
    #[allow(clippy::result_large_err)]
    fn new_lookahead(pats: &[(&str, bool)]) -> Result<Self, BuildError> {
        let (pats, lookahead): (Vec<_>, _) = pats.iter().copied().unzip();
        let pat = Regex::new_many(&pats)?;
        Ok(Self { pat, lookahead })
    }

    /// Returns an iterator with the text pieces after splitting with the regular expression.
    pub fn split<'a>(&'a self, text: &'a str) -> impl Iterator<Item = &'a str> + 'a {
        Splits {
            pat: &self.pat,
            lookahead: &self.lookahead,
            text,
            last: 0,
            caps: Captures::matches(self.pat.group_info().clone()),
        }
    }
}

/// This is a small wrapper around the regex which emulates the behaviour of look-ahead by
/// dropping the look-ahead character from the match. The assumption here is that the
/// second pattern is always a look-ahead pattern, and that just a single character needs
/// to be dropped. With this little hack, we can keep most of the regex patterns as they are,
/// but achieve a >3x speedup.
///
/// Alternatively, this could have been implemented with capture groups, but those were ~30%
/// slower than this approach with multiple patterns.
struct Splits<'a> {
    pat: &'a Regex,
    lookahead: &'a [bool],
    text: &'a str,
    last: usize,
    caps: Captures,
}

impl<'a> Iterator for Splits<'a> {
    type Item = &'a str;

    fn next(&mut self) -> Option<Self::Item> {
        let input = Input::new(&self.text[self.last..]).anchored(Anchored::Yes);
        self.caps.clear();
        self.pat.captures(input, &mut self.caps);
        let m = self.caps.get_match()?;
        let start = self.last;
        let mut end = self.last + m.range().end;
        if self.lookahead[m.pattern().as_usize()] {
            let last = self.text[start..end]
                .chars()
                .next_back()
                .expect("Expected at least a look-ahead character!");
            end -= last.len_utf8();
            assert_ne!(end, start, "a look-ahead pattern must ALWAYS consume at least one character excluding the look-ahead character!");
        }
        self.last = end;
        Some(&self.text[start..end])
    }
}

pub fn cl100k_base() -> &'static Tokenizer {
    &BPE_CL100K_BASE
}

pub fn o200k_base() -> &'static Tokenizer {
    &BPE_O200K_BASE
}

#[cfg(test)]
mod tests {
    use bpe::byte_pair_encoding::{create_test_string, select_test_string};
    use tiktoken_rs::{cl100k_base_singleton, o200k_base_singleton, CoreBPE};

    use super::*;

    #[test]
    fn test_cl100k() {
        test_equivalence(cl100k_base(), &cl100k_base_singleton().lock());
    }

    #[test]
    fn test_o200k() {
        test_equivalence(o200k_base(), &o200k_base_singleton().lock());
    }

    #[track_caller]
    fn test_equivalence(tok: &Tokenizer, tiktoken: &CoreBPE) {
        let text = create_test_string(&tok.bpe, 80_000);
        for bytes in [10, 100, 1000, 10_000] {
            for _ in 0..32 {
                let text = select_test_string(&text, bytes);
                let tokens = tok.encode(text);
                let tiktokens = tiktoken.encode_ordinary(text).to_vec();
                assert_eq!(tokens, tiktokens, "encoding mismatch for {text:?}");
            }
        }
    }

    #[test]
    fn test_count_till_limit() {
        assert_eq!(cl100k_base().count_till_limit("abc", 3), Some(1));
        assert_eq!(cl100k_base().count_till_limit("abcabc", 3), Some(2));
        assert_eq!(cl100k_base().count_till_limit("abcabcabc", 3), Some(3));
        assert_eq!(cl100k_base().count_till_limit("abcabcabcabc", 3), None);
    }
    
    #[test]
    fn test_batch_encoding() {
        let tok = cl100k_base();
        let texts = ["Hello world", "Testing batch encoding", "This is a longer text to encode"];
        
        // Test batch encoding
        let batch_result = tok.encode_batch(&texts);
        
        // Verify each result matches individual encoding
        for (i, &text) in texts.iter().enumerate() {
            let individual = tok.encode(text);
            assert_eq!(batch_result.tokens[i], individual, "batch encoding mismatch for text #{i}");
        }
        
        // Verify total count
        let expected_total = texts.iter().map(|&t| tok.encode(t).len()).sum::<usize>();
        assert_eq!(batch_result.total_tokens, expected_total, "total token count mismatch");
    }
    
    #[test]
    fn test_parallel_batch_encoding() {
        let tok = cl100k_base();
        let texts = vec![
            "Hello world",
            "Testing batch encoding",
            "This is a longer text to encode",
            "Let's test parallel processing",
            "With multiple threads and longer texts",
            "To ensure everything works correctly",
            "And the results match the sequential version",
            "Even with many different inputs"
        ];
        
        // Test parallel batch encoding with default options
        let parallel_result = tok.encode_batch_parallel(&texts, None);
        
        // Test sequential batch encoding for comparison
        let sequential_result = tok.encode_batch(&texts);
        
        // Verify parallel processing produces the same results as sequential
        assert_eq!(parallel_result.len(), sequential_result.tokens.len(), 
                   "parallel and sequential results should have the same number of outputs");
        
        for (i, (parallel, sequential)) in parallel_result.iter().zip(sequential_result.tokens.iter()).enumerate() {
            assert_eq!(parallel, sequential, "parallel and sequential results differ for text #{}", i);
        }
        
        assert_eq!(parallel_result.iter().map(|t| t.len()).sum::<usize>(), sequential_result.total_tokens,
                   "parallel and sequential total token counts should match");
        
        // Verify we actually used multiple threads when appropriate
        if texts.len() >= ParallelOptions::default().min_batch_size {
            assert!(parallel_result.len() > 1, "should have used multiple threads");
        }
    }
}
