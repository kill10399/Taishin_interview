import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
from math import cos,pi

import requests
import json
import re

#search for target tag in Json
def searchJ(file, target):
    # search for target element
    # input should be a list
    for i in file:
        if type(i) not in [dict, list]:
            break
        if target in i.keys():
            a= i[target]
            return a
            
        else:
            for k in i.keys():
                if type(i[k]) in [list, dict]:
                    if type(i[k])==list:
                        find = searchJ(i[k],target)
                        if find!=None:
                            return find
                    else:
                        find = searchJ([i[k]],target)
                        if find!=None:
                            return find
                        
# get coordinates from google geocode API
def get_googleData(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'%(address, gMapClientKey)
    r = requests.get(url)
    results = r.json()['results']
    location = searchJ(results,'location')
    return location

# find the nearest taishin branch for each 7-11 store
# distance in Km
def find_closet_branch(br_data, x, y, city=None, remove=[]):
    branch_location = br_data[['分行代碼','lat','lng','city']]
    location = np.array(branch_location[['lng', 'lat']])
    location = ((location-np.array([x,y])) * np.array([111.320 * cos(y*pi/180), 110.574]))**2
    location = location.sum(axis=1)**0.5
    mdis1 =location.min()
    md_branch1=branch_location.分行代碼.iloc[location.argmin()]
    return mdis1,md_branch1

# the 7-11 store not in main island of Taiwan
def findNonIsland(address):
    city_list = ['澎湖縣', '連江縣','金門縣']
    village_list = ['台東縣綠島鄉','台東縣蘭嶼鄉','屏東縣琉球鄉']
    city = re.match('.*?[市縣]{1}',address).group(0)
    village = re.match('.*?[鄉]{1}',address)
    village = village.group(0) if village else ''
    return city in city_list or village in village_list

def branch_cover(s):
    #atIsland = seven[seven['NotAtIsland']==False]
    branch_cover = s[['poiid', 'city']]
    branch_cover['Nearest_b_index'] = s.mDis_br.apply(lambda x:x[1])
    branch_cover['br_distance'] = s.mDis_br.apply(lambda x:x[0])
    
    branch_cover = branch_cover.groupby('Nearest_b_index').agg({'poiid':['count','unique'], 'br_distance':'mean'})
    branch_cover['cover'] = branch_cover[('poiid', 'count')] * branch_cover[('br_distance', 'mean')]
    
    return branch_cover

