# 🍽️ What's for Dinner? Recipe Card Generator

This Python script uses the **Google Gemini API**'s **function calling** capability to generate a single dinner recipe based on a list of core ingredients provided via the command line.

The script simulates using a search tool to find a recipe and then sends the result back to the Gemini model, which formats the final output as a professional recipe card image (text representation).

-----

## ✨ Features

* **Intelligent Recipe Generation:** Uses the Gemini model to creatively generate a full recipe from a list of ingredients.
* **Nutritional Estimates:** The model is instructed to **estimate and include nutritional information** (Calories, Protein, Fat, Carbs) per serving based on the recipe and ingredients.
* **Function Calling Simulation:** Demonstrates the use of a mock `Google Search` function to fetch real-world data (a recipe snippet).
* **Reliable Tool Use:** Uses robust configuration (`function_calling_config`) to ensure the model reliably calls the mock search function.
* **Command-Line Interface (CLI):** Easily input your available ingredients using the `--ingredients` flag.
* **Professional Formatting:** Outputs the recipe as a clean, text-based recipe card.
* **Error Handling:** Includes checks for missing ingredients, a **check for empty/filtered API responses**, and graceful fallback to a mock response if the API key is not configured.

-----

## 🚀 Setup and Installation

### 1. Prerequisites

You must have Python installed (3.8+ recommended).

### 2. Install Dependencies

The script relies on the Google GenAI SDK for Python and standard libraries (`os`, `json`, `argparse`).

```bash
pip install google-genai
````

### 3\. Set Your API Key

The Gemini model requires an API key. You must set this key as an environment variable named `GEMINI_API_KEY`.

**Linux/macOS:**

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

**Windows (Command Prompt):**

```bash
set GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

*(Note: If the key is not set, the script will default to generating a mock, placeholder recipe.)*

-----

## 🍴 Usage

Run the script from your terminal, passing your available ingredients as a comma-separated string to the `--ingredients` argument. **Be sure to wrap the entire list in double quotes (`" "`) to prevent shell errors.**

### Example Command

This example uses core ingredients:

```bash
python whats-for-dinner.py --ingredients "turkey kielbasa, penne pasta, jarred marinara sauce, shredded mozzarella, instant potatoes"
```

### Example Output (API Success)

The script output will be formatted as a recipe card, now including a nutritional estimate section:

```
--- Input Ingredients: ['turkey kielbasa', 'penne pasta', 'jarred marinara sauce', 'shredded mozzarella', 'instant potatoes'] ---

[STEP 1: Calling Gemini to initiate search and tool use...]
--- TOOL CALLING: Searching for: simple dinner recipe with turkey kielbasa, penne pasta, jarred marinara sauce, shredded mozzarella, instant potatoes ---

[STEP 2: Sending tool results back to Gemini for final response generation...]

================================================================================
GENERATED RECIPE CARD:
================================================================================
**[RECIPE CARD IMAGE: WHAT'S FOR DINNER?]**

**CORE INGREDIENTS**
turkey kielbasa, penne pasta, jarred marinara sauce, shredded mozzarella, instant potatoes

***

**RECIPE: ONE-POT KIELBASA & CHEESY MARINARA PASTA**
*(Time: 30 Min | Serves 4)*

**Description:**
A simple, hearty weeknight meal that combines savory turkey kielbasa, tomato sauce, and pasta, all cooked in one pot for minimal cleanup.
... (Rest of the recipe steps)

***

**NUTRITIONAL INFORMATION (Estimated Per Serving)**
* Calories: 580 kcal
* Protein: 35g
* Fat: 22g
* Carbs: 65g
================================================================================
```

### Error Handling Example

If the script runs but the model's final response is empty (e.g., due to safety filtering), the new error check will print a helpful message instead of just "None."

```
================================================================================
GENERATED RECIPE CARD:
================================================================================
ERROR: Recipe generation failed. The model returned no text.
This can happen due to safety filtering. Please check the prompt or try again.
================================================================================
```

-----

## 🛠️ How It Works (Code Breakdown)

1.  **`argparse`:** The script uses `argparse` to receive the ingredients string, cleans it, and validates that ingredients were actually provided.
2.  **`Google Search` (Mock Tool):** This function acts as the **tool** for the Gemini model, providing a hardcoded mock recipe snippet.
3.  **`generate_recipe_card` (Main Logic):**
      * It prepares a detailed prompt, now explicitly asking for **estimated nutritional information**.
      * It uses `tool_config_force` with `function_calling_config(mode='ANY')` to make the **First API Call**, ensuring the model calls the mock `Google Search` function reliably.
      * The script executes the Python `Google Search` function and captures the mock JSON result.
      * It makes the **Second API Call**, sending the original prompt *plus* the mock result back to Gemini.
      * Gemini uses the snippet to generate the final, fully formatted recipe card, including the nutritional estimates.
      * The final output block includes a check: `if response.text:` to handle cases where the model returns an empty body.

<!-- end list -->

```
```