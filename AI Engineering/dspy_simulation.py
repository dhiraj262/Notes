import random
import time

# ==============================================================================
# 1. Mock Infrastructure (Simulating the DSPy library structure)
# ==============================================================================

class MockLLM:
    """
    A simulated LLM that behaves probabilistically.
    It performs better if provided with 'demonstrations' (few-shot examples).
    """
    def __init__(self):
        self.history = []

    def __call__(self, prompt):
        self.history.append(prompt)

        # --- Simulation Logic ---
        # The model's "intelligence" depends on the prompt structure.
        # 1. Base accuracy: 20%
        # 2. If it has "Reasoning": +30%
        # 3. If it has "Examples": +40%

        chance = 0.2
        if "Reasoning:" in prompt:
            chance += 0.3
        if "Example Input:" in prompt:
            chance += 0.4

        # Hardcoded logic for the specific "Math" task we will solve
        # The task is: "Double the number and add 2"
        # We simulate the model "figuring it out" based on chance.

        lines = prompt.strip().split('\n')
        last_line = lines[-1]

        # Extract input number from "Input: <num>"
        try:
            input_val = int(last_line.split(":")[-1].strip())
            true_answer = (input_val * 2) + 2
        except:
            return "Error"

        # Roll the dice
        if random.random() < chance:
            return str(true_answer) # Correct
        else:
            return str(true_answer - 1) # Wrong (hallucination)

class Signature:
    """Defines input/output fields."""
    def __init__(self, input_field, output_field):
        self.input_field = input_field
        self.output_field = output_field

class Prediction:
    """A simple container for the result."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Module:
    """A module that calls the LLM."""
    def forward(self, x):
        raise NotImplementedError

# ==============================================================================
# 2. The User's Program (The "Module" we want to optimize)
# ==============================================================================

class ChainOfThought(Module):
    """
    A module that implements a simple CoT strategy.
    It can hold 'demos' (few-shot examples).
    """
    def __init__(self, signature):
        self.signature = signature
        self.demos = [] # Optimized demonstrations will go here
        self.llm = MockLLM()

    def forward(self, input_val):
        # 1. Construct Prompt
        prompt = f"Task: {self.signature.input_field} -> {self.signature.output_field}\n"
        prompt += "Instruction: Double the input and add 2.\n\n"

        # 2. Add Demonstrations (This is what the Optimizer will populate)
        if self.demos:
            prompt += "--- Examples ---\n"
            for d in self.demos:
                prompt += f"Example Input: {d['input']}\n"
                prompt += f"Reasoning: {d['reasoning']}\n"
                prompt += f"Example Answer: {d['answer']}\n\n"
            prompt += "--- End Examples ---\n"

        # 3. Add Current Question
        prompt += f"Input: {input_val}"

        # 4. Call LLM (Simulated)
        # We simulate the LLM generating a reasoning trace + answer
        raw_output = self.llm(prompt)

        # In a real system, we'd parse the output. Here we just return it.
        return Prediction(answer=raw_output, reasoning="Calculated step by step...")

# ==============================================================================
# 3. The Optimizer (The Core of DSPy)
# ==============================================================================

class BootstrapFewShot:
    """
    A simple implementation of the BootstrapFewShot optimizer.
    It improves the module by finding examples where the model *already* succeeds,
    and saving them as 'golden' demonstrations for future use.
    """
    def __init__(self, metric):
        self.metric = metric

    def compile(self, student, trainset):
        print("\n[Optimizer] Starting Compilation (Optimization)...")
        print("[Optimizer] Strategy: Find examples where the model succeeds and 'lock' them.")

        successful_demos = []

        for i, example in enumerate(trainset):
            input_val = example['input']
            target_ans = example['answer']

            # 1. Run the student (currently zero-shot or random)
            print(f"  > Attempting Training Example {i}: Input={input_val}...", end="")
            prediction = student.forward(input_val)

            # 2. Check Metric
            score = self.metric(target_ans, prediction.answer)

            if score:
                print(" SUCCESS! ✅")
                # 3. If successful, save this trace as a demonstration
                # In real DSPy, we save the generated reasoning trace.
                # Here we mock it.
                demo = {
                    "input": input_val,
                    "reasoning": f"First I multiply {input_val} by 2 to get {input_val*2}, then add 2 to get {target_ans}.",
                    "answer": prediction.answer
                }
                successful_demos.append(demo)
            else:
                print(f" FAILED ❌ (Got {prediction.answer}, Expected {target_ans})")

        # 4. Update the student module with the discovered demonstrations
        print(f"\n[Optimizer] Compilation Complete. Found {len(successful_demos)} golden examples.")
        student.demos = successful_demos # "Optimizing" the weights (prompts)
        return student

# ==============================================================================
# 4. Execution
# ==============================================================================

def main():
    # 1. Define the Task
    # Task: f(x) = 2x + 2
    sig = Signature("number", "result")

    # 2. Define the Program (Student)
    program = ChainOfThought(sig)

    # 3. Define Metric
    def exact_match(target, pred):
        return target.strip() == pred.strip()

    # 4. Training Data
    # A small set of examples to "teach" the model
    trainset = [
        {'input': 3, 'answer': '8'},
        {'input': 5, 'answer': '12'},
        {'input': 10, 'answer': '22'},
        {'input': 7, 'answer': '16'},
        {'input': 2, 'answer': '6'},
    ]

    print("--- Phase 1: Zero-Shot Baseline ---")
    # Without examples, our MockLLM has only ~20% accuracy (simulating a hard task)
    # We force the random seed to show failure first
    random.seed(42)

    test_input = 100
    pred = program.forward(test_input)
    print(f"Question: Input={test_input}")
    print(f"Zero-Shot Prediction: {pred.answer} (Expected: 202)")
    # Likely wrong because mock LLM needs 'Examples' to trigger high accuracy

    # 5. Optimize
    optimizer = BootstrapFewShot(metric=exact_match)

    # We reset seed to allow some successes during training
    random.seed(123)
    compiled_program = optimizer.compile(program, trainset)

    print("\n--- Phase 2: Optimized (Compiled) Program ---")
    # Now the program has "learned" (stored demos).
    # The MockLLM sees "Examples" in the prompt and boosts its accuracy to ~90%.

    pred_opt = compiled_program.forward(test_input)
    print(f"Question: Input={test_input}")
    print(f"Optimized Prediction: {pred_opt.answer}")

    if pred_opt.answer == '202':
        print("Result: CORRECT! The optimized prompt worked.")
    else:
        print("Result: Still failing (probabilistic).")

    print("\n[Inspection] The Compiled Prompt now looks like this:")
    print("-" * 40)
    # Peek at the internal 'demos' to show what changed
    print(f"Prompt contains {len(compiled_program.demos)} few-shot examples.")
    print("Example 1:", compiled_program.demos[0])
    print("-" * 40)

if __name__ == "__main__":
    main()
