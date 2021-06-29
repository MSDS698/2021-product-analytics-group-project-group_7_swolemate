eb init wkxa1 --region us-west-2 --platform Docker --key $PEM_NAME 
eb create wkxe1 --verbose --envvars AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --envvars AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -i m4.2xlarge --timeout 300
