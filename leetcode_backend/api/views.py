from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from django.conf import settings
import requests
from bs4 import BeautifulSoup

# Create your views here.

genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
def solve_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get("title")
        url = data.get("url")
        print(f"Received: {title}, {url}")

        extracted_content = ""
        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors
                soup = BeautifulSoup(response.text, 'lxml')

                # The XPath you provided is /html/body/div[1]/div[2]/div/div/div[4]/div/div/div[4]/div/div[1]
                # Beautiful Soup doesn't directly support XPath like that.
                # You'll need to navigate the DOM tree using its methods.
                # Let's break down the XPath into a series of .find() or .find_all() calls.
                # This assumes a consistent structure. If the structure varies,
                # you might need more robust error handling or different selection strategies.
                try:
                    # Starting from html -> body
                    body = soup.find('body')
                    if body:
                        div1 = body.find_all('div', recursive=False)[0] # div[1]
                        if div1:
                            div2 = div1.find_all('div', recursive=False)[1] # div[2]
                            if div2:
                                div3 = div2.find_all('div', recursive=False)[0] # div
                                if div3:
                                    div4 = div3.find_all('div', recursive=False)[0] # div
                                    if div4:
                                        div5 = div4.find_all('div', recursive=False)[3] # div[4]
                                        if div5:
                                            div6 = div5.find_all('div', recursive=False)[0] # div
                                            if div6:
                                                div7 = div6.find_all('div', recursive=False)[0] # div
                                                if div7:
                                                    div8 = div7.find_all('div', recursive=False)[3] # div[4]
                                                    if div8:
                                                        div9 = div8.find_all('div', recursive=False)[0] # div
                                                        if div9:
                                                            target_div = div9.find_all('div', recursive=False)[0] # div[1]
                                                            if target_div:
                                                                extracted_content = target_div.get_text(separator="\n", strip=True)
                                                            else:
                                                                print("Could not find the final target div[1]")
                                                        else:
                                                            print("Could not find div[0] after div[4]")
                                                    else:
                                                        print("Could not find div[4] after the 7th div")
                                                else:
                                                    print("Could not find the 7th div")
                                            else:
                                                print("Could not find the 6th div")
                                        else:
                                            print("Could not find div[4] after the 5th div")
                                    else:
                                        print("Could not find the 4th div")
                                else:
                                    print("Could not find the 3rd div")
                            else:
                                print("Could not find div[2] after div[1]")
                        else:
                            print("Could not find div[1] after body")
                except IndexError:
                    print("Error navigating through the DOM with the specified path. Index out of range.")
                except Exception as e:
                    print(f"An unexpected error occurred during BeautifulSoup parsing: {e}")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching URL {url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        prompt = f"""
        You're an expert LeetCode mentor. A user is working on the problem titled: "{title}" ({url}).
        Here is the extracted problem description (if available):
        ---
        {extracted_content if extracted_content else "No problem description extracted."}
        ---
        Give them clear, step-by-step guidance to solve it — including edge cases, brute-force thinking, and optimization ideas.
        DO NOT write or suggest actual code.
        Only provide strategic help in natural language.
        """

        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        answer = response.text

        steps = answer.strip().split("\n")
        steps = [step.strip() for step in steps if step.strip()]

        return JsonResponse({"steps": steps})

    return JsonResponse({"error": "Only POST allowed"}, status=400)