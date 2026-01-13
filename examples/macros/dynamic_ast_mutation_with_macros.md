# Quantum Macros: Observing and Mutating the Code Superposition

## The Code Waveform: ASTs in Probabilistic States

In classical programming paradigms, the source code you write has a single, deterministic Abstract Syntax Tree (AST) representation. The compiler's job is to parse this fixed structure and generate machine code. In QuantaLang, we introduce the principle of **syntactic superposition**. Before a definitive compilation pass or macro-level observation, a block of code exists not as a single AST, but as a probability distribution of multiple valid ASTs.

Consider this seemingly simple declaration:

```quantalang
// The 'auto' keyword in QuantaLang implies a superposition of potential types
// based on context and potential future assignments.
let data = auto(10);
```

An unobserved `data` variable doesn't have a concrete type. It exists in a superposition of states. Its potential AST representations could include:

*   **State 1 (Probability: 60%):** `data` is an `Int32`. The AST node is `Declaration(name: "data", type: Int32, value: 10)`.
*   **State 2 (Probability: 30%):** `data` is a `Float64` for potential floating-point operations later. The AST node is `Declaration(name: "data", type: Float64, value: 10.0)`.
*   **State 3 (Probability: 10%):** `data` is a `QuantumRegister(size: 10)` if the value is interpreted as a dimension. The AST node is `Declaration(name: "data", type: QuantumRegister, constructor_args: [10])`.

The compiler maintains these possibilities until an "observation" forces a collapse into a single, classical state. This observation is most powerfully performed by a quantum macro.

## Invoking Measurement: The Macro as a Quantum Gate

A quantum macro is not a simple text-replacement tool. It is a meta-program that operates directly on the superpositional AST. It acts as a measurement apparatus. The moment a macro inspects a property of a node, it collapses the waveform of that node's potential structures, making one of them the definite reality for all subsequent compilation stages.

Let's define a macro, `solidify_type!`, that observes the most probable type of a variable and rewrites its declaration to use that concrete type.

```quantalang
// Macro Definition
macro solidify_type!(variable_name) {
    // 1. Access the AST node associated with 'variable_name' in the current scope.
    let node = ast::find_declaration(variable_name);

    // 2. 'measure_most_probable_type()' is the observation.
    // This collapses the type superposition of the 'node'.
    // The act of calling this function changes the AST.
    let collapsed_type = node.measure_most_probable_type();

    // 3. Mutate the AST. Replace the 'auto' declaration with the new concrete type.
    // The original superposition is now gone forever.
    ast::replace(node, ast::Declaration {
        name: node.name,
        type: collapsed_type,
        value: node.value
    });
}

// Usage
let value = auto(compute_complex_value()); // 'value' is in a superposition of Int, Float, Complex

solidify_type!(value); // The Observer Effect in action.

// After the macro runs, the line above is permanently rewritten in the AST to something like:
// let value: Float64 = compute_complex_value();
// All subsequent code now sees 'value' as a definite Float64.
```

The critical insight is that `measure_most_probable_type()` is not a passive read. It is an active measurement that fundamentally alters the fabric of the program. Before the macro, the program had multiple potential execution paths based on `value`'s type. After the macro, only one path remains.

## Entangling Syntactic Structures: Non-Local AST Transformations

Quantum entanglement allows two particles to be linked in such a way that the state of one instantly affects the other, regardless of distance. QuantaLang macros can create a similar "spooky action at a distance" within the AST, entangling disparate code nodes.

The `entangle_semantics!` macro links two or more AST nodes. A mutation applied to one entangled node is propagated to all others in its entanglement group during a specific compiler phase (e.g., the "decoherence" phase).

```quantalang
macro entangle_semantics!(...nodes) {
    // Create a unique entanglement group ID.
    let group_id = ast::create_entanglement_group();
    
    // Add each node to the group. The AST now contains metadata linking them.
    for node in nodes {
        ast::get_node(node).set_entanglement(group_id);
    }
}

// --- Application Code ---

// A configuration flag
let enable_auditing = auto(true);

// A function deep within another module
function process_transaction(amount) {
    // ... core logic
}

// Entangle the flag with the function definition itself.
entangle_semantics!(enable_auditing, process_transaction);

// Later, another macro or optimization pass observes and mutates the flag.
// This could be in a completely different file.
macro force_secure_mode!() {
    let node = ast::find_declaration("enable_auditing");
    // This mutation is the trigger for the spooky action.
    ast::replace(node, ast::Declaration {
        name: "enable_auditing",
        type: Bool,
        value: true,
        is_const: true // We've made it a compile-time constant.
    });
}

force_secure_mode!();
```

During the compiler's decoherence phase, it processes the entanglement. Since `enable_auditing` was mutated (its `is_const` property changed), the entangled `process_transaction` node is also mutated. The compiler might, for example, automatically inject logging and validation code directly into the function's AST, because it is now part of a "secure" entanglement group.

**Resulting AST for `process_transaction` after decoherence:**

```quantalang
function process_transaction(amount) {
    // Code below was dynamically injected by the compiler
    // due to the entanglement with the mutated 'enable_auditing' flag.
    log_audit_entry(user_id, "process_transaction_start", amount);
    validate_permissions();

    // ... original core logic

    log_audit_entry(user_id, "process_transaction_end", amount);
}
```
The structure of `process_transaction` was altered by a change to a seemingly unrelated variable in a different part of the codebase.

## The Heisenberg Compiler Principle: Precision vs. Momentum

Heisenberg's Uncertainty Principle states that you cannot simultaneously know the exact position and momentum of a particle. This has a direct analogue in quantum macro programming: **The more precisely you observe and constrain the AST's *structure* (position), the more uncertainty you introduce into its *runtime behavior and optimization potential* (momentum).**

Consider a macro designed to enforce a specific function call structure.

```quantalang
macro enforce_call_signature!(function_node, expected_arg_types) {
    let call_sites = ast::find_all_calls_to(function_node);
    
    for site in call_sites {
        // OBSERVATION: We are measuring the types of the arguments at every call site.
        let actual_types = site.get_argument_types();

        // This act of measurement collapses the types to their most probable state.
        if actual_types != expected_arg_types {
            compiler::error("Mismatched call signature for " + function_node.name);
        }
        
        // MUTATION: Because we observed, we now lock in this specific function overload.
        // This prevents the JIT compiler from later using a more optimized,
        // dynamically-generated version of the function for a different type.
        site.lock_overload_resolution();
    }
}

// --- Application ---

function calculate(x, y) {
    // This function is polymorphic and can be JIT-compiled for
    // Ints, Floats, Vectors, etc.
    return x + y;
}

// By observing the call sites, we lock the structure.
enforce_call_signature!(calculate, [Int32, Int32]);

// This call is now valid and locked.
let a = calculate(5, 10);

// This call would now be a compile-time error, even if the JIT
// could have handled it perfectly at runtime. We have sacrificed
// runtime dynamism (momentum) for compile-time structural certainty (position).
let b = calculate(3.14, 2.71); // COMPILE ERROR!
```

By using `enforce_call_signature!`, we gained compile-time safety and a predictable structure. However, we lost the "momentum" of the `calculate` function—its ability to adapt to different types at runtime via JIT compilation. The act of observing the AST to verify its structure irrevocably changed the program's potential runtime behavior. We observed its position so precisely that we destroyed its momentum.