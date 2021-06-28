# Swolemate
*Final project of Product Analytics, USF MSDS program*


# About

*Providing Hollywood level training in the comfort of your home*

**CEO**: Kexin Wang <br>
**Front End**:  Elyse Cheung-Sutton, Daniel Carrera, Moh Kaddoura <br>
**Back End**: Suren Gunturu, Kristofor Johnson, Wenyao Zhang, Boliang Liu

<img src = './readme/new_image_girl.png' height = 250>   <img src = './readme/new_image_boy.png' height = 250>


# Technical Components
Steps To Run: 
1) Go into the code directory 
2) Run "docker build -t app_img ."
3) Run "docker run -e AWS_ACCESS_KEY_ID=AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -it --rm -p 80:5000 app_img"
4) Go into the site using Localhost and click "Register" to register an account and "Login"
5) After Login, automatically redirect to the Upload Page and upload a video with a dropdown of the given exercise and submit
6) After submitting, if there is an error, manually redirect to "localhost/userpage", otherwise it will automatically redirect


## Trello Project Management <img src = './readme/trello2.jpeg' height = 20>

We used project management tool Trello to track tasks and progress.

<img src = './readme/trello.png' height = 350>

## Sphinx

We used Python documentation generation tool to generate document.

<img src = './readme/sphinx.png' height = 350>

## Docker   <img src = './readme/docker.png' height = 20>


## Elastic Beanstalk   <img src = './readme/aws.jpeg' height = 20>

We used AWS Elastic Beanstalk to deploy our application, so it's easy to scale and update based on user growth.
Link: http://testenvv3.eba-dzpuncdn.us-west-2.elasticbeanstalk.com/
