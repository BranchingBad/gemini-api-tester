import os
import json
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
    # In a real setup, you would use a search tool like the official Google Search API.
    mock_results = {
        "results": [
            {
                "title": "One-Pot Kielbasa and Veggie Pasta",
                "snippet": "A fast weeknight meal combining sliced smoked sausage, a box of pasta, jarred tomato sauce, and shredded cheese in a single pot. Ready in 30 minutes.",
                "url": "https://mock-recipe-site.com/kielbasa-pasta"
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
    # Ensure your GEMINI_API_KEY is set in your environment variables
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set.")
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


# --- 7. Execution Block ---
if __name__ == "__main__":
    # Example ingredients from the user's initial haul
    my_ingredients = [
        "Turkey Kielbasa", 
        "Penne Pasta", 
        "Jarred Marinara Sauce", 
        "Shredded Mozzarella Cheese", core_ingredients 
        "Instant Potatoes"
    ]
    
    generate_recipe_card(my_ingredients)