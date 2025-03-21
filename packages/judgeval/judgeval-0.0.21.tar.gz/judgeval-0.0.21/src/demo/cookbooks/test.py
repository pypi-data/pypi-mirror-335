from judgeval.data import Example
from judgeval.data.datasets import EvalDataset
from judgeval.scorers import AnswerRelevancyScorer
from judgeval import JudgmentClient


def create_sample_dataset():
    # Define sample inputs
    inputs = [
        # Highly relevant Q/A pairs
        "Who founded Microsoft?",
        "What is the capital of France?",
        "How does photosynthesis work?",
        "What are the benefits of exercise?",
        "Explain quantum computing in simple terms.",
        
        # Somewhat relevant Q/A pairs
        "What is machine learning?",
        "How do electric cars work?",
        "What causes climate change?",
        "How does the human digestive system function?",
        "What is blockchain technology?",
        
        # Minimally relevant Q/A pairs
        "What are the main programming languages?",
        "How do I bake a chocolate cake?",
        "What is the history of the Roman Empire?",
        "How do vaccines work?",
        "What are black holes?",
        
        # Not relevant Q/A pairs
        "What is the best smartphone to buy?",
        "How tall is Mount Everest?",
        "Who wrote Romeo and Juliet?",
        "What is the population of Tokyo?",
        "How do I change a flat tire?"
    ]
    
    # Define corresponding outputs
    actual_outputs = [
        # Highly relevant answers
        "Bill Gates and Paul Allen founded Microsoft in 1975.",
        "The capital of France is Paris, known for the Eiffel Tower and Louvre Museum.",
        "Photosynthesis is the process where plants convert sunlight, water, and carbon dioxide into glucose and oxygen.",
        "Regular exercise improves cardiovascular health, builds muscle strength, reduces stress, and helps maintain a healthy weight.",
        "Quantum computing uses quantum bits or qubits that can exist in multiple states simultaneously, allowing for potentially faster computation of certain problems compared to classical computers.",
        
        # Somewhat relevant answers (partial or tangential information)
        "Machine learning involves statistical techniques, but it's primarily about natural language processing and computer vision applications in modern businesses.",
        "Electric cars use batteries, though the most important aspect is their impact on reducing traffic congestion in urban areas.",
        "Climate change is related to weather patterns, but it's mainly caused by volcanic eruptions and natural planetary cycles.",
        "The digestive system breaks down food, but the most interesting part is how it connects to brain function and mental health.",
        "Blockchain is a distributed ledger technology, though its primary purpose is to replace traditional banking systems entirely.",
        
        # Minimally relevant answers (mostly off-topic but with slight connection)
        "Programming languages include Python and JavaScript, but the real question is whether AI will replace programmers in the next decade.",
        "Chocolate cakes require flour and sugar, but I'd recommend focusing on gluten-free alternatives since they're healthier.",
        "The Roman Empire lasted for centuries, but modern Italy's political system is more relevant to understand today's European politics.",
        "Vaccines stimulate immune responses, but the pharmaceutical industry's profit motives are what you should really be concerned about.",
        "Black holes are regions of spacetime, but the conspiracy theories about what NASA isn't telling us are far more interesting.",
        
        # Not relevant answers (completely off-topic)
        "The migration patterns of monarch butterflies are fascinating examples of evolutionary adaptation.",
        "The Great Wall of China was built over multiple dynasties and stretches over 13,000 miles.",
        "Photosynthesis is how plants convert sunlight into energy, producing oxygen as a byproduct.",
        "The human genome contains approximately 3 billion base pairs of DNA.",
        "The Pythagorean theorem states that in a right-angled triangle, the square of the hypotenuse equals the sum of squares of the other two sides."
    ]

    # Create Example objects from inputs and outputs
    examples = []
    for i in range(len(inputs)):
        examples.append(Example(
            input=inputs[i],
            actual_output=actual_outputs[i]
        ))

    return EvalDataset(examples=examples)


def save_dataset(client, dataset, alias):
    """Save the dataset to Judgment API with the given alias"""
    client.push_dataset(alias=alias, dataset=dataset)
    print(f"Dataset saved with alias: {alias}")


def run_evaluation(client, dataset_alias, model="gpt-4o", project_name="jnpr_mist_demo_project", eval_run_name="jnpr_demo_eval_run"):
    """Pull a dataset and run an evaluation on it"""
    # Pull the dataset from Judgment API
    eval_dataset = client.pull_dataset(alias=dataset_alias)
    
    # Run the evaluation
    results = client.evaluate_dataset(
        dataset=eval_dataset,
        scorers=[AnswerRelevancyScorer(threshold=0.8)],
        model=model,
        eval_run_name=eval_run_name,
        project_name=project_name,
    )
    
    return results


def run_assertion_test(client, dataset_alias, model="gpt-4o", project_name="jnpr_mist_demo_project", eval_run_name="jnpr_demo_assertion_run"):
    """Pull a dataset and run assertion tests on its examples"""
    # Pull the dataset from Judgment API
    eval_dataset = client.pull_dataset(alias=dataset_alias)
    
    # Extract examples from the dataset
    examples = eval_dataset.examples
    
    # Run assertion tests on each example
    # Run assertion test on all examples at once
    client.assert_test(
        examples=examples,
        scorers=[AnswerRelevancyScorer(threshold=0.8)],
        model=model,
        project_name=project_name,
        eval_run_name=eval_run_name
    )
    

def main():
    client = JudgmentClient()
    
    # Uncomment to create and save a new dataset
    # dataset = create_sample_dataset()
    # save_dataset(client, dataset, "jnpr_demo_dataset")
    
    # # Run evaluation on the saved dataset
    # results = run_evaluation(
    #     client, 
    #     dataset_alias="jnpr_demo_dataset",
    #     model="gpt-4o",
    #     project_name="jnpr_mist_demo_project",
    #     eval_run_name="jnpr_demo_eval"
    # )
    
    # Run assertion test on the saved dataset
    results = run_assertion_test(
        client, 
        dataset_alias="jnpr_demo_dataset",
        model="gpt-4o",
        project_name="jnpr_mist_demo_project",
        eval_run_name="jnpr_demo_assertion"
    )
    return results


if __name__ == "__main__":
    results = main()
    print(results)
