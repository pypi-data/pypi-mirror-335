
git tag -a v0.1.1 -m "version 0.1.1"
#poetry version 0.1.1
poetry build
poetry publish

```
poetry run pytest
```

# Code in src Folder
```
src
├─── assignment                         => Folder that contains Py scripts for managing an assignment
│    │
│    ├─── __init__.py                   => Contains `AssignmentMarking` class that is used for running the marking engine for an assignment (no need to change it)
│    │
│    ├─── config.py                     => Contains the variables that will be used during marking (need to update it according to the assignment requirements)
│    │
│    ├─── utils                         => Folder that contains Py scripts that will be useful for assessing some defined citeria
│    │ 
│    ├─── __init__.py                   => Contains `BaseFolder` class that is used to managed the directory structure for each student's submission (no need to change it)
│    │
│    ├─── similarities.py               => Contains functions used for assessing similarities between texts or numerics (can add more functionalities)
│    │
│    └─── sysmodules.py                 => Contains functions used for adding the path to the students folders in order to import thaier functions and/or classes (can add more functionalities)
│    
├─── checks                             => Folder that contains Py scripts used for performing checks and provide marks (need to update it according to the assignment requirements)
│    │
│    └─── pythonfile
│    │   ├─── __init__.py               => Contains `PythonFileChecker` class that is used to perform checks on python scripts only (no need to change it)
│    │   ├─── api_test.py               => Contains list of scenarios used for marking student's apy.py (need to update it according to the assignment requirements)
│    │   ├─── currency_test.py          => Contains list of scenarios used for marking student's currency.py (need to update it according to the assignment requirements)
│    │   └─── frankfurter_test.py       => Contains list of scenarios used for marking student's frankfurter.py (need to update it according to the assignment requirements)
│    │
│    └─── structure
│    │   ├─── __init__.py               => Contains `TemplateChecker` class that is used to verify if student's submission complies with the provided template structure (no need to change it)
│    │   └─── template.py               => Contains list of scenarios used for verifying and marking compliance of student's submission to provided template (need to update it according to the assignment requirements)
|
└─── submission.py                      => Contains `StudentMarking` class that is used to perform all checks on a student's submission complies with the provided template structure (need to update it according to the assignment requirements)
```


At the end of the marking process, a grouping is performed on the raw CSV file for each student in order to get the final view by category for each student.

# Notebook

A Jupyter notebook is saved in the `notebooks` folder. This is used to import the relevant classes and launch the marking engine.

You need to install all required dependencies by running:
```
poetry install
```

Then you can launch Jupyter:
```
poetry run jupyter lab
```
