gcloud functions deploy text-summarization \
	--entry-point summarize_text \
	--runtime python39 \
	--trigger-http \
	--region europe-west1 \
	--timeout 60 \
	--allow-unauthenticated \
	--env-vars-file .env.yaml #\
	#--ingress-settings internal-only
