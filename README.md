This project delivers a unified, multi-functional agent application structured as a reusable template for the Google Cloud Platform (GCP). It demonstrates a clear separation of concerns: the Flask API Gateway handles secure, real-time query streaming, while the core reasoning and tool-use logic resides in a managed Vertex AI Agent Engine resource. This setup allows for simple customization across different customer use cases.


Please be sure to update the parameters in main.py based on your project ID and region and use the gcloud run deploy ancestry-chatbot-agent-demo \ --project=<YOUR_PROJECT_ID> \ --source . \ --platform managed \ --region=<YOUR_REGION_HERE> command to deploy to Cloud Run. Also be sure to
update main.py with the correct parameters based off your Agent Engine instance.
