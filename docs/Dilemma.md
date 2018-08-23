# Current Dilemmas

## How do we maximize the collection of training data?
 
The people who will answer this survey, who ideally are from MIT, will fit into two categories: those who have declared their major and those who haven't. This project can potentially help those who haven't declared their majors. However, in order for it to be useful, we need responses from those who have.

There are two solutions:
- Collect data from those who have declared major by asking them to complete the survey and put their major at the end. 
- Collect data from those who haven't declared later when they declare by converting their stored response from being un-labelled to labelled. 

The first solution is pretty straightforward and briefly discussed below.

### Collect From Declared Majors

This is simply having the declared person answer the question and include their major before submitting. This will be the first way of collecting data. Simply put, we will dormspam people who have declared their major to answer the questionnaire.

There needs to be an incentive to answer. There will be multiple raffle prizes for those who participate.   

### Collect From Undeclared When Declared

These people will go through the normal flow. Once they reach the end and are asked whether they have declared their major, they will have an option to choose "undeclared". At that moment, the given user's data will be stored in the DB. 

This information, such as email, can be used to contact them later on to ask whether they have declared and what major they chose.

The problem with this is that the information about the user can be matched with a survey response, which is bad because a malicious person can snoop on other people's responses.

# Solved Dilemmas

## How to prevent non-MIT to answer this survey or MIT to answer multiple times? 

We will use MITOpenID connect and have people log in through it. 

The way this this will work is that after they are done completing their survey, we will prompt them to log in to confirm that they are MIT. Once they log in, we have a way to match one set of answer to one individual. 

We will hash the receivable information from MIT OpenID Connect so that we're not able to match a given user's response with a specific user. 

## Should it be mandatory to answer all questions?

### Yes, here's why

If people know that they don't have to answer all the questions, then it can potentially make them feel more in control and be more willing to take the quiz.

If we add more questions, then all the answers from before will miss that questions. So, it'd make sense to put the answer to that question with a default value just as it would be with questions that are unanswered. Basically, this gives the opportunity to add more questions safely, which is better for our needs. Some questions will probably be trash. 

### No, here's why

 We need all answered to be as real as possible. Letting people not answer questions means that those questions will be answered with a default response. This is a missed opportunity at classifying them better. 