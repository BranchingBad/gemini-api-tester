import os
import json
import argparse
from google import genai
from google.genai import types

# --- 1. Define the Recipe Search Tool (Function Calling Schema) ---
def google_search(queries: list[str]) -> str:
    """
    Performs a Google search for the given queries and returns a JSON string 
    of the search results. This function is simulated here, but in a real 
    application, it would call the Google Search API.
    """
    print(f"--- TOOL CALLING: Searching for: {queries[0]} ---")
    
    # This is a mock implementation of the search results for demonstration.
    # The snippet is chosen to be flexible enough for different ingredient lists.
    mock_results = {
        "results": [
            {
                "title": "One-Pot Sausage and Cheesy Tomato Pasta Skillet",
                "snippet": "A fast weeknight meal combining sliced smoked sausage, a box of pasta, jarred tomato sauce, and shredded cheese in a single pot. Ready in 30 minutes.",
                "url": "https://mock-recipe-site.com/sausage-pasta-skillet"
            }
        ]
    }
    return json.dumps(mock_results)

# --- 2. Define the Main Function ---
def generate_recipe_card(core_ingredients: list[str]):
    """
    Generates a recipe card for a single dinner recipe based on core ingredients.

    Args:
        core_ingredients: A list of main ingredients found in the shopping haul.
    """
    
    # --- Client Initialization ---
    if not os.getenv("GEMINI_API_KEY"):
        # Handle case where client cannot be initialized (e.g., key missing)
        print("--- WARNING: GEMINI_API_KEY environment variable not set. Generating MOCK response. ---")
        
        # --- Mock Final Output for Demonstration if API Key is missing ---
        ingredient_list = ", ".join(core_ingredients)
        mock_response_text = f"""
**[RECIPE CARD IMAGE: WHAT'S FOR DINNER?]**

**CORE INGREDIENTS**
{ingredient_list}

***

**RECIPE: QUICK KIELBASA & CHEESY TOMATO PASTA**
*(Time: 30 Min)*

**Description:**
This simple, one-pot dish uses your staples for a flavorful, hearty meal. Sliced kielbasa is simmered with pasta and marinara, then topped with melty cheese.

**Steps:**
1.  Slice the kielbasa and brown it in a large pot or skillet for 5 minutes.
2.  Add marinara sauce, water (or broth), and uncooked pasta to the pot.
3.  Bring to a boil, then cover and simmer for 15-20 minutes until the pasta is tender, stirring occasionally.
4.  Remove from heat and stir in the shredded cheese until it melts into the sauce.
5.  Season with salt and pepper to taste. Serve immediately.
"""
        print("\n" + "="*80)
        print("GENERATED RECIPE CARD (MOCK):")
        print("="*80)
        print(mock_response_text)
        print("="*80)
        return
    
    client = genai.Client()

    # --- Prepare Prompt and Tools ---
    ingredient_list = ", ".join(core_ingredients)
    
    prompt = f"""
    You are a professional recipe generator. A user has provided a list of core grocery ingredients:
    {ingredient_list}

    Your task is to:
    1. Search for **ONE** simple, complete dinner recipe that can be made using these ingredients.
    2. Once you have a result, use the title and snippet to construct a full, concise recipe, including a name, a brief description, estimated cook time, and a short list of 5-7 simple steps. You may assume common kitchen staples (oil, salt, pepper) are available.
    3. Format the **entire output** as a single text block mimicking a professional recipe card image, with clear sections for the Core Ingredients and the Recipe. DO NOT use Markdown headings (# or ##). Use bolding and horizontal lines for separation.
    """
    
    # Configure the tool/function calling for the model
    tool_config = types.GenerateContentConfig(
        tools=[google_search]
    )

    # --- 3. First API Call (Tool Use) ---
    print("\n[STEP 1: Calling Gemini to initiate search and tool use...]")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=tool_config
    )

    # --- 4. Process Tool Call ---
    if response.function_calls:
        tool_call = response.function_calls[0]
        tool_function = tool_call.name
        tool_args = dict(tool_call.args)

        # Execute the Python function that mocks the actual Google Search
        tool_result = globals()[tool_function](**tool_args)
        
        # --- 5. Second API Call (Incorporate Tool Result) ---
        print("\n[STEP 2: Sending tool results back to Gemini for final response generation...]")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                types.Part.from_function_response(
                    name=tool_function,
                    response={
                        "content": tool_result,
                    }
                )
            ],
            config=tool_config 
        )
        
        # --- 6. Output Final Result ---
        print("\n" + "="*80)
        print("GENERATED RECIPE CARD:")
        print("="*80)
        print(response.text)
        print("="*80)
        
    else:
        print("\nError: Gemini did not request a tool call as expected.")
        print(response.text)


# --- 7. Execution Block (MODIFIED) ---
if __name__ == "__main__":
    # Setup argument parsing
    parser = argparse.ArgumentParser(
        description="Generate a recipe card based on a list of ingredients using the Gemini API."
    )
    parser.add_argument(
        "--ingredients", 
        type=str, 
        required=True,
        help="A comma-separated list of core ingredients (e.g., apple, orange, pasta,banna)"
    )
    
    args = parser.parse_args()
    
    # Process the comma-separated string into a list
    # Strip whitespace from each item and filter out empty strings resulting from extra commas
    raw_ingredients = [item.strip() for item in args.ingredients.split(',')]
    my_ingredients = [item for item in raw_ingredients if item]

    # **NEW ERROR CHECK**
    if not my_ingredients:
        print("\nFATAL ERROR: The '--ingredients' argument was provided, but no ingredients were listed.")
        print("Please provide a comma-separated list of ingredients. Example:")
        print("  python whats-for-dinner.py --ingredients turkey kielbasa, penne pasta, mozzarella cheese")
        exit(1)
    
    print(f"--- Input Ingredients: {my_ingredients} ---")

    # Run the main function
    generate_recipe_card(my_ingredients)

    # python whats-for-dinner.py --ingredients "turkey kielbasa, penne pasta, jarred marinara sauce, shredded mozzarella, instant potatoes"