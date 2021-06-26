eb init testwkx --region us-west-2 --platform Docker --key $PEM_NAME 
eb create testenvwkx --verbose --envvars AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --envvars AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -i t3.2xlarge
