Tutorial
==============
Below are the steps needed to run the following code locally: 

1) Run docker-compose up

2) Go to localhost

3) Go to register page, then to the login page

4) Go to the login page, upload video, then automatically goes to results page

Steps to Run on Elastic Beanstalk

1) Run 'sh deploy.sh'

2) Go to your Elastic Beanstalk account

3) Go to the specified envirnoment

4) Go to configuration on the left side

5) Go to Load Balancer and click Edit on the page

6) Go down to Connection Draining and set Draining Timeout to 2000 seconds

7) Go to the site and follow steps 3 and 4 in "steps to run locally"