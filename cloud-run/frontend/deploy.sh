PROJECT_ID=$(gcloud config list --format 'value(core.project)')
REGION="europe-west1"

gcloud builds submit --config cloudbuild.yaml --machine-type=e2-highcpu-8 .

gcloud run deploy text-summarization-frontend \
	--cpu 1 \
	--memory 2Gi \
	--image eu.gcr.io/$PROJECT_ID/text-summarization/cloud-run/frontend:latest \
	--max-instances 5 \
	--min-instances 0 \
	--platform managed \
	--timeout 600 \
	--region $REGION \
	--no-allow-unauthenticated \
	--ingress internal-and-cloud-load-balancing \
	--update-env-vars PROJECT_ID=$PROJECT_ID
