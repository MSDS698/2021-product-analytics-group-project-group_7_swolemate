Tutorial
==============
Below are the steps needed to run the following code locally: 

- Git pull from the GitHub repository
- Run the dockercompose.yml in the swolemate_flask directory
- Go to localhost:5000 to run the site from the docker container

There may be errors in the above process. If so, then follow the below
method instead to run the site and upload a video locally: 

1) Go into the code directory 

2) Run "docker build -t app_img ."
3) Run "docker run -e AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID -e 
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -it --rm -p 80:5000 app_img"

4) Go into the site using localhost and click "Register" to register an account and "Login"

5) After Login, automatically redirect to the Upload Page and upload a video with a dropdown of the given exercise and submit

6) After submitting, if there is an error, manually redirect to "localhost/userpage", otherwise it will automatically redirect

To get the flask website running on Elastic Beanstalk

- run 'sh deploy.sh' --> input your user pem file, and both AWS secret keys
- go to elastic beanstalk under environments, find the available environment and click the link to the website
