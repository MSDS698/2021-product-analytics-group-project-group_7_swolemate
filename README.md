# Swolemate
*Final project of Product Analytics, USF MSDS program*


# About

*Providing Hollywood level training in the comfort of your home*

**CEO**: [Kexin Wang](https://www.linkedin.com/in/sheena-kexin-wang-3a51b7170/) <br>
**CTO**: [Daniel Carrera](https://www.linkedin.com/in/daniel-carrera/) <br>
**Data Scientist**:  [Elyse Cheung-Sutton](https://www.linkedin.com/in/elysecs), [Moh Kaddoura](https://www.linkedin.com/in/moh-kaddoura/) <br>
**Engineer**: [Boliang Liu](https://www.linkedin.com/in/boliang-liu/), [Kristofor Johnson](https://www.linkedin.com/in/kr-johnson/),
              [Suren Gunturu](https://www.linkedin.com/in/suren-gunturu/), [Wenyao Zhang](https://www.linkedin.com/in/wenyao-zhang/) <br>

<img src = './readme/new_image_girl.png' height = 250>   <img src = './readme/new_image_boy.png' height = 250>


# Technical Components

## Model

We used Detectron2, which is developed by Facebook AI Research, to detect the movements of human joint points in vedios. And We used the outputs of pose estimation to evaluate videos of professional trainers and users through human pose keypoints. In this project, we evaluated three exercises: bicep curl, front raise, and shoulder press.

References: <br>
https://github.com/facebookresearch/detectron2 <br>
https://github.com/stevenzchen/pose-trainer

## Trello Project Management <img src = './readme/trello2.jpeg' height = 20>

We used project management tool Trello to track tasks and progress.

<img src = './readme/trello.png' height = 350>

## Sphinx

We used Python documentation generation tool to generate document.

<img src = './readme/sphinx.png' height = 350>

## Docker   <img src = './readme/docker.png' height = 20>


## Elastic Beanstalk   <img src = './readme/aws.jpeg' height = 20>

We used AWS Elastic Beanstalk to deploy our application, so it's easy to scale and update based on user growth.
