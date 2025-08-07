# List of APIs for User Flow

1. **Upload Resume**
   - **Endpoint:** `POST /api/upload_resume`
   - **Description:** Accepts the user's resume file and stores it for processing.

2. **Extract Resume Data**
   - **Endpoint:** `POST /api/extract_resume`
   - **Description:** Extracts text and structured data from the uploaded resume.

3. **Evaluate Resume**
   - **Endpoint:** `POST /api/evaluate_resume`
   - **Description:** Evaluates the extracted resume data based on predefined criteria.

4. **Get Suggestions**
   - **Endpoint:** `POST /api/get_suggestions`
   - **Description:** Provides suggestions for improving the resume.

5. **Get Recommendations**
   - **Endpoint:** `POST /api/get_recommendations`
   - **Description:** Returns job or skill recommendations based on the resume evaluation.

6. **Fetch Feature Options**
   - **Endpoint:** `GET /api/feature_options`
   - **Description:** Returns available features (evaluation, suggestions, recommendations) for the user to select.

-

*These APIs cover the main interactions after the user lands on the page and