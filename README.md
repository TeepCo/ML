# ML
---
This project is developed for better localisation of pallets with goods in open warehouse.

We are using Machine Learning for better localisation in last few meters.

Project is written in Python


##Installation

These algorithms requires [Python](https://www.python.org/downloads/) to run.

There are also several libraries that are required to run. 

- [Shapely](https://pypi.org/project/Shapely)
- [Pandas](https://pypi.org/project/pandas)
- [NumPy](https://pypi.org/project/numpy)
- [Sklearn](https://pypi.org/project/scikit-learn/)
- [Pydot](https://pypi.org/project/pydot)

After installation of all necessary dependencies test data must bee downloaded. 

You can download them [here](https://drive.google.com/drive/folders/1MD2ihb0ygYwINTISdTO3_V-OSGgu-ljA)


##Usage

###First algorithm

To run first algorithm use these commands  

```sh
cd ML_model_loading
python model_run.py
```

Algorithm show result e.g. true negative: 554, false positive: 107, false negative: 107, true positive 232.

###Second algorithm 

To run second algorithm use these commands

```sh
python lastmeters.py
```

Algorithm will show a window with way through warehouse.

###Third algorithm

Third algorithm is used for pairing data from ERP and collected data.

To run third algorithm use these commands


```sh
python route_locator.py
```

Algorithm will generate a file localized_routes.csv with locations, name and type of these positions.