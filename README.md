<p align="center">
	<img src="https://user-images.githubusercontent.com/30529572/72455010-fb38d400-37e7-11ea-9c1e-8cdeb5f5906e.png" />
	<h2 align="center"> Project Ideas </h2>
	<h4 align="center"> Platform to Post new Ideas and Discuss about them <h4>
</p>

---
[![DOCS](https://img.shields.io/badge/Documentation-see%20docs-green?style=flat-square&logo=appveyor)](INSERT_LINK_FOR_DOCS_HERE) 
  [![UI ](https://img.shields.io/badge/User%20Interface-Link%20to%20UI-orange?style=flat-square&logo=appveyor)](INSERT_UI_LINK_HERE)


## Functionalities
- [x]  Open Authorization using Google and Facebook
- [x]  Post New Ideas (Without Authentication)
- [x]  View All Published Ideas
- [ ]  Comment on Posted Ideas (Thread Based)
- [ ]  Upvote or Downvote the Idea
- [ ]  Admins can View the ideas and Publish or Reject them

<br>


## Instructions to run

* Pre-requisites:
	-  Python3

* Directions to install
	- Setting up a virtual env 
	```bash
	virtualenv env
	env\\Scripts\\activate
	```
	- Installing Packages
	```bash
	pip install -r requirements.txt
	```
	- Making mgrations
	```bash
	python manage.py makemigrations
	python manage.py migrate
	````

* Run the server

	```bash
	python manage.py runserver 3000
	```

<br>

## Contributors

* [ RiddhiGupta5 ](https://github.com/RiddhiGupta5)



<br>
<br>

<p align="center">
	Made with :heart: by DSC VIT
</p>

