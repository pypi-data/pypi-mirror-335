import destigmatizer

from destigmatizer.tests.utils import get_api_key_for_testing, get_model_for_testing, setup_test_argument_parser, parse_test_args

def test_drug_classifier(api_key=None, model=None, client_type=None):
    """
    Test the drug classification functionality.
    
    Args:
        api_key (str, optional): API key for the LLM service
        model (str, optional): Model name to use for testing
        client_type (str, optional): Type of client ("openai", "together", "claude", etc.)
    """
    # Initialize client
    try:
        client = destigmatizer.initialize(api_key=api_key, client_type=client_type)
        print("✓ Client initialization successful")
        
        
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    # Test posts for classification
    test_posts = {
        "drug_post_1": "I'm so high right now, smoking the best weed ever",
        "drug_post_2": "The dope is phenomenal and cheap (3g's for $100)",
        "non_drug_post_1": "I'm feeling really down today, need someone to talk to",
        "non_drug_post_2": "Recently I took a psychological exam for work."
    }
    
    # Print model information
    print(f"Using model: {model or 'default'} with client type: {client_type}")
    
    # Test drug classification
    print("\nTesting drug classification...")
    for post_type, post in test_posts.items():
        print(f"\nTesting on: {post}")
        result = destigmatizer.classify_if_drug(
            post,
            client=client,
            model=model
        )
        print(f"{post_type}: {result}")

if __name__ == "__main__":
    # Set up argument parser
    parser = setup_test_argument_parser('Test drug classification functionality')
    
    # Parse arguments and get API key, model, and client type
    api_key, model, client_type = parse_test_args(parser)
    
    # Run the test
    test_drug_classifier(api_key=api_key, model=model, client_type=client_type)
