import os
from pickle import FALSE, TRUE
import nltk
import string
from nltk.stem import PorterStemmer
import json
import tkinter as tk
#object for stemming
word_stemmer = PorterStemmer()
#object for relacing punctuations to space
#string.punctuation = !"#$%&'()*+, -./:;<=>?@[\]^_`{|}~ 
remove_punctuation_translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))

def splitWords(word_list):
    words=[]
    for word in word_list:
        print(word)

#read form file and create positional and inverted index
#will be performed once only
#PREPROCESSING
def readFromFileAndMakeIndexes():
    #getcwd brings the existing path of file
    path=os.getcwd()
    path=path+'/Abstracts/'
    #getting all files in path
    files=os.listdir(path)
    i=0
    inverted_index={}
    positional_index={}
    stop_words=stopWord()
    # print(stop_words)
    for file in files:
        i=i+1
        f=open(os.path.join(path,file))
        words=[]
        new_words=[]
        #split is a built in function used to break the documents into sentences
        for line in f.read().split("\n")[0:]:
                if line:
                    #remove any punctuation in a line
                    line=line.translate(remove_punctuation_translator)
                    #nltk libarary function used to make sentences into word tokens
                    words=nltk.word_tokenize(line)
                    for items in words:
                        if len(items)>1:
                            items=items.translate(remove_punctuation_translator)
                            new_words.append(word_stemmer.stem(items))                    
        #patition function is sued to break string at the first occurence of '.'
        doc_id=(file.partition(".")[0])
        #convert from sting to int 
        doc_id=int(doc_id)

        #postion variable is used to determine position of word in document
        position=0
        for word in new_words:
            position=position+1
            if word not in stop_words:
                #create inverted index
                if word not in inverted_index:
                    inverted_index[word]=[]
                    inverted_index[word].append(doc_id)
                else:
                    if doc_id not in inverted_index[word]:
                        inverted_index[word].append(doc_id)
                
                #for positional index
                if word not in positional_index:
                    positional_index[word]={doc_id : [position]}
                elif doc_id in positional_index[word]:
                    positional_index[word][doc_id].append(position)
                else:
                    positional_index[word][doc_id]=[position]
    sorted_inverted_index={}
    for i in sorted(inverted_index):
        sorted_inverted_index[i]=inverted_index[i]

    return sorted_inverted_index,positional_index
    # print(positional_index)
    
def writeIndexesToFile(inverted_index,positional_index):
    tf = open("inverted_index.json", "w")
    json.dump(inverted_index,tf)
    tf.close()
    tf = open("positional_index.json", "w")
    json.dump(positional_index,tf)
    tf.close()

def ReadIndexesFromFile():
    
    tf = open("inverted_index.json", "r")
    inverted_index = json.load(tf)
    # print(inverted_index)
    tf = open("positional_index.json", "r")
    positional_index={}
    positional_index = json.load(tf)
    
    print(positional_index)
    return inverted_index,positional_index


#used to read stopwords from file
def stopWord():
    stop_words=[]
    f=open("Stopword-List.txt")
    #make an array of all stop words
    for word in f.read().split("\n")[0:]:
        if word:
            stop_words.append(word.strip())
    return stop_words

#function for simple one word query
def simpleQuery(query_word,inverted_index):
    if query_word in inverted_index:
        result_set=inverted_index[query_word]
        return sorted(result_set)
    else:
        return("No search result found")

#function for AND Boolean query
def booleanAndQuery(query_words,inverted_index):
    result1=set(inverted_index[query_words[0]])
    result2=set(inverted_index[query_words[2]])
    andResult=result1.intersection(result2)
    for i in range(4,len(query_words),2):
        print(i,query_words[i])
        result1=set(inverted_index[query_words[i]])
        andResult=result1.intersection(andResult)
        print(i,query_words[i])
    return(sorted(andResult))


#function to resolve OR boolean query
#ex time OR series
def booleanOrQuery(query_words,inverted_index):
    andResult=set(inverted_index[query_words[0]])
    for i in range(2,len(query_words),2):
        result1=set(inverted_index[query_words[i]])
        #used union function
        andResult=result1.union(andResult)
    return(sorted(andResult))


#function to resolve combined boolean querry 
#which have both AND OR in query
#ex time AND series OR classification
def booleanCombinedQuery(query_words,inverted_index):
    #initialize
    result=set(inverted_index[query_words[0]])
    #loop through whole query
    for i in range (1,len(query_words),2):
        #if center word is and then instersect else union
        if 'and' in query_words[i]:
            result1=set(inverted_index[query_words[i+1]])
            result=result.intersection(result1)
        else:
            result1=set(inverted_index[query_words[i+1]])
            result=result.union(result1)
    return(sorted(result))


#function to resolve proximit query ex feature track /5
def proximityQuery(query_words,inverted_index,positional_index):
    k=query_words[-1]
    k=k.replace("/","")
    #check if query words are present in documents
    if query_words[0] and query_words[1] in inverted_index:
        #intersect documents of both query words
        result1=set(inverted_index[query_words[0]])
        result2=set(inverted_index[query_words[1]])
        andResult=list(result1.intersection(result2))
        finalResult=[]
        #loop for documents in which both words are present
        for i in range (len(andResult)-1):
            left=0
            right=0
            while((left<(len(positional_index[query_words[0]][(andResult[i])]))) and (right<(len(positional_index[query_words[1]][(andResult[i])])))):
                #check if difference in position is within k 
                if(abs((positional_index[query_words[1]][(andResult[i])][right])-(positional_index[query_words[0]][(andResult[i])][left]))<=int(k)+1):
                    finalResult.append((andResult[i]))
                    break
                #check which iterator left or right should be moved forward according to positions
                elif ((positional_index[query_words[1]][(andResult[i])][right])>(positional_index[query_words[0]][(andResult[i])][left])):
                    left=left+1
                else:
                    right=right+1
        return sorted(finalResult)
    else:
        return "No search result found!"

def Complement(query_word,Inverted_Index,Position_Index):#This function will return Complement of a list  
    result=[]
    if (type(query_word) is str):
      if(len(Inverted_Index[query_word])==0):
         Inverted_Index[query_word]=[]  
      for i in  range(0,448):
         if str(i) not in Inverted_Index[query_word]:
            result.append(str(i)) 
    return(result)


def queryProcess(query,inverted_index,positional_index):
    query_words=[]
    stop_words=stopWord()
    for q_word in nltk.word_tokenize(query):
        if q_word not in stop_words or 'AND' in q_word:
            query_words.append(word_stemmer.stem(q_word))
    print(query_words)
    #checking which type of query is comming 
    if len(query_words)==1:
        fResult=simpleQuery(query_words[0],inverted_index)
    elif 'and' in query_words or 'or' in query_words:
        for i in range(0,len(query_words),2):
            if query_words[i] not in inverted_index:
                return "No search result found!"
        if 'and' in query_words and 'or' in query_words: 
            fResult=booleanCombinedQuery(query_words,inverted_index)
        elif 'and' in query_words:
            fResult=booleanAndQuery(query_words,inverted_index)
        else:
            fResult=booleanOrQuery(query_words,inverted_index)
    elif "not" in query_words:
        fResult=Complement(query_words,inverted_index,positional_index)
    else:
        fResult=proximityQuery(query_words,inverted_index,positional_index)
    return fResult


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.configure(background='#00AFF0')
        self.geometry('500x500')
        self.title('Giga Search Engine')
        self.innerFrame = tk.Frame(self, height=300, width=400,background="#00AFF0")
        self.innerFrame.pack(pady=80)
        self.innerFrame.pack_propagate(0)
        self.inputLabel = tk.Label(self.innerFrame, text="Welcome to GIGA Search Engine",background="#00AFF0",font=("Bahnschrift light", 20))
        self.inputLabel.pack(pady=20)
        self.inputtxt = tk.Text(self.innerFrame,
                   height = 1,
                   width = 30)
        self.inputtxt.pack()
        self.searchButton = tk.Button(self.innerFrame,
                        text = "Search", 
                        command = self.search)
        self.searchButton.pack(pady=20)
        self.resultFrame = tk.Frame(self.innerFrame, height=170, width=400)
        self.resultFrame.pack()
        self.resultFrame.pack_propagate(0)
        self.resultText = tk.StringVar()
        self.resultBox = tk.Label(self.resultFrame, height=170, width=300, textvariable=self.resultText, wraplength=300,background="#00AFF0")
        self.resultBox.pack(pady=0)
        # if os.path.isfile("positional_index.json"):
        #     self.inverted_index,self.positional_index=ReadIndexesFromFile()
        # else:
        self.inverted_index,self.positional_index=readFromFileAndMakeIndexes()
            # writeIndexesToFile(self.inverted_index,self.positional_index)
    def search(self):
        query = self.inputtxt.get(1.0, "end-1c")
        result=queryProcess(query,self.inverted_index,self.positional_index)

        if "No" not in result:
            self.resultText.set(", ".join([str(x) for x in result]))
        else:
            self.resultText.set(result)



if __name__ == "__main__":
    app = Application()
    app.mainloop()