# Hapax Graph API

The Hapax Graph API provides a flexible and intuitive way to build complex data processing pipelines. Inspired by frameworks like JAX and Flyte, it offers a fluent interface for composing operations and defining workflows, with built-in type checking at import time.

## Core Concepts

### Type-Safe Operations

Operations are the basic building blocks of a Hapax graph. Each operation is a pure function that takes an input and produces an output. Operations are type-checked at both import time and runtime:

```python
@ops(name="summarize", tags=["llm"])
def summarize(text: str) -> str:
    """Generate a concise summary using LLM."""
    # Implementation
```

The `@ops` decorator performs initial type validation at import time, ensuring the function has proper type hints. Further type checking occurs at runtime when the operation is executed.

### Type Validation Stages

Hapax performs comprehensive type checking at multiple stages:

1. Import Time (Static):
   - Validates presence of type hints through the `@ops` decorator
   - Checks input parameter types exist
   - Verifies return type annotations exist
   - Stores validated type information for later use

2. Graph Definition Time:
   - Type compatibility between connected operations
   - Structural validation (cycles, missing connections)
   - Configuration and metadata validation
   - Immediate type checking when using operation composition (`>>`)

3. Runtime (Dynamic):
   - Input type validation before operation execution
   - Output type validation after operation execution
   - Complete graph validation during execution
   - Type checking of operation results
   - Resource availability checks
   - Configuration validation

This multi-stage type checking ensures type safety throughout the entire lifecycle of your data processing pipeline:
- Early detection of type-related issues during development (import time)
- Immediate feedback when building graphs (definition time)
- Runtime safety guarantees during execution

For example, the following code would fail at different stages:

```python
# Fails at import time - missing type hints
@ops(name="bad_op")
def no_type_hints(x):
    return x + 1

# Fails at graph definition time - type mismatch
graph = (
    Graph("type_mismatch")
    .then(str_op)      # str -> str
    .then(int_op)      # int -> int  # Type error!
)

# Fails at runtime - actual input type doesn't match declaration
@ops(name="runtime_check")
def expect_string(text: str) -> str:
    return text.upper()

result = expect_string(123)  # Runtime type error
```

### Compile-Time Type Validation

A Graph is a collection of operations connected in a specific way. The Graph class provides a fluent API for building these connections, with comprehensive type checking at definition time:

```python
# Type compatibility is checked when the graph is defined
graph = (
    Graph("name", "description")
    .then(op1)  # Type compatibility checked immediately
    .then(op2)  # Type compatibility checked immediately
)
```

## Building Blocks

### 1. Sequential Operations (`.then()`)

Chain operations one after another with automatic type checking:

```python
graph = (
    Graph("text_processing")
    .then(clean_text)      # Returns str
    .then(tokenize)        # Expects str, returns List[str]
    .then(analyze)         # Expects List[str]
)
```

### 2. Parallel Processing (`.branch()`)

Execute multiple operations in parallel with type-safe result collection:

```python
graph = (
    Graph("parallel_processing")
    .branch(
        sentiment_analysis,  # Branch 1: str -> float
        entity_extraction,   # Branch 2: str -> List[str]
        topic_modeling      # Branch 3: str -> Dict[str, float]
    )
    .merge(combine_results)  # List[Union[float, List[str], Dict[str, float]]] -> Result
)
```

### 3. Conditional Logic (`.condition()`)

Add type-safe branching logic:

```python
graph = (
    Graph("language_processing")
    .then(detect_language)  # str -> str
    .condition(
        lambda lang: lang != "en",
        translate,          # str -> str
        lambda x: x        # str -> str (identity)
    )
)
```

### 4. Loops (`.loop()`)

Repeat an operation with type-safe condition checking:

```python
graph = (
    Graph("retry_logic")
    .loop(
        api_call,           # Request -> Response
        condition=lambda response: response.status == "success",
        max_iterations=3
    )
)
```

## Error Handling

Hapax provides clear error messages when validation fails:

1. Type Mismatch:
```python
TypeError: Cannot compose operations: output type List[str] does not match input type Dict[str, Any]
```

2. Structural Issues:
```python
GraphValidationError: Graph contains cycles: [['op1', 'op2', 'op1']]
```

3. Configuration Issues:
```python
ValueError: Missing required configuration: operation 'api_call' requires API endpoint
```

### Custom Error Types

Hapax includes specialized error types for different parts of graph execution:

1. **BranchError**: Provides information about errors in parallel branches
```python
try:
    result = graph.execute(data)
except BranchError as e:
    print(f"Branch errors: {e.branch_errors}")  # List of (branch_name, exception) tuples
    print(f"Partial results: {e.partial_results}")  # Results from successful branches
```

2. **MergeError**: Details issues when merging branch results
```python
try:
    result = graph.execute(data)
except MergeError as e:
    print(f"Merge input data: {e.inputs}")  # The inputs that failed to merge
```

3. **ConditionError**: Information about failures in conditional operations
```python
try:
    result = graph.execute(data)
except ConditionError as e:
    print(f"Input data: {e.input_data}")
    print(f"Predicate result: {e.predicate_result}")
```

4. **LoopError**: Details about loop operation failures
```python
try:
    result = graph.execute(data)
except LoopError as e:
    print(f"Completed iterations: {e.iterations}")
    print(f"Last error: {e.last_error}")
```

5. **EvaluationError**: Raised when output evaluation fails
```python
try:
    result = graph.execute(data)
except EvaluationError as e:
    print(f"Evaluation failure: {str(e)}")
```

6. **GraphExecutionError**: Comprehensive information about graph execution failures
```python
try:
    result = graph.execute(data)
except GraphExecutionError as e:
    print(f"Failed node: {e.node_name}")
    print(f"Node errors: {e.node_errors}")  # List of (node_name, exception) tuples
    print(f"Partial results: {e.partial_results}")  # Dictionary of node_name to result
```

7. **GraphValidationError**: Details about graph structure validation failures
```python
try:
    graph.validate()
except GraphValidationError as e:
    print(f"Validation error: {str(e)}")
    print(f"Original error: {e.error}")
```

## Example: Advanced NLP Pipeline

Here's a real-world example that showcases the power and flexibility of the Graph API:

```python
def create_nlp_pipeline() -> Graph[str, Dict[str, Any]]:
    return (
        Graph("nlp_pipeline", "Advanced NLP processing pipeline")
        # First detect language and translate if needed
        .then(detect_language)
        .condition(
            lambda lang: lang != "en",
            translate,
            lambda x: x
        )
        # Then process in parallel
        .branch(
            summarize,           # Branch 1: Summarization
            sentiment_analysis,  # Branch 2: Sentiment
            extract_entities,    # Branch 3: Entity extraction
            extract_keywords     # Branch 4: Keyword extraction
        )
        # Merge results
        .merge(combine_results)
    )
```

This pipeline:
1. Detects the language of input text
2. Translates to English if needed
3. Processes the text in parallel:
   - Generates a summary
   - Analyzes sentiment and emotions
   - Extracts named entities
   - Identifies key topics
4. Combines all results into a structured output

## Type Safety

The Graph API includes built-in type checking to ensure type safety across operations:

```python
def tokenize(text: str) -> List[str]: ...
def analyze(tokens: List[str]) -> Dict[str, float]: ...

# Types are checked at runtime
graph = Graph("example").then(tokenize).then(analyze)
```

## Monitoring and Observability

Hapax integrates with OpenLit for monitoring and observability:

```python
# Configure globally
set_openlit_config({
    "trace_content": True,
    "disable_metrics": False
})

# Operations are automatically monitored
@ops(name="process", tags=["processing"])
def process(data: str) -> str:
    # OpenLit will trace this operation
    return data.upper()
```

## Best Practices

1. **Modularity**: Keep operations small and focused on a single task
2. **Type Hints**: Always use type hints to catch type errors early
3. **Documentation**: Add clear docstrings to operations
4. **Error Handling**: Use appropriate error handling in operations
5. **Monitoring**: Configure OpenLit for production monitoring

## Advanced Features

### Evaluation Integration

Hapax provides built-in support for evaluating graph outputs:

```python
# Configure evaluation for this graph
graph = (
    Graph("llm_pipeline", "LLM processing pipeline")
    .then(preprocess_text)
    .then(generate_response)
    .with_evaluation(
        eval_type="hallucination",    # Can be "all", "hallucination", "bias", "toxicity"
        threshold=0.7,                # Score threshold (0.0 to 1.0)
        provider="openai",           # LLM provider ("openai", "anthropic")
        fail_on_evaluation=True,     # Whether to raise exception on failure
        model="gpt-4o",              # Optional specific model to use
        custom_config={"trace_content": True}  # Additional configuration
    )
)

# Evaluation results available after execution
result = graph.execute(input_text)
if graph.last_evaluation:
    print(f"Evaluation results: {graph.last_evaluation}")
```

### GPU Monitoring

For graphs that use GPU-accelerated operations, built-in monitoring is available:

```python
# Enable GPU monitoring
graph = (
    Graph("gpu_intensive", "GPU-intensive processing pipeline")
    .then(preprocess_data)
    .then(train_model)
    .with_gpu_monitoring(
        enabled=True,
        sample_rate_seconds=2,
        custom_config={"log_to_file": True, "log_file": "gpu_metrics.log"}
    )
)

# GPU metrics will be collected during execution
result = graph.execute(training_data)
```

### Operation Composition

Operations can be composed using the `>>` operator:

```python
pipeline = tokenize >> normalize >> analyze
```

This is equivalent to:

```python
pipeline = tokenize.compose(normalize).compose(analyze)
```

And also equivalent to:

```python
pipeline = Graph("pipeline").then(tokenize).then(normalize).then(analyze)
```

### Graph Visualization

Hapax provides built-in visualization for graphs:

```python
# Create a graph
graph = (
    Graph("visualization_example")
    .then(preprocess)
    .branch(
        analyze_sentiment,
        extract_entities,
        summarize
    )
    .merge(combine_results)
)

# Generate a visualization
graph.visualize()
```

The visualization shows the graph structure, operation relationships, and type information, making it easier to understand complex pipelines.

### Automatic Type Inference

The Graph API automatically infers input and output types from function signatures:

```python
@ops(name="process")
def process(text: str) -> List[str]:
    # Input and output types are automatically extracted
    return text.split()
```

When operations are combined in a graph, the type compatibility is checked automatically:

```python
@ops(name="tokenize")
def tokenize(text: str) -> List[str]:
    return text.split()

@ops(name="count")
def count(tokens: List[str]) -> int:
    return len(tokens)

# Types are checked during graph definition
graph = Graph("example").then(tokenize).then(count)  # Works correctly

# This would fail at definition time due to incompatible types
graph = Graph("example").then(count).then(tokenize)  # Type error!
```

### Explicit Graph Validation

While Hapax performs validation during graph definition and execution, you can also explicitly validate a graph without executing it:

```python
# Define a graph
graph = (
    Graph("complex_processing")
    .then(preprocess)
    .branch(
        analyze_sentiment,
        extract_entities,
        summarize
    )
    .merge(combine_results)
)

# Explicitly validate the graph
try:
    graph.validate()
    print("Graph is valid")
except GraphValidationError as e:
    print(f"Graph validation failed: {e}")
    print(f"Original error: {e.error}")
```

The `validate()` method performs comprehensive checks:
- Cycle detection (except in Loop operators)
- Type compatibility between connected operations
- Configuration validation
- Flow operator structure validation

This is useful during development or before deploying a graph to production to catch potential issues early.