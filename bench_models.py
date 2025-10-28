#!/usr/bin/env python3
"""
Model Benchmarking Tool for TimeCapsuleWriter

This script tests multiple models side-by-side using the same prompt and compares:
- Generation speed (tokens per second)
- Memory usage
- Output quality/coherence
- Victorian-era style accuracy

Usage:
    python bench_models.py --output_file benchmarks.json
    python bench_models.py --models mistralai/Mistral-7B-Instruct-v0.2 microsoft/phi-3-mini-4k-instruct
    python bench_models.py --prompt "A ghost haunts an abandoned factory in Manchester"
"""

import os
import argparse
import json
import time
import gc
import psutil
import torch
from datetime import datetime
from typing import Dict, List, Any, Optional
import tracemalloc
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

import config
from character_utils import load_text_file

# Default models to benchmark
DEFAULT_MODELS = [
    "haykgrigo3/TimeCapsuleLLM",  # Our primary model
    "microsoft/phi-3-mini-4k-instruct",  # Lightweight alternative
    "mistralai/Mistral-7B-Instruct-v0.2",  # Larger model option
]

# Default benchmark prompt (short logline)
DEFAULT_PROMPT = "A conscientious clerk in fogbound London must deliver a perilous parcel."

# Victorian style keywords for simple quality assessment
VICTORIAN_KEYWORDS = [
    "upon", "whilst", "wherein", "thence", "hitherto", 
    "ought", "perchance", "nevertheless", "forthwith", "alas",
    "countenance", "endeavour", "lamentable", "vexation", "particulars",
    "constitution", "impudent", "approbation", "odious", "felicity",
    "henceforth", "scarcely", "indignation", "melancholy", "sentiment",
    "agreeable", "acquaintance", "perceive", "present", "circumstance"
]

def measure_memory():
    """Measure current memory usage."""
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

def create_generator(model_id: str):
    """
    Create a generator pipeline for the specified model.
    
    Args:
        model_id: HuggingFace model ID
        
    Returns:
        The generator pipeline and tokenizer
    """
    print(f"Loading model: {model_id}")
    start_memory = measure_memory()
    start_time = time.time()
    
    # Load tokenizer and model
    # Default: do not trust remote code unless caller passes it via args
    trust_flag = False
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_flag)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=trust_flag,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True
    )
    
    # Create the generator
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=400,
        temperature=0.9,
        top_p=0.95,
        repetition_penalty=1.1,
        do_sample=True
    )
    
    # Calculate loading stats
    load_time = time.time() - start_time
    memory_used = measure_memory() - start_memory
    
    print(f"Model loaded in {load_time:.2f}s, using {memory_used:.1f}MB of memory")
    return generator, tokenizer, {"load_time": load_time, "memory_used": memory_used}

def benchmark_model(model_id: str, prompt: str, persona_text: str):
    """
    Benchmark a single model.
    
    Args:
        model_id: HuggingFace model ID
        prompt: Text prompt to use for generation
        persona_text: Persona context to prepend
        
    Returns:
        Dictionary with benchmark results
    """
    results = {
        "model_id": model_id,
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        # Create generator
        generator, tokenizer, load_stats = create_generator(model_id)
        results.update(load_stats)
        
        # Prepare full prompt
        full_prompt = f"{persona_text}\n\nWrite a Victorian-era short story based on this concept:\n\n{prompt}"
        input_tokens = tokenizer(full_prompt, return_tensors="pt")["input_ids"].shape[1]
        results["input_tokens"] = input_tokens
        
        # Garbage collection before generation
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        # Generate text and measure performance
        start_time = time.time()
        start_memory = measure_memory()
        
        response = generator(full_prompt, return_full_text=False)[0]['generated_text']
        
        gen_time = time.time() - start_time
        memory_used = measure_memory() - start_memory
        
        # Save generation stats
        output_tokens = tokenizer(response, return_tensors="pt")["input_ids"].shape[1]
        
        results.update({
            "generation_time": gen_time,
            "memory_used_during_generation": memory_used,
            "output_tokens": output_tokens,
            "tokens_per_second": output_tokens / gen_time,
            "output_text": response,
        })
        
        # Simple quality metrics
        results["quality_metrics"] = analyze_output_quality(response)
        
    except Exception as e:
        results["error"] = str(e)
        print(f"Error benchmarking {model_id}: {e}")
    
    # Clean up to free memory
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    return results

def analyze_output_quality(text: str) -> Dict[str, float]:
    """
    Perform basic analysis of output quality.
    
    Args:
        text: Generated text
        
    Returns:
        Dictionary with quality metrics
    """
    # Count Victorian-era terms
    victorian_term_count = sum(1 for term in VICTORIAN_KEYWORDS if term.lower() in text.lower())
    
    # Basic metrics
    words = text.split()
    word_count = len(words)
    avg_word_length = sum(len(word) for word in words) / max(1, word_count)
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    avg_sentence_length = word_count / max(1, sentence_count)
    
    return {
        "word_count": word_count,
        "avg_word_length": avg_word_length,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "victorian_term_count": victorian_term_count,
        "victorian_term_density": victorian_term_count / max(1, word_count) * 100,
    }

def run_benchmarks(args):
    """
    Run benchmarks on all specified models.
    
    Args:
        args: Command line arguments
    
    Returns:
        Dictionary of benchmark results
    """
    # Load persona text
    persona_text = load_text_file(args.persona)
    
    benchmark_results = {
        "prompt": args.prompt,
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "python_version": psutil.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_available": psutil.virtual_memory().total / (1024 * 1024 * 1024),  # GB
            "gpu_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
        },
        "results": []
    }
    
    # Run benchmarks for each model
    for model_id in args.models:
        print(f"\nBenchmarking model: {model_id}")
        result = benchmark_model(model_id, args.prompt, persona_text)
        benchmark_results["results"].append(result)
        
        # Print basic results
        if "error" not in result:
            print(f"  Generation time: {result['generation_time']:.2f}s")
            print(f"  Tokens per second: {result['tokens_per_second']:.2f}")
            print(f"  Output tokens: {result['output_tokens']}")
            print(f"  Victorian terms: {result['quality_metrics']['victorian_term_count']}")
            
            # Save sample of output
            output_sample = result["output_text"][:200] + "..." if len(result["output_text"]) > 200 else result["output_text"]
            print(f"\nSample output:\n{output_sample}\n")
        else:
            print(f"  Error: {result['error']}")
    
    return benchmark_results

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Benchmark multiple language models for Victorian prose generation")
    
    # Model selection
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, 
                        help="List of HuggingFace model IDs to benchmark")
    
    # Content parameters
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, 
                        help="Prompt text to use for benchmarking")
    parser.add_argument("--persona", default=os.path.join(config.PROMPTS_DIR, "persona_victorian.md"),
                        help="Path to persona prompt file")
    
    # Output options
    parser.add_argument("--output_file", help="File to save benchmark results")
    parser.add_argument("--save_samples", action="store_true", 
                        help="Save generated text samples to samples directory")
    
    args = parser.parse_args()
    
    # Run benchmarks
    print(f"Starting benchmarks with {len(args.models)} models...")
    benchmark_results = run_benchmarks(args)
    
    # Save results if requested
    if args.output_file:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
        with open(args.output_file, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        print(f"Benchmark results saved to {args.output_file}")
    
    # Save samples if requested
    if args.save_samples:
        samples_dir = "samples"
        os.makedirs(samples_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for result in benchmark_results["results"]:
            if "error" not in result and "output_text" in result:
                model_name = result["model_id"].split("/")[-1]
                filename = f"{samples_dir}/bench_{model_name}_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write(f"Prompt: {args.prompt}\n\n")
                    f.write(result["output_text"])
                
                print(f"Sample saved to {filename}")
    
    # Print summary
    print("\nBenchmark summary:")
    for result in benchmark_results["results"]:
        model_id = result["model_id"]
        if "error" not in result:
            print(f"{model_id}: {result['tokens_per_second']:.2f} tokens/sec, "
                  f"{result['quality_metrics']['victorian_term_density']:.2f}% Victorian terms")
        else:
            print(f"{model_id}: Error - {result['error']}")
    
if __name__ == "__main__":
    main()
