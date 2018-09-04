# Design Format

## Home Page

This page quickly explains how the app works. At the end of the home page, there will be a "Take the Quiz" section. See below:

> MIT Course Match is a tool that uses Machine Learning to help students at MIT figure out their majors. 

> ##### How it works
> 1. Answer the questions in the quiz. 
> 2. Send your responses to our backend so we can calculate which major fits you best.
> 3. Explore your results.

> [Take the Quiz](#) 

> How it Works (<- links to about page)  
> About This Project (<- links to about page)  
> Contact Us (<- have a modal form)  
> Copyright C 2018 MIT Course Match

## Quiz Page

This is where one takes the quiz. Two cases can happen:
- Someone answers the quiz with a labelled response (they tell what major they are)
- Someone answers the quiz without a labelled response

### Unlabelled Response

In this flow, first there will be a disclaimer. This must be short enough that people can read it completely. However, it needs to have enough information to clearly say "yo, don't just blindly follow what this suggests. it's ML after all, and we all know how bad it can be." Also talk about plans to have this in the future tell you why that major. 

Then, the person gets to answer the quiz. They answer all the responses needed then can submit their answer. Finally, at the end, they will be prompted to enter a raffle if they know their major already to input it, with the idea in mind that their major will not be used to compute their answer but to make the model better. 

### Labelled Response 

In this case, the person will work the same as the unlabelled response except at the end, they choose to label their response. After choosing it, they are prompted to log in with MIT OpenID Connect. This part needs to make sure to emphasize that their information will be hashed (so impossible for us to match them with their answers). The purpose of this is to limit the answers to only one person. 

Then, their name & email will be entered into a separate entry, independent again of their answer, such that they can be notified with the raffling results. 

## About Page

This page details why we're working on this project and how this project works. 

## Courses Page

After having done the studies, this page will allow one to determine how one course behave and maybe do comparisons between courses. 

---

> BELOW THIS IS **DEPRECATED**. The content below is not accurate and will be removed eventually. September 4th, 2018. 

# Design Format

These are the design choices that will be implemented in this format:
- We'll use a **Tinder** format for the quiz portion. What that means is that people get to answer questions one by one, and they get the questions in a shuffled order.
- There will be a total of 100 questions to answers. 
- Users will need to answer at least 25 questions to get predictions. Other unanswered questions will be given a default value. 
- We use the model we have in the database, except now there will be no question sets. There will be just questions. 
- We will use a user's table and track which questions they have answered. So, that means people will need to sign up.
  - Let people sign up with Facebook or Google or MITOpenIDConnect or Github. 

## Collecting Training Data

Some roadblocks for collecting training data:

- There is no incentive to be a subject to collect training data if one has already chosen their major and love it.
  - We'd need to incentivize people to do it somehow. Asking friends to do it can work, but then we wouldn't collect enough training data. Maybe raffles? 
- When collecting the training data, the instructions need to be clear so that people know what to do.
- To reach a lot of people, we'll need to dormspam like crazy. 
- Only sophomores+ should be eligible. How do we prevent freshmen from getting targeted?
- If people "sign-up", then we can set a reminder to ask them to label (say what course they have chosen) their course 1 year after they login (or on a specific set of dates in the academic year after they sign up).

We can do the following: 

- we can offer some of the following incentives:
  - Raffle for prizes. Let's have the following raffle goals:
    - 1 person wins a $50 gift card
    - 5 people win $25 gift cards
    - 5 people win $10 gift cards
  - One person has to answer at least 25 questions to enter the raffle. 
    - At 25 questions, it's as if they have won 1 raffle ticket.
    - For each question in count 26-50, they win 0.2 extra raffle tickets. **Total: 5**
    - For each question in count 51-60, they win 0.3 extra raffle tickets. **Total: 3**
    - For each question in count 61-80, they win 0.4 extra raffle tickets. **Total: 8**
    - For each question in count 81-95, they win 0.6 extra raffle tickets. **Total: 9** 
    - For each question in count 96-100, they win 2 extra rffle tickets. **Total: 10** 
  - Maybe ask money from MIT to do this raffle. It could help the MIT community.
  


## Goals

- We should get a total of about 500 labeled response per question to deem our predictor somewhat accurate. 





---

# Previous Discussions on Format

#### `[Completed on 2018-08-07]`

I have thought of two formats to go about this.

## Quiz Format

This format means there will be one quiz with a limited number of questions to answer. 

Let `QCount` be the number of questions in the quiz. Then, there will be a maximum of `QCount` questions that everyone will ever answer. 

### Advantages

- Having `QCount` questions means that the backend that we currently have is ready to handle this format. The backend is made in such a way that we have a set of questions and answers and question sets. This will mean we just have to select one question set. 
- It's easier to collect data. We can simply ask people what major they have chosen for training data and have them answer the quiz. 

### Disadvantages

- If the set of questions is bad, how do we fix it?
- This is kind of boring to be honest. It's also easy. I almost already have all the infrastructure needed to build it. Where is the learning in that?
  - Due to being boring, less developers will also be interested in contributing. Ideally, if there are interested people who want to contribute, that would be nice.   

## "Tinder" Format

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
  - If the number of questions is limited, then this will not be a recommender system. 
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
  
  