import os
import json
import argparse
from google import genai
from google.genai import types

# --- 1. Define the Recipe Search Tool (Function Calling Schema) ---
def google_search(queries: list[str]) -> str:
    """
    MOCK TOOL: Performs a Google search for the given queries and returns a JSON 
    string of mock search results. This function simulates finding a recipe title 
    and snippet for the Gemini model to use.
    """
    print(f"--- TOOL CALLING: Searching for: {queries[0]} ---")
    
    # This is a mock implementation for demonstration.
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
    Generates a recipe card for a single dinner recipe based on core ingredients 
    using the Gemini API and function calling.
    """
    
    # --- Client Initialization and Fallback ---
    if not os.getenv("GEMINI_API_KEY"):
        print("--- WARNING: GEMINI_API_KEY environment variable not set. Generating MOCK response. ---")
        
        # Mock Final Output for Demonstration if API Key is missing
        ingredient_list = ", ".join(core_ingredients)
        mock_response_text = f"""
**[RECIPE CARD IMAGE: WHAT'S FOR DINNER?]**

**CORE INGREDIENTS**
{ingredient_list}

***

**RECIPE: QUICK KIELBASA & CHEESY TOMATO PASTA (MOCK)**
*(Time: 30 Min)*

**Description:**
This is a mock recipe generated because the API key was missing. It mimics a simple, one-pot dish using staples.

**Steps:**
1. Slice the kielbasa and brown it in a large pot.
2. Add marinara sauce, water, and uncooked pasta. Simmer until tender.
3. Stir in shredded cheese until it melts.
4. Serve immediately.

***

**NUTRITIONAL INFORMATION (Estimated Per Serving)**
* Calories: 550 kcal
* Protein: 30g
* Fat: 25g
* Carbs: 55g
"""
        print("\n" + "="*80)
        print("GENERATED RECIPE CARD (MOCK):")
        print("="*80)
        print(mock_response_text)
        print("="*80)
        return
    
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return

    # --- Prepare Prompt ---
    ingredient_list = ", ".join(core_ingredients)
    
    prompt = f"""
    You are a professional recipe generator. A user has provided a list of core grocery ingredients:
    {ingredient_list}

    Your task is to:
    1. Search for **ONE** simple, complete dinner recipe that can be made using these ingredients.
    2. Once you have a result, use the title and snippet to construct a full, concise recipe, including a name, a brief description, estimated cook time, and a short list of 5-7 simple steps. You may assume common kitchen staples (oil, salt, pepper) are available.
    3. **ESTIMATE** and include a 'NUTRITIONAL INFORMATION' section at the end of the recipe card. Provide estimated values for Calories (kcal), Protein (g), Fat (g), and Carbs (g) per serving.
    4. Format the **entire output** as a single text block mimicking a professional recipe card image, with clear sections for the Core Ingredients, the Recipe, and the Nutritional Information. DO NOT use Markdown headings (# or ##). Use bolding and horizontal lines for separation.
    """
    
    # --- Robust Tool Configuration (Fixes ToolChoice Error) ---
    # Configuration for the first call, forcing tool use with 'ANY' string
    tool_config_force = types.GenerateContentConfig(
        tools=[google_search],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode='ANY' 
            )
        )
    )

    # Configuration for the second call (standard config)
    tool_config = types.GenerateContentConfig(
        tools=[google_search]
    )

    # --- 3. First API Call (Tool Use) ---
    print("\n[STEP 1: Calling Gemini to initiate search and tool use...]")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=tool_config_force 
    )

    # --- 4. Process Tool Call ---
    if response.function_calls:
        tool_call = response.function_calls[0]
        tool_function = tool_call.name
        tool_args = dict(tool_call.args)

        # Execute the Python function that mocks the actual Google Search
        # The mock always returns the same result for consistency
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
        
        # --- 6. Output Final Result (Added empty response check) ---
        print("\n" + "="*80)
        print("GENERATED RECIPE CARD:")
        print("="*80)
        
        if response.text:
            print(response.text)
        else:
            print("ERROR: Recipe generation failed. The model returned no text.")
            print("This can happen due to safety filtering. Please check the prompt or try again.")
            
        print("="*80)
        
    else:
        print("\nError: Gemini did not request a tool call as expected. The model may have attempted to answer directly or failed internally.")
        print(f"Debug output: {response.text}")


# --- 7. Execution Block ---
if __name__ == "__main__":
    # Setup argument parsing
    parser = argparse.ArgumentParser(
        description="Generate a recipe card based on a list of ingredients using the Gemini API."
    )
    parser.add_argument(
        "--ingredients", 
        type=str, 
        required=True,
        help='A comma-separated list of core ingredients (e.g., "chicken, pasta, cheese")'
    )
    
    args = parser.parse_args()
    
    # Process the comma-separated string into a list
    raw_ingredients = [item.strip() for item in args.ingredients.split(',')]
    my_ingredients = [item for item in raw_ingredients if item]

    # FATAL ERROR CHECK
    if not my_ingredients:
        print("\nFATAL ERROR: The '--ingredients' argument was provided, but no ingredients were listed.")
        print("Please provide a comma-separated list of ingredients. Example:")
        print('  python whats-for-dinner.py --ingredients "turkey kielbasa, penne pasta, mozzarella cheese"')
        exit(1)
    
    print(f"--- Input Ingredients: {my_ingredients} ---")

    # Run the main function
    generate_recipe_card(my_ingredients)