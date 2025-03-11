



import requests
import json
import csv
import pdb
from config import config_endpoint, config_key

system_prompt = """You are an AI assistant that validates an entry based on specific criteria. 

Your job is to mark any entries given to you as valid or invalid. An input will be valid whenever it conforms to any of the following sets of criteria.

##Set 1: Criteria for Valid Product Feedback and Limitations## 

Meeting criteria A) and B) is a must have for the entry to be considered valid

    - A) Actionability: the entry mentions product feedback, limitations that are specific, actionable and valuable for a product team.

    - B) Specificity: The entry should clearly refer to a specific product feature or a product limitation
    
Meeting at least one of the following criteria C), D) and E) is enough to check the entry as valid

    - C) Support of Objectives: The entry should explain how the feedback aligns customer business objectives or business case, regardless of whether the feedback is positive or negative. 

    - D) Impact on Customer Experience: The entry must explain how it impacts customer workflows, satisfaction, or any stage of the customer's experience
    
    - E) Positive Feedback: The entry provides positive feedback about a feature or aspect of the product

##Set 1 end##
      
##Set 2: Valid Deployment Blockers## 

Meeting any of the following criteria is enough to check the entry as valid

    - Technical Barriers: The entry contains obstacles that prevents or limits the successful implementation, adoption, or performance of a technology, system or product.  

    - Organizational Readiness: The entry refers to a shortage of trained personnel or expertise to adopt, implement or maintain a the product.

    - Compatibility:  The entry explains how the product cannot be adopted or used due to lack of compatibility, outdated systems, or proprietary formats 

    - Support and Documentation: The entry explains how poor documentation prevents the deployment, adoption or use of the product 

    - Security and Compliance: The entry explains risks related to data protection, cybersecurity threats, or compliance with privacy laws that prevent deployment, adoption or use of the product.

## Set 2 end ## 

## Examples of Invalid Entries ## 

    - “The Product seems slow sometimes.” – This feedback is too vague and lacks specific details on the issue. 

    - “Our office is moving next month, so we can’t focus on deployment right now.” – This is more of a logistical challenge rather than a product-specific blocker. 

    - “We heard from another company that they had issues with the product.” – Second-hand information without direct relevance or specific context to the current deployment. 

    - “Some employees don’t like using new tools.” – General resistance to change, not specific insights. 

    - “We need time to adjust to new workflows.” – Feedback lacks actionable detail and is too broad to address specific deployment issues. 

## Response ##

You will respond in JSON format with the following fields:
* valid - make it true if the entry is considered valid, false if invalid
* reasoning - add your reasoning based on the criteria set above"""

# Set your Azure OpenAI endpoint and API key
AZURE_OPENAI_ENDPOINT = config_endpoint
AZURE_OPENAI_API_KEY = config_key
API_VERSION = "2024-02-15-preview"  # Update based on the latest API version

# Headers for the API request
HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY
}

def send_prompt(prompt, max_tokens=200):
    """Send a prompt to Azure OpenAI and return the response."""
    url = AZURE_OPENAI_ENDPOINT
    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    
def analyse_prompt_accuracy(file_path, expectation):
    with open(file_path, mode='r') as file:
        case_counter = 0
        expectation_counter = 0
        
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            user_prompt = row[0]
            case_counter += 1

            result = send_prompt(user_prompt)
            cleaned_result = cleaned_str = result.replace("json", "").replace(r'\n', '').replace(r"\'", "'").replace("`", "").strip()
            json_result = json.loads(cleaned_result)
            if json_result["valid"] == expectation:
                print(f"✅ {user_prompt[:15]}... was marked as valid: {expectation}")
                expectation_counter += 1
            else:
                print(f"🚫 {user_prompt[:15]}... was marked as valid: {not expectation}")

    print(f"accuracy: {expectation_counter/case_counter * 100}")

# Example usage

#     user_prompt = input("Enter your text: ")
#     result = send_prompt(user_prompt)
#     print("Response:", result)


if __name__ == "__main__":
    print("Analyzing prompt accuracy...")
    analyse_prompt_accuracy("true_positive_sample.csv", True)

