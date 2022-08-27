# Project task ticketing system

This project is realization of my engineering thesis.</br> 
A browser application that allows to submit and manage tickets to a different 
extent depending on the role assigned in the system, the implementation 
was designed to work on a product that requires long-term operational improvement.
Implementation allows you to centralize communication with the client in the tasks 
and in a convenient way to filter the tickets that have entered the system. 
From the administration panel level it is possible to manage groups, users, 
start panels, types of tasks, processes in a given type of request, 
priorities and many other values that can be used to describe a task.</br>
In addition, it is possible to divide tickets by categorizing them into tenants, 
thanks to which it is possible to handle several projects from the level of the same 
application instance. The solution was prepared in Python using the Django framework.

## Instruction

#### Create virtual environment
```
  py -m virtualenv -p python3 venv
```

#### Instal necessary packages
```
  pip install -r requirements.txt
```

#### Collect static files
```
  py manager.py collecstatic
```

#### Run server
```
  py manager.py runserver
```

## License

This application is licensed under terms of the BSD 3-clause license. See the LICENSE file for full licensing terms.

Note that this application is distributed with 3rd party products which have their own licenses.

## Author

- [@Karol Siedlaczek](https://github.com/Haswell33)

