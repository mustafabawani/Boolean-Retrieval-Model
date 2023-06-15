import json

my_dict = { 'Apple': 4, 'Banana': 2, 'Orange': 6, 'Grapes': 11}

tf = open("myDictionary.json", "w")
json.dump(my_dict,tf)
tf.close()