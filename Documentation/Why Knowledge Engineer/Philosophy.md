# Why Knowledge Engineer?  What Problem Does it Address?


## LLMs and Short Attention Spans

The current state of AI technology has a "***short attention span***".  
Although it can produce amazingly intelligent responses; 
it can only work on ***smallish*** pieces of a problem at a time. 
If you give it too big of a problem it gets lost.


This problem is compounded when trying to get the AI to do something like coding which is extremely exacting. 
This is related to the famous ***context size***.  I refer to it as "***short attention span***", 
which is the easiest way to understand the effects.  

Newer models of AI have increased the ***context sizes*** from 32k tokens to 128K tokens (a factor of 4 times). 
This works better, **_but does not_** give us an attention span 4 times longer.  

We are pushing up a curve of diminishing returns!

# Current Knowledge Management Solutions

There are 2 **_standard_** solutions for managing knowledge size:
1. Summarizing and
2. Semantic Searches 

## 1. Summarizing

Consider the case where we want to use the Knowledge presented in a large book.
The book exceeds the context size by a huge margin.
But we can go chapter by chapter asking AI to summarize the chapter. 

Then you split the AI Query into 2 parts:
1. Before we ask the AI to do something, we first give it the summaries and ask AI: 
'Which chapter will have the answer?'.
2. Then we can feed AI the specific chapter and ask it use that knowledge.

This method assumes: 
- that the information is divided into logical sections of appropriate sizes.  
- It also requires that the chapters be designed to be independent of each other. 

 The results of feeding AI the knowledge in chapter 14 while withholding the **_required knowledge_** in chapters 1 - 13 obviously won't work.  
 
So for this to work well **_the "book" must be designed to be used in such a way_**. 


#### Your Milage May Vary

## 2. Semantic Searches 
In this solution we break the knowledge into arbitrary chunks of fixed size.  We then tokenize the chunks. 
The chunk is then stored in a database that allows you to identify text that is **_semantically similar_** to the question you are asking.  
The Semantic Database will give you a rating of which chunks have Semantically similar words in proximity to each other. 
You then identify the chunk that "best matches", retrieve that text and feed that text to the AI, with your question.

**_Although the semantic search itself is a wonder of modern IT_**, the concept of feeding the AI arbitrary "chunks" out of a knowledge base 
and hoping that the chunk is coherent, and that the AI can make sense of the knowledge is doubtful at best.

#### Your Milage May Vary

# A Different Approach
The **_standard solutions_** had one thing in common.  They are general solutions to be applied to any problem irrelevant of the domain of the problem.

In IT, we have long known that the more domain knowledge you put into your solution the better and more elegant you can make the solution.  That is exactly what we are going to do here...

But let's start from the beginning...

## Aladin AI grants your wish

We could ask AI to **_"Write a Snake Game using pygame."_**, and expect it to output the entire python program just like that.  If you fudge with the prompts enough you might even get it to work every once in a while.  

But the only reason that it works is that there are thousands of 
snake game implementations that the AI was trained on. 
(The snake game is a typical intermediate exercise that is given to
many programmers).

Do something useful beyond that? That is simply not within the attention span of current LLMs.

#### Okay, what now?

## Breaking The problem into Pieces

We need to manage the Knowledge: 
- We need to break the problem into the steps.  
- Each step needs to use specific inputs designed exactly for that step.  
- The problem within the step needs to be singularly focused on one problem.  
- Each output needs to be designed to output exactly what is required 
for the next step. 
- We need a system that is strictly top down without cyclic complications.  
- each step needs its own problem domain.
- The AI must know how to solve the problem within the domain of each step.

Sounds impossible?  Well, It is not.  there is a well known and methodology 
meets all the conditions.  It is one of the most studied IT Methodologies 
ever (Therefor AI knows it well). 

It is called: 
#### The WaterFall Technique

What? Are you Crazy? That old stuff we threw away in the 60's?  
Yep, that is the one! 

## The Waterfall Technique

Advantages:
- It is the best studied / understood form of IT development.  
- Each step in the process has very detailed and designed inputs and outputs.
- LLMs have studied it extensively on the internet and have a good understanding of it.

Old Disadvantages of Waterfall:
- Have to restart at the beginning, if an input to a previous step is changed. (This is not a problem for AI)  
- Tedious and time-consuming. (This is not a problem for AI)
- You have to know every requirement at the beginning. (This is not a problem for AI)

The WaterFall Technic gets its name from each Step having to be completed before the next step can be started.  It is a strict top-down process.  Each step has a very specific input and a very specific output.  The output of one step is the input to the next step.  The process is very well-defined and understood.

We dropped the WaterFall technique in the 60's because it was too time-consuming.  By the time we got to programming the system, the user market requirements had changed.  By the time the end user got the system it was already outdated. This is not a problem with AI.  It can do the steps very quickly and consistently.  It can also quickly restart at the beginning if an input to a previous step is changed.

## The Waterfall Technique with AI
Okay lets look at an over simplified example:  

### 1- Make Requirements
- Read the description of the application in the file Requirements/ApplicationDescription.md 
- Generate a list of rules for the game of Snake to Requirements/SnakeGameRules.md
- Generate a list of requirements for the Snake program that includes implementation of all the rules in Requirements/SnakeGameRules.md and write it to Requirements/SnakeGameRequirements.md


That is a definite "can do" with the current level of AI.  
But more importantly, it can do it consistently (allowing automation)

### 2- Make an Implementation Plan
- Read the application requirements in Requirements/SnakeGameRequirements.md
- generate Implementation Plan and write it to Requirements/ImplementationPlan.md

### 3- Execute Implementation Plan 
...


# Conclusion 
You can see how this form of Knowledge Management makes a lot more sense, 
and could actually get AI to produce something useful.

## Knowledge Engineer is built to help you do just that...


Jerry The Dinosaur

**_P.S._** 
Maybe it took a Dinosaur to see how our most ancient IT techniques 
would work well with the newest most modern IT technology.  
But I think it is a good idea,  What do you think?

