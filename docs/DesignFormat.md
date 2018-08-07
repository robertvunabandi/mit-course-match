Whatever the format, let's home we are able to collect at least 1000 answers per questions for training. 


I have thought of two formats to go about this.

# Quiz Format

This format means there will be one quiz with a limited number of questions to answer. 

Let `QCount` be the number of questions in the quiz. Then, there will be a maximum of `QCount` questions that everyone will ever answer. 

### Advantages

- Having `QCount` questions means that the backend that we currently have is ready to handle this format. The backend is made in such a way that we have a set of questions and answers and question sets. This will mean we just have to select one question set. 
- It's easier to collect data. We can simply ask people what major they have chosen for training data and have them answer the quiz. 

### Disadvantages

- If the set of questions is bad, how do we fix it?
- This is kind of boring to be honest. It's also easy. I almost already have all the infrastructure needed to build it. Where is the learning in that?
  - Due to being boring, less developers will also be interested in contributing. Ideally, if there are interested people who want to contribute, that would be nice.   

# "Tinder" Format

The tinder format is not the one I had in mind when starting this. However, it has some interesting advantages. Before we get into that, here's how this format works.

One is presented with one question at a time. One can then answer the question accordingly. Then, one can answer questions indefinitely. As one answers more question, they will get more accurate predictions on the major that they should choose.  

Let `QMin` be the minimum number of questions needed for a population of `PCount` labeled subjects to have a substantial number of training data to have an accurate model. Essentially, we need `QMin` questions answered per training data person to have good enough data. 

### Advantages

- We are not limited with the number of questions that we can have. So, no need for question sets. 
- Users can be allowed to add their own questions. This will make it more fun. 
- Having "Tinder" on the name can be buzz-y, so that will catch onto people faster.

### Disadvantages

- Training becomes more complicated with this. It now looks more like a recommender problem. However, I am not sure how to best approach this.
  - That implies learning how to best do this since the questions will be categorical (instead of linear/real). 
  - After learning how to best train this, I will then need to figure out how to either use tensorflow to train the model or create it from scratch. 
  - **Is this a recommender system though?** Should think carefully about that. Another way to do this may be possible.
  - [Google Cloud Guide](https://cloud.google.com/solutions/machine-learning/recommendation-system-tensorflow-overview)
- We need to maintain state of the user. Therefore, we'd need to probably have users sign up. Signing up sucks.
  - That implies storing credentials in a database. That can be a hassle. 
    - Well this is not that bad since we already needed a database to store the questions. 
  - Could potentially use cookies to make it easier
  - People don't like signing up. However, we can easily have them sign up with Facebook or Github or Google or Twitter. That can make the process faster. 
- Collecting data becomes difficult:
  - How many questions should people answer until we know that we have collected enough data per person?
  - How do we instruct training en-mass with people not getting confused?
  - People will have to answer a minimum of `QMin` questions. 
- Designing this becomes a lot more complicated. There is a lot more things to take into account. 
  
  