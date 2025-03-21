#!/usr/bin/env python3
from claudine import Agent
import sys
import random
import argparse

def main():
    """
    Example that demonstrates how to track cache-related token metrics
    when using the Claudine Agent.
    """
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run cache token tracking example")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    args = parser.parse_args()
    
    verbose = args.verbose
    
    # Initialize Agent with increased max_tokens and verbose mode based on argument
    agent = Agent(config_params={"temperature": 0.7}, verbose=verbose, max_tokens=4096)
    
    if verbose:
        print("Verbose mode enabled - API calls and token tracking details will be shown")
    
    # Reset the agent to ensure a clean state
    agent.reset()
    
    # Generate a random word to ensure cache creation on each run
    random_words = ["amazing", "beautiful", "colorful", "delightful", "elegant", 
                    "fascinating", "gorgeous", "harmonious", "incredible", "jubilant"]
    random_word = random.choice(random_words)
    
    # Create a large input prompt (over 1,000 tokens)
    prompt = f"""
    I'm studying the following {random_word} flowers and would like you to simply count how many flowers are in this list:
    
    1. Rose - A classic flower known for its beauty and fragrance. Roses come in many colors, each with its own symbolism. They are often used in perfumes, cosmetics, and culinary applications.
    2. Tulip - A spring flower with cup-shaped blooms. Tulips originated in Turkey and became famously valuable during the Dutch "tulip mania" of the 17th century.
    3. Lily - Elegant flowers with distinct petals and strong fragrance. Lilies are often associated with purity and are popular in religious ceremonies and weddings.
    4. Sunflower - Tall flowers with bright yellow petals and dark centers. Sunflowers are known for their heliotropic behavior, where they turn to face the sun throughout the day.
    5. Daisy - Simple flowers with white petals and yellow centers. Daisies symbolize innocence and are among the oldest known flowering plants.
    6. Orchid - Exotic flowers with complex shapes and vibrant colors. There are over 28,000 species of orchids, making them one of the largest flowering plant families.
    7. Carnation - Ruffled flowers available in many colors. Carnations have been cultivated for over 2,000 years and are often used in boutonnieres and corsages.
    8. Chrysanthemum - Fall blooming flowers with many petals. Chrysanthemums are highly valued in Asian cultures and are one of the "Four Gentlemen" in Chinese art.
    9. Daffodil - Spring flowers with trumpet-shaped centers. Daffodils symbolize rebirth and new beginnings, and are often the first flowers to bloom after winter.
    10. Peony - Lush, full flowers with rounded shape. Peonies are known for their exquisite beauty and are considered a symbol of prosperity in many cultures.
    11. Dahlia - Flowers with geometric petal arrangements. Dahlias are native to Mexico and were named after the Swedish botanist Anders Dahl.
    12. Iris - Flowers with distinctive three-part blooms. The iris is named after the Greek goddess of the rainbow and comes in nearly every color.
    13. Poppy - Delicate flowers with paper-like petals. Poppies are known for their medicinal properties and have become a symbol of remembrance for war veterans.
    14. Marigold - Bright orange and yellow flowers. Marigolds are often used in Day of the Dead celebrations and have natural pest-repellent properties.
    15. Lavender - Purple flower spikes with aromatic properties. Lavender is widely used in aromatherapy and is known for its calming effects.
    16. Hydrangea - Large clusters of small flowers. Hydrangea colors can change based on soil pH, with acidic soil producing blue flowers and alkaline soil producing pink flowers.
    17. Snapdragon - Flowers with unique mouth-like shape. When the sides of a snapdragon flower are squeezed, the "mouth" opens and closes, resembling a dragon's jaw.
    18. Violet - Small purple flowers with heart-shaped leaves. Violets have been used in perfumes, candies, and medicinal remedies for centuries.
    19. Zinnia - Bright, round flowers in many colors. Zinnias are named after the German botanist Johann Gottfried Zinn and are known for their long-lasting blooms.
    20. Geranium - Clusters of small flowers with distinctive leaves. Geraniums are popular in window boxes and hanging baskets due to their drought tolerance and continuous blooming.
    21. Amaryllis - Striking trumpet-shaped flowers on tall stalks. Amaryllis bulbs are popular gifts during winter holidays and can be forced to bloom indoors.
    22. Anemone - Delicate flowers with paper-thin petals. Also known as windflowers, anemones come in various colors and bloom in spring and fall.
    23. Aster - Daisy-like flowers that bloom in late summer and fall. The name comes from the Greek word for "star" due to their star-shaped flower heads.
    24. Begonia - Flowers with waxy petals and colorful foliage. Begonias are versatile plants that can be grown as annuals, perennials, or houseplants.
    25. Bleeding Heart - Heart-shaped pink or white flowers on arching stems. The unique shape makes it a favorite in shade gardens.
    26. Bluebell - Bell-shaped blue flowers that often carpet woodland floors in spring. They're protected in many countries due to their cultural significance.
    27. Buttercup - Glossy yellow flowers with a distinctive cup shape. Their shiny petals reflect light, creating the illusion they're glowing.
    28. Calendula - Bright orange and yellow daisy-like flowers. Also known as pot marigold, calendula has medicinal properties and is used in skincare.
    29. Camellia - Flowers with perfect symmetry and glossy leaves. Camellias bloom in winter and early spring when few other plants are flowering.
    30. Clematis - Climbing vines with star-shaped flowers. With over 300 species, clematis comes in various colors and sizes.
    
    Please count the total number of flowers in this list and respond with just the number.
    """
    
    # First call with a large prompt - will create cache
    print("First call (cache creation):")
    response = agent.query(prompt)
    print(f"Claude's response: {response}")
    
    # Get token usage after first call
    token_info = agent.get_tokens()
    print("\nToken Usage After First Call:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    print(f"Cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get cost information
    cost_info = agent.get_token_cost()
    print("\nToken Cost After First Call:")
    print(f"Input cost: ${cost_info.input_cost:.6f}")
    print(f"Output cost: ${cost_info.output_cost:.6f}")
    print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f}")
    print(f"Cache read cost: ${cost_info.cache_read_cost:.6f}")
    print(f"Total cost: ${cost_info.total_cost:.6f}")
    print(f"Cache delta (savings): ${cost_info.cache_delta:.6f}")
    
    # Add a separator
    print("\n" + "="*50 + "\n")
    
    # Second call with the same prompt - should use cache
    print("Second call (cache read):")
    response2 = agent.query(prompt)
    print(f"Claude's response: {response2}")
    
    # Get token usage after second call
    token_info = agent.get_tokens()
    print("\nToken Usage After Second Call:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    print(f"Cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get cost information after second call
    cost_info = agent.get_token_cost()
    print("\nToken Cost After Second Call:")
    print(f"Input cost: ${cost_info.input_cost:.6f}")
    print(f"Output cost: ${cost_info.output_cost:.6f}")
    print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f}")
    print(f"Cache read cost: ${cost_info.cache_read_cost:.6f}")
    print(f"Total cost: ${cost_info.total_cost:.6f}")
    print(f"Cache delta (savings): ${cost_info.cache_delta:.6f}")
    
    # Calculate cost savings from cache
    # Standard cost would include regular input tokens + all cache tokens at standard rate
    standard_cost = (token_info.total_usage.input_tokens + 
                     token_info.total_usage.cache_creation_input_tokens + 
                     token_info.total_usage.cache_read_input_tokens) * (3.0 / 1_000_000)
    
    # Actual cost includes regular input cost + cache creation cost + cache read cost
    actual_cost = cost_info.input_cost + cost_info.cache_creation_cost + cost_info.cache_read_cost
    
    savings = standard_cost - actual_cost
    savings_percentage = (savings / standard_cost) * 100 if standard_cost > 0 else 0
    
    print("\nCache Cost Savings:")
    print(f"Standard cost without cache: ${standard_cost:.6f}")
    print(f"Actual cost with cache: ${actual_cost:.6f}")
    print(f"Cost savings: ${savings:.6f} ({savings_percentage:.2f}%)")
    print(f"Cache delta (from TokenCost): ${cost_info.cache_delta:.6f}")
    
    # Add a visualization of the cache impact
    print("\nCache Impact Visualization:")
    print("Standard cost without cache:")
    standard_bar = "█" * int(standard_cost * 1_000_000)
    print(f"  {standard_bar} ${standard_cost:.6f}")
    
    print("Actual cost with cache:")
    actual_bar = "█" * int(actual_cost * 1_000_000)
    print(f"  {actual_bar} ${actual_cost:.6f}")
    
    print("Savings from cache:")
    savings_bar = "░" * int(cost_info.cache_delta * 1_000_000)
    print(f"  {savings_bar} ${cost_info.cache_delta:.6f}")
    
    # Calculate savings percentage relative to standard cost
    cache_savings_percentage = (cost_info.cache_delta / standard_cost) * 100 if standard_cost > 0 else 0
    print(f"\nCache savings percentage: {cache_savings_percentage:.2f}%")
    
    # Add a third call with a different random word to force cache creation again
    print("\n" + "="*50 + "\n")
    
    # Generate a different random word
    different_random_word = random.choice([w for w in random_words if w != random_word])
    
    # Create a new prompt with the different random word
    different_prompt = prompt.replace(random_word, different_random_word)
    
    print(f"Third call with different random word '{different_random_word}' (new cache creation):")
    response3 = agent.query(different_prompt)
    print(f"Claude's response: {response3}")
    
    # Get token usage after third call
    token_info = agent.get_tokens()
    print("\nToken Usage After Third Call:")
    print(f"Input tokens: {token_info.total_usage.input_tokens}")
    print(f"Output tokens: {token_info.total_usage.output_tokens}")
    print(f"Cache creation input tokens: {token_info.total_usage.cache_creation_input_tokens}")
    print(f"Cache read input tokens: {token_info.total_usage.cache_read_input_tokens}")
    
    # Get cost information after third call
    cost_info = agent.get_token_cost()
    print("\nToken Cost After Third Call:")
    print(f"Input cost: ${cost_info.input_cost:.6f}")
    print(f"Output cost: ${cost_info.output_cost:.6f}")
    print(f"Cache creation cost: ${cost_info.cache_creation_cost:.6f}")
    print(f"Cache read cost: ${cost_info.cache_read_cost:.6f}")
    print(f"Total cost: ${cost_info.total_cost:.6f}")
    print(f"Cache delta (savings): ${cost_info.cache_delta:.6f}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
