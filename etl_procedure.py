#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import unicodedata	
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import os


def shape_element(element):
    node = {}
    adj  = {}
    way  = []
    address={}
    contact={}
    business=""
    name=""
    children="false"
    postcode =""
    phone =""
    if element.tag == "node"  :
        for child in element:
          if child.attrib["k"].find("addr:street") >= 0:
             children = "true"
             break
          else:
            #print (child.attrib)
            children = "false"
   
 
        if children == "true":
            node={        "id": element.attrib["id"],
                        "type": "node",
                    "created" :{"version"   : element.attrib["version"],
                               "changeset" : element.attrib["changeset"],
                               "timestamp" : element.attrib["timestamp"],
                               "user"      : element.attrib["user"],
                               "uid"       : element.attrib["uid"]
                               },
                    "latitude"  : float(element.attrib["lat"]),
                    "Longitude" : float(element.attrib["lon"])}
            for child in element:
                  #Only identifies inner elements with addr string
                  if str(child.attrib["k"]).find("addr:")  >= 0 :
                      if str(child.attrib["k"]).count(":") == 1:
                        if str(child.attrib["k"]) == "addr:postcode":
                          postcode = fix_postcode(str(child.attrib["v"]))
                          adj= {str(child.attrib["k"].replace("addr:","")) : postcode}
                        else:
                          adj= {str(child.attrib["k"].replace("addr:","")) : str(child.attrib["v"])}
                        address.update(adj)
                  else:
                      if str(child.attrib["k"]).find("contact:")  >= 0 : 
                        if str(child.attrib["k"]).count(":") == 1:
                          if str(child.attrib["k"]) == "contact:phone":
                            phone =  fix_phone(str(child.attrib["v"]))
                            ctc = {str(child.attrib["k"].replace("contact:","")) : phone }
                          else:
                            ctc = {str(child.attrib["k"].replace("contact:","")) : str(child.attrib["v"])}
                          contact.update(ctc)
                      elif str(child.attrib["k"])== "amenity" :
                          business = str(child.attrib["v"])
                      elif  str(child.attrib["k"])== "name" :
                          name =  str(child.attrib["v"])
                        
            if len(address)!=0:    
              node.update({"address":address})
            if len(business)!=0:
              node.update({"Business": business})
            if len(name)!=0:
              node.update({"Name": name })
            if len(contact)!=0:
              node.update({"contact":contact})
    
        return node  
    else:
        return None


def fix_postcode(value):
# This routine is just to transform the postalcode in a format xxxx-xxxx
  data = ""
  if len(value)==9 :
    data = value
  else:
    if value.find("-")==-1 :
       data = value[0:4] + "-" + value[4:9]
    else:
       data = value[0:9]
  return data


def fix_phone(value):
# This routine is to remove special characters from phone numbers
  data = ""
  chars = "()/\.|_ -  "
  for c in chars:
    value = value.replace(c,"")
     	
  data = value
  return data


def process_map(file_in, pretty = False):
    # You do not need to change this file 
    file_out = "{0}.json".format(file_in)
    data = []
    tam = 0
    with codecs.open(file_out, "w") as fo:
        fo.write("[")
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "," + "\n")
                else:
                    fo.write(json.dumps(el) + "," + "\n")
       
    
    # read the file into a list of lines
    lines = open(file_out, 'r').readlines()

    # now edit the last line of the list of lines
    new_last_line = (lines[-1].rstrip())
    size= len(new_last_line)
    new_last_line = new_last_line[0:size-1]
    new_last_line = new_last_line + "]"
    lines[-1] = new_last_line

    # now write the modified list back out to the file
    file = open(file_out, 'w')
    file.writelines(lines)
    file.close
    return data

def insert_data(data, db):

    for a in data:
        db.saopaulo.insert(a)
    

def test():
    from pymongo import MongoClient
    # Here is called the driver to communicate to mongodb
    client = MongoClient("mongodb://archanous:test01sm@cluster0-shard-00-00-3mqod.mongodb.net:27017,cluster0-shard-00-01-3mqod.mongodb.net:27017,cluster0-shard-00-02-3mqod.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
    db     = client.saopaulo	
    data = process_map('/home/training/vanhack/saopaulo.osm', True)
    with open('/home/training/vanhack/saopaulo.osm.json') as f:
      out = json.loads(f.read())
#      insert_data(out, db)
   

if __name__ == "__main__":
    test()
