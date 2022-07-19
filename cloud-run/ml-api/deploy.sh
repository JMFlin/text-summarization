PROJECT_ID=$(gcloud config list --format 'value(core.project)')
USER_EMAIL=$(gcloud config list account --format "value(core.account)")
TOKEN=$(gcloud auth print-identity-token)
REGION="europe-west1"

gcloud builds submit --config cloudbuild.yaml --machine-type=e2-highcpu-8 .

gcloud run deploy text-summarization-ml-api \
	--cpu 1 \
	--memory 2Gi \
	--image eu.gcr.io/$PROJECT_ID/text-summarization/cloud-run/model-api:latest \
	--concurrency 1 \
	--ingress all \
	--no-allow-unauthenticated \
	--max-instances 5 \
	--min-instances 0 \
	--platform managed \
	--timeout 600 \
	--region $REGION \
	--port 5000 \
	--update-env-vars PROJECT_ID=$PROJECT_ID


#gcloud run services add-iam-policy-binding text-summarization-ml-api \
#  --member="user:${USER_EMAIL}" \
#  --role='roles/run.invoker' \
#  --region=$REGION
#
#curl -H "Authorization: Bearer $TOKEN" \
#    https://text-summarization-ml-api-axswvbmypa-ew.a.run.app/api/health_check
