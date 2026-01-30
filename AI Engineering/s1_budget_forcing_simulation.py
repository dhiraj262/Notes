import time

class MockLLM:
    """
    A mock LLM that simulates the behavior of a reasoning model.
    It tends to stop early unless forced to continue.
    """
    def __init__(self):
        self.max_capacity = 3  # The model effectively has 3 "chunks" of reasoning in it

    def generate(self, prompt: str) -> str:
        """
        Simulates generation.
        If it sees 'Wait', it extends its reasoning.
        """
        # Analyze the prompt to decide what to output
        wait_counts = prompt.count("Wait")

        # Base reasoning step
        if wait_counts == 0:
            return " The answer seems to be 5. <|im_end|>"

        # Extended reasoning (triggered by 'Wait')
        elif wait_counts == 1:
            return " Hold on, let me double check. 5 + 5 is 10, but the question asked for... <|im_end|>"

        elif wait_counts == 2:
            return " Ah, I missed the multiplier. It's 5 * 2. So the result is 10. <|im_end|>"

        else:
            return " Therefore, the final answer is 10. <|im_end|>"

def budget_forcing_simulation():
    print("--- s1: Budget Forcing Simulation ---")
    print("Goal: Force the model to think longer than it wants to.\n")

    model = MockLLM()

    # Initial Prompt
    prompt = "<|im_start|>user\nWhat is result?\n<|im_end|>\n<|im_start|>think"
    print(f"[Initial Prompt]: {prompt}")

    # Parameters
    MIN_THINKING_STEPS = 3
    STOP_TOKEN = "<|im_end|>"
    IGNORE_STR = "Wait"

    current_steps = 0
    final_output = ""

    # Generation Loop
    while current_steps < MIN_THINKING_STEPS:
        print(f"\n--- Step {current_steps + 1} ---")

        # 1. Generate
        output = model.generate(prompt)
        print(f"[Model Output]: {output}")

        # 2. Check for stop token
        if STOP_TOKEN in output:
            # 3. Decision: Do we accept the stop?
            if current_steps < MIN_THINKING_STEPS - 1:
                print(f"[Budget Logic]: Budget not met ({current_steps+1}/{MIN_THINKING_STEPS}). Intercepting STOP.")

                # Remove the stop token from the output effectively (in a real generic loop we might slice it)
                # Here we just append the text content + the "Wait" command
                clean_output = output.replace(STOP_TOKEN, "")

                # UPDATE THE PROMPT: This is the core 'Budget Forcing' mechanism
                # We feed the model's own output back to it, plus "Wait"
                prompt += clean_output + IGNORE_STR

                print(f"[Action]: Appended '{IGNORE_STR}' to prompt.")
                # print(f"[Current Prompt Context]: ...{prompt[-50:]}")
            else:
                print(f"[Budget Logic]: Budget met. allowing STOP.")
                final_output = output.replace(STOP_TOKEN, "")
                break

        current_steps += 1
        time.sleep(1) # Pause for effect

    print("\n--- Final Result ---")
    print(f"Reasoning Trace:\n{prompt.replace('<|im_start|>user\\nWhat is result?\\n<|im_end|>\\n<|im_start|>think', '') + final_output}")

if __name__ == "__main__":
    budget_forcing_simulation()
