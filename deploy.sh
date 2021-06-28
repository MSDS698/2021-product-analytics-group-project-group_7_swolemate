eb init group-7-swolemate-app --region us-west-2 --platform Docker --key $PEM_NAME 
eb create group-7-swolemate-env --verbose --envvars AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --envvars AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -i t3.2xlarge
