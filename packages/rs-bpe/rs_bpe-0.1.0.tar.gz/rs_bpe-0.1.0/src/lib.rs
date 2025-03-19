use std::borrow::Cow;
use std::sync::Once;
use std::sync::Mutex;
use pyo3::prelude::*;
use once_cell::sync::Lazy;

// Global static instances of tokenizers
static CL100K_TOKENIZER: Lazy<Mutex<Option<&'static ::bpe_openai::Tokenizer>>> = 
    Lazy::new(|| Mutex::new(None));
static O200K_TOKENIZER: Lazy<Mutex<Option<&'static ::bpe_openai::Tokenizer>>> = 
    Lazy::new(|| Mutex::new(None));
static CL100K_INIT: Once = Once::new();
static O200K_INIT: Once = Once::new();

#[pyclass]
struct BytePairEncoding(&'static ::bpe::byte_pair_encoding::BytePairEncoding);

#[pymethods]
impl BytePairEncoding {
    fn count(&self, input: &[u8]) -> usize {
        self.0.count(input)
    }

    fn encode_via_backtracking(&self, input: &[u8]) -> Vec<u32> {
        self.0.encode_via_backtracking(input)
    }

    fn decode_tokens(&self, tokens: Vec<u32>) -> Vec<u8> {
        self.0.decode_tokens(&tokens)
    }
}

/// Python wrapper for ParallelOptions
#[pyclass]
#[derive(Clone)]
struct ParallelOptions {
    inner: ::bpe_openai::ParallelOptions,
}

#[pymethods]
impl ParallelOptions {
    #[new]
    fn new(min_batch_size: Option<usize>, chunk_size: Option<usize>, max_threads: Option<usize>) -> Self {
        let mut options = ::bpe_openai::ParallelOptions::default();
        
        if let Some(min_batch_size) = min_batch_size {
            options.min_batch_size = min_batch_size;
        }
        
        if let Some(chunk_size) = chunk_size {
            options.chunk_size = chunk_size;
        }
        
        if let Some(max_threads) = max_threads {
            options.max_threads = max_threads;
        }
        
        Self { inner: options }
    }
    
    #[getter]
    fn min_batch_size(&self) -> usize {
        self.inner.min_batch_size
    }
    
    #[getter]
    fn chunk_size(&self) -> usize {
        self.inner.chunk_size
    }
    
    #[getter]
    fn max_threads(&self) -> usize {
        self.inner.max_threads
    }
}

#[pyclass]
struct Tokenizer(&'static ::bpe_openai::Tokenizer);

#[pymethods]
impl Tokenizer {
    fn count(&self, input: &str) -> usize {
        self.0.count(&input)
    }

    fn count_till_limit(&self, input: Cow<str>, limit: usize) -> Option<usize> {
        self.0.count_till_limit(&input, limit)
    }

    fn encode(&self, input: Cow<str>) -> Vec<u32> {
        self.0.encode(&input)
    }
    
    fn encode_batch(&self, texts: Vec<String>) -> PyResult<(Vec<Vec<u32>>, usize, f64)> {
        let str_texts: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let result = self.0.encode_batch(&str_texts);
        Ok((result.tokens, result.total_tokens, result.time_taken))
    }
    
    fn encode_batch_parallel(&self, texts: Vec<String>, options: Option<ParallelOptions>) -> PyResult<(Vec<Vec<u32>>, usize, f64, usize)> {
        let str_texts: Vec<&str> = texts.iter().map(|s| s.as_str()).collect();
        let rust_options = options.map(|opts| opts.inner);
        let tokens = self.0.encode_batch_parallel(&str_texts, rust_options);
        let total_tokens = tokens.iter().map(|t| t.len()).sum();
        
        // Backward compatibility values
        let time_taken = 0.0;
        let threads_used = num_cpus::get();
        
        Ok((tokens, total_tokens, time_taken, threads_used))
    }

    fn decode(&self, tokens: Vec<u32>) -> Option<String> {
        self.0.decode(&tokens)
    }
    
    fn decode_batch(&self, batch_tokens: Vec<Vec<u32>>) -> Vec<Option<String>> {
        self.0.decode_batch(&batch_tokens)
    }
    
    fn decode_batch_parallel(&self, batch_tokens: Vec<Vec<u32>>, options: Option<ParallelOptions>) -> Vec<Option<String>> {
        let rust_options = options.map(|opts| opts.inner);
        self.0.decode_batch_parallel(&batch_tokens, rust_options)
    }

    fn bpe(&self) -> BytePairEncoding {
        BytePairEncoding(&self.0.bpe)
    }
}

/// OpenAI tokenizer interface
#[pymodule]
fn openai(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Tokenizer>()?;
    m.add_class::<ParallelOptions>()?;
    m.add_function(wrap_pyfunction!(cl100k_base, m)?)?;
    m.add_function(wrap_pyfunction!(o200k_base, m)?)?;
    m.add_function(wrap_pyfunction!(is_cached_cl100k, m)?)?;
    m.add_function(wrap_pyfunction!(is_cached_o200k, m)?)?;
    m.add_function(wrap_pyfunction!(get_num_threads, m)?)?;
    Ok(())
}

#[pyfunction]
fn cl100k_base() -> PyResult<Tokenizer> {
    CL100K_INIT.call_once(|| {
        let mut tokenizer = CL100K_TOKENIZER.lock().unwrap();
        *tokenizer = Some(::bpe_openai::cl100k_base());
    });
    
    let tokenizer_opt = CL100K_TOKENIZER.lock().unwrap();
    Ok(Tokenizer(*tokenizer_opt.as_ref().unwrap()))
}

#[pyfunction]
fn o200k_base() -> PyResult<Tokenizer> {
    O200K_INIT.call_once(|| {
        let mut tokenizer = O200K_TOKENIZER.lock().unwrap();
        *tokenizer = Some(::bpe_openai::o200k_base());
    });
    
    let tokenizer_opt = O200K_TOKENIZER.lock().unwrap();
    Ok(Tokenizer(*tokenizer_opt.as_ref().unwrap()))
}

#[pyfunction]
fn is_cached_cl100k() -> PyResult<bool> {
    let tokenizer = CL100K_TOKENIZER.lock().unwrap();
    Ok(tokenizer.is_some())
}

#[pyfunction]
fn is_cached_o200k() -> PyResult<bool> {
    let tokenizer = O200K_TOKENIZER.lock().unwrap();
    Ok(tokenizer.is_some())
}

#[pyfunction]
fn get_num_threads() -> PyResult<usize> {
    Ok(rayon::current_num_threads())
}

/// BPE implementation in Rust
#[pymodule]
fn bpe(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BytePairEncoding>()?;
    
    let openai = pyo3::wrap_pymodule!(openai);
    m.add_wrapped(openai)?;
    
    Ok(())
}
