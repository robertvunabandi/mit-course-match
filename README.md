# README

MIT Course Match is a web application that helps students figure out what major they should choose at MIT. This project aims to achieve the following:
- Find interesting indicators for people's academic major decision
- Help people find the majors that they will likely enjoy

Thus, this is also a research project. How it works is that a given MIT (prospective) student answers a set of questions. Then, their answers are fed into a machine learning classifier that will figure out what major this person would be (with probabilities). Finally, this person sees the output of the model. 

# Design Criteria and Choice

This had two criteria to begin with: 
 1. the questions will "fun" and "non-traditional" survey-like questions. 
 2. Questions need to be such that any given person would not answer them in an obvious manner. 
    - So, the questions cannot single out a specific subset of people (i.e. by race or gender). Here, I am specifically referring to the questions used int the machine learning model to do the classification. 
    - No question should ostensibly bias toward any given major. So, an invalid question would be something like "do you like computers?", from which we can assume that most Computer Science and Electrical Engineering majors would answer "yes" to.
    - The questions should be such that the answer that the person chooses is not affected by the fact that they are in high school or are in college or are a given grade. 
    
# Project Goals

We specify goals in terms of "versions". 

## Version 0

In version 0, we just want to have something minimal working. This will require the following:
- `[1]` Coming up with the questions to use for the model respecting the questions criteria
- `[2]` Collect training data across multiple majors and people at MIT
  - Goals:
    - We need to have at least 300 or so labelled responses to start using this in production.
    - We should shoot for 600 or so labelled responses.
    - It would be great if we have 1000 responses.
  - Requires `[1]`
- `[3]` Build mechanism to convert recorded responses into training data (i.e. record responses and label them later on).
- `[4]` Build a website that reliably works.
  - `[4.1]` Set up how the machine learning model will train itself recurrently.
  - `[4.2]` Set up a mean to make prediction in production concurrently. 
  - `[4.3]` Set up means to collect responses and all data manipulations
- `[5]` Run the app in production, making sure we have that feedback loop that converts recorded responses into training data. 

## Version 1

The main focus of version 1 is to polish the UI. 

## Version 2

Assuming we get a substantial amount of answers, we can start analyzing the data to figure out why one answer yields a specific result. Some of the things we want ot figure out are: 
- what are the importance of each individual question in deciding which major the model decides?
- How do people for a given major usually answer a given question?
  - This is, assuming the people in that major seem to answer that question in a particularly similar way.

After making multiple analysis, we can publish somewhere somehow. That's really TBD. 

Another actionable here is to display the response with more details about why a given major ranks where it ranks for a given user. 

## Version 3

Attempt to expand to other schools.

# Design Choice

See the design format doc.

**NOTE:** *The project is currently at its early phase, so everything is a bit crazy in the codebase, including this README. Content should become more organized as time passes.*