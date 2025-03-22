from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys

class Model:
    def __init__(self, model_name):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)

    def predict(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

def main():
    if len(sys.argv) < 3:
        print("Usage: lessllm <model_name> <prompt>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    prompt = sys.argv[2]
    
    model = Model(model_name)
    result = model.predict(prompt)
    print(result)

if __name__ == "__main__":
    main()
