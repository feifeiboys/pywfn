import numpy as np
from logReader import Reader
Data=Reader(r"C:\code\HFV\files\lianben\files\lianbenScan_2.out").get()
orbitals=list(map(lambda x:x-1,[32,34,35,38,39,40,41]))
atoms=[1,2]
bondOrder_i=Data.squareSum(atoms[0],orbitals)/Data.all_sauare_sum[:,orbitals]
bondOrder_j=Data.squareSum(atoms[1],orbitals)/Data.all_sauare_sum[:,orbitals]
