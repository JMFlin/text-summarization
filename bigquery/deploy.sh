PROJECT_ID=$(gcloud config list --format 'value(core.project)')

bq rm -f -t $PROJECT_ID:text_summarization.summarized

bq --location=EU mk -d \
 $PROJECT_ID:text_summarization

bq mk --table \
  --schema schema.json \
$PROJECT_ID:text_summarization.summarized
