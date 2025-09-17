# Project Rules

1.  When a search is initiated from the frontend search screen, it will trigger an API call. This call will initiate a web crawling process based on the search query. The crawled information will then be cross-validated for fact-checking using both Naver and Kakao APIs. Finally, the validated information will be summarized by the Gemini API and presented to the user.

2.  The summarized information must be stored in a JSON file format.




