# This files contains your custom actions which can be used to run
# custom Python code.


## if you want to run code, that would go in the actions.py file (python).
# code that you create and action, if you need action to be triggered add to stories, add to list of actions in domain file, if the action 

#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from cgitb import text
from typing import Any, Text, Dict, List
from urllib import response

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import ConversationPaused

import pandas as pd
import numpy as np
import datetime
import time

# Moods, sorted by quadrant w.r.t. valence and arousal
moods_ha_lv = ["afraid", "alarmed", "annoyed", "distressed", "angry", 
               "frustrated"]
moods_la_lv = ["miserable", "depressed", "gloomy", "tense", "droopy", "sad", 
               "tired", "bored", "sleepy"] # sleepy actually in different quadrant
moods_la_hv = ["content", "serene", "calm", "relaxed", "tranquil"]
moods_ha_hv = ["satisfied", "pleased", "delighted", "happy", "glad", 
               "astonished", "aroused", "excited"]

# Extract custom data from rasa webchat
def extract_metadata_from_tracker(tracker: Tracker):
    events = tracker.current_state()['events']
    user_events = []
    for e in events:
        if e['event'] == 'user':
            user_events.append(e)

    return user_events[-1]['metadata']

# Answer based on mood
class ActionAnswerMood(Action):
    def name(self):
        return "action_answer_mood"

    async def run(self, dispatcher, tracker, domain):

        curr_mood = tracker.get_slot('mood') #tracker.latest_message['entities'][0]['value']

        if curr_mood == "neutral":
            dispatcher.utter_message(response="utter_mood_neutral")
        elif curr_mood in moods_ha_lv:
            dispatcher.utter_message(response="utter_mood_negative_valence_high_arousal_quadrant")
        elif curr_mood in moods_la_lv:
            dispatcher.utter_message(response="utter_mood_negative_valence_low_arousal_quadrant")
        elif curr_mood in moods_la_hv:
            dispatcher.utter_message(response="utter_mood_positive_valence_low_arousal_quadrant")
        else:
            dispatcher.utter_message(response="utter_mood_positive_valence_high_arousal_quadrant")
        
        return []

# Introduce bot
class ExplainBot(Action):
    def name(self) -> Text:
            return "explain_bot"

    def run(self, dispatcher, tracker, domain):
            
        dispatcher.utter_message(response="utter_bot_name") 
        dispatcher.utter_message(text="Physical activity has significant health benefits for hearts, bodies and minds.")
        dispatcher.utter_message(text="In this session, we will focus on running or walking to stay or become active.")
        dispatcher.utter_message(text="And why should you set a goal for that? Because having a goal is great to stay motivated and focused on what you want to achieve.")
        dispatcher.utter_message(text="We will set a long-term running or walking goal.")
        dispatcher.utter_message(response="utter_long_term")
        return[]

# Introduce bot
class Overview(Action):
    def name(self) -> Text:
            return "overview"

    def run(self, dispatcher, tracker, domain):
            
        dispatcher.utter_message(text="Alright then, let me give you an overview of what we're going to do:")
        dispatcher.utter_message(text="We're going to set a running or walking goal that you would like to achieve.")
        dispatcher.utter_message(text="First, I’ll ask you to think about a running or walking goal that you want to achieve.")
        dispatcher.utter_message(text="This is only to make sure that you have a first idea of the goal that you would like to set.")
        dispatcher.utter_message(text="Next, I will show you some examples of other people to give you an idea of how you can refine your goal.")
        dispatcher.utter_message(text="I will also ask you some details about your goal to make your goal as complete as possible.")
        dispatcher.utter_message(text="And don't worry, before we finalize your goal, we will look at it together and I will give you the chance to make changes if you would like to.")
    
        return[]      

# Display goal type buttons 
class GoalType(Action):
    def name(self) -> Text:
        return "action_goal_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload":'/running{"goal_type":"running"}', "title":"Running 🏃‍♀️"},
            {"payload":'/walking{"goal_type":"walking"}', "title":"Walking 🚶"}
        ]
        dispatcher.utter_message(text="Would you like to set a long-term goal for **running**  or **walking**?", buttons=buttons)

        return []

# Ask first goal
class FirstGoal(Action):
    def name(self) -> Text:
            return "ask_first_goal"

    def run(self, dispatcher, tracker, domain):

        goal_type =  tracker.get_slot('goal_type')
        dispatcher.utter_message(text="Let's think about the " + goal_type + " goal you want to achieve.")
        dispatcher.utter_message(text="Don't worry, this is not your final goal yet! We will also look at some examples of other people later to help you make your goal more specific.")
        dispatcher.utter_message(text="What " + goal_type + " goal would you like to achieve?")
        # dispatcher.utter_message(text="*You could for example mention how long, how far, how often, or where you would like to go " + goal_type + "*.")
    
        return[]      


# Respond on first goal
class GoalResponse(Action):
    def name(self) -> Text:
            return "goal_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        def contains_word(s, w):
            return (' ' + w + ' ') in (' ' + s + ' ') 

        goal_type =  tracker.get_slot('goal_type')
        print(goal_type)
        last_message = (tracker.latest_message)['text']

        dispatcher.utter_message(text="Okay!")

        if contains_word(last_message, 'step') or contains_word(last_message, 'steps'):
            print("word detected step")
            dispatcher.utter_message(text="It's always good to specify the amount that you want to go " + goal_type + ".")
        
        elif contains_word(last_message, 'km') or contains_word(last_message, 'kilometers') or contains_word(last_message, 'kilometres') or contains_word(last_message, 'miles'):
            print("word detected km")
            dispatcher.utter_message(text="It's always good to specify the amount that you want to go " + goal_type + ".")

        elif contains_word(last_message, 'every day') or contains_word(last_message, 'everyday') or contains_word(last_message, 'daily'):
            print("word detected everyday")
            dispatcher.utter_message(text="It's always good to specify how often you want to go " + goal_type + ".")
        
        elif contains_word(last_message, 'marathon'):
            print("word detected marathon")
            dispatcher.utter_message(text="It's great to train for a marathon.")
        
        elif contains_word(last_message, 'minutes') or contains_word(last_message, 'hour') or contains_word(last_message, 'hours'):
            print("word detected duration")
            dispatcher.utter_message(text="It's always good to specify the duration of your physical activity.")
        elif contains_word(last_message, 'around the house') or contains_word(last_message, 'gym') or contains_word(last_message, 'grocery store') or contains_word(last_message, 'street'):
            print("word detected duration")
            dispatcher.utter_message(text="It's always good to specify where you want to go " + goal_type + ".")   
        else:
            print("no word detected")
            dispatcher.utter_message(text="It is good that you have thought about your " + goal_type + " goal.")   

        return[FollowupAction(name="first_example"), SlotSet("goal_type", goal_type)]

# Timer to measure the second example reading time
class Timer(Action):
    def name(self) -> Text:
            return "timer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        end_read2 = time.perf_counter()
        start_time2 = tracker.get_slot('start_time2')
        read_second = int(end_read2 - start_time2)
        print(read_second)

        return[SlotSet("read_second", read_second), FollowupAction(name="opinion2_form")]

# First example
class FirstExample(Action):
    def name(self) -> Text:
            return "first_example"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        goal_type =  tracker.get_slot('goal_type')
        
        metadata = extract_metadata_from_tracker(tracker)
        user_id = metadata['userid']

        goals = pd.read_csv("experiment_data/goals.csv", sep=';', index_col='example')
        user_examples = pd.read_csv("experiment_data/user_examples.csv", sep=';', index_col='id')

        index = user_examples.loc[user_id]['example1']
        intro1 = "🧍* " + goals.loc[index]['introduction']+"*"
        goalhow1 = "**"+"🎯 " + goals.loc[index]['goal'] + " " + goals.loc[index]['how']+"**"
        # intro1 = "\n \"🧍 **Hi, my name is Mary. I tend to define myself as a person with a normal body in terms of weight. Anyway, I am interested in doing physical activities because I think my health would benefit from it.**\""
        # goalhow1 = "\n \" 🎯**I started running for 2 km now I run 4 km. I achieved this by forcing myself to go out running at least 1 time per week.**\""

        start_time1 = time.perf_counter()
        dispatcher.utter_message(text="Now that you have an idea of the goal you want to achieve, let me show you two examples of people who achieved a running or walking goal.")
        dispatcher.utter_message(text="Each person will first introduce themselves 🧍 and then tell you about the goal they achieved 🎯.")
        dispatcher.utter_message(text="Here is how the person from the first example introduces themselves:")
        dispatcher.utter_message(text=intro1)
        dispatcher.utter_message(text="This person achieved the following goal:")
        dispatcher.utter_message(text=goalhow1)

        dispatcher.utter_message(text="Let me know when you finished reading this example!", buttons=[
        {"payload":'/finished_reading', "title":"I have read the first example"}
        ])

        print(start_time1)
        return [SlotSet("start_time1", start_time1)]

# Second example
class SecondExample(Action):
    def name(self) -> Text:
            return "second_example"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        end_read1 = time.perf_counter()
        start_time1 =  tracker.get_slot('start_time1')
        read_first = int(end_read1 - start_time1)

        metadata = extract_metadata_from_tracker(tracker)
        user_id = metadata['userid']

        goals = pd.read_csv("experiment_data/goals.csv", sep=';', index_col='example')
        user_examples = pd.read_csv("experiment_data/user_examples.csv", sep=';', index_col='id')

        index = user_examples.loc[user_id]['example2']
        intro2 = "🧍* " + goals.loc[index]['introduction']+"*"
        goalhow2 = "**"+"🎯 " + goals.loc[index]['goal'] + " " + goals.loc[index]['how']+"**"
        # intro2 = "\n \"🧍 **I'm 21 years old. I've practised volleyball for 7 years until I quit because of my school commitments. Then I've always kept myself trained: I run, walk, went to the gym for a while, but I realised that I prefer running through the streets over running on a treadmill.**\""
        # goalhow2 = "\n \" 🎯**I was able to run 4 km in a row. I achieved this by walking almost every day and started running slowly.**\""

        start_time2 = time.perf_counter()
        dispatcher.utter_message(text="Here is how the person from the second example introduces themselves:")
        dispatcher.utter_message(text=intro2)
        dispatcher.utter_message(text="This person achieved the following goal:")
        dispatcher.utter_message(text=goalhow2)

        dispatcher.utter_message(text="Let me know when you read the example!", buttons=[
        {"payload":'/finished_examples', "title":"I'm done!"}, {"payload":'/finished_examples', "title":"I read the example"}
        ])

        print(read_first)
        return [SlotSet("read_first", read_first), SlotSet("start_time2", start_time2)]

# Ask goal the user wants to achieve (more specific)
class AskGoal(Action):
    def name(self) -> Text:
            return "ask_goal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Thank you for sharing that with me!")
        dispatcher.utter_message(text="Now that you've seen the examples, maybe you have a better idea about what you want to accomplish.")
        dispatcher.utter_message(response="utter_remind_goal")
        dispatcher.utter_message(text="Please review your goal and try to make it as specific as possible.")
        dispatcher.utter_message(text="Making your goal specific is important, because it helps with understanding what exactly you want to achieve.")
        dispatcher.utter_message(text="*Make sure to write down your whole goal again, even if it's the same goal.*")
        
        return[FollowupAction(name="goal_form")]

# Introduction to importance questions
class IntroImportance(Action):
    def name(self) -> Text:
            return "intro_importance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Alright!")
        dispatcher.utter_message(text="You have thought about how to make your goal more specific.")
        dispatcher.utter_message(text="It is also important to set goals that are relevant to you.")
        dispatcher.utter_message(text="To think more about that, let's now look at why this goal is important to you")
        
        return[FollowupAction(name="utter_ask_importance")]

# Introduction to achievability question
class IntroAchievable(Action):
    def name(self) -> Text:
            return "intro_achievable"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Thank you for telling me!")
        dispatcher.utter_message(text="It's great that you thought about why this goal is important to you.")
        dispatcher.utter_message(text="We also want to think about whether your goal is achievable or not, as we want to be sure that you have the time and resources to achieve your goal.")
        dispatcher.utter_message(text="Let's think about how achievable your goal is.")
        
        return[FollowupAction(name="utter_ask_achievable")]

# Answer based on chosen achievability goal
class Achievability(Action):
    def name(self) -> Text:
            return "achievability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        achievability =  tracker.get_slot('achievable')
        
        if achievability == "1" or achievability == "2":
            print("1 or 2")
            dispatcher.utter_message(text="Hmm, if you think your goal is too difficult, it is okay to start with an easier goal.") 
            dispatcher.utter_message(text="Your goal should be realistic to achieve, but challenging enough to keep you motivated.")
            buttons = [
            {"payload":'/change_goal_achievability', "title":"I want to make my goal more achievable"},
            {"payload":'/set_deadline', "title":"I want to keep the goal that I set, I can do this"}
            ]
            dispatcher.utter_message(text="Do you want to change your goal, or are you up for the challenge?", buttons=buttons)
            
        elif achievability == "6" or achievability == "7":
            print("6 or 7")
            dispatcher.utter_message(text="Hmm, it seems like you can easily achieve your goal.")
            buttons = [
            {"payload":'/change_goal_achievability', "title":"I want to make my goal more challenging"},
            {"payload":'/set_deadline', "title":"I want to keep the goal I set, it is challenging enough"}
            ]
            dispatcher.utter_message(text="What do you think of challenging yourself a bit more?", buttons=buttons)
        else:
            print("3-4-5")
            buttons = [
            {"payload":'/set_deadline', "title":"I agree!"},
            {"payload":'/set_deadline', "title":"Yes"}
            ]
            dispatcher.utter_message(text="That seems good.")
            dispatcher.utter_message(text="Setting realistic, achievable goals increases the chance of success.", buttons=buttons)
            # return[FollowupAction("utter_intro_deadline")]

        return []

    
# Change goal or goal deadline
class Change(Action):
    def name(self) -> Text:
        return "change"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        last_message = (tracker.latest_message)['text']
        if last_message == "/goal_change":
            print("if goal")
            dispatcher.utter_message(text="Alright, let's change it.")
            dispatcher.utter_message(text="What is the new goal you would like to set?")
            return [SlotSet("goal", None), FollowupAction(name="goal_form")]
        
        elif last_message == "/deadline_change":
            print("if goal deadline")
            dispatcher.utter_message(text="Alright, let's change it.")
            dispatcher.utter_message(text="What is the new deadline you would like to set?")
            return [SlotSet("deadline", None), FollowupAction(name="deadline_form")]
        
        elif last_message == "/change_goal_achievability":
            print("if goal achievability")
            dispatcher.utter_message(text="Let's do that!")
            dispatcher.utter_message(text="What is the new goal you would like to set?")
            return [SlotSet("achievable", None), SlotSet("goal", None), FollowupAction(name="goal_form")]

        else:
            print("else")
            dispatcher.utter_message(text=last_message)
            return []
   
   # Answer based on given date
    class CheckDate(Action):
        def name(self) -> Text:
                return "check_date"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            last_message = (tracker.latest_message)['text']
            today = datetime.date.today()
            print("Today's date:", today)
            
            for format in ['%d-%m-%Y', '%d/%m/%Y', '%d %m %Y']:
                try:
                    deadline = datetime.datetime.strptime(last_message, format) 
                    print('correct format date')
                    break
                except ValueError as e:
                    print('wrong format date')
                    dispatcher.utter_message(text="Hmm, I didn't quite get that.")
                    dispatcher.utter_message(text="Could you please reformulate the goal deadline you want to set?")
                    return[SlotSet("deadline", None), FollowupAction(name="deadline_form")]
                    break
            
            difference = (deadline.date()-today).days
            print(difference)

            if difference < 7 and difference >= 0:
                print("less than a week later")
                dispatcher.utter_message(text="Hmm, this seems a bit soon. How about setting a new deadline?")
                return[SlotSet("deadline", None), FollowupAction(name="deadline_form")]
            
            elif difference < 0:
                print("in the past")
                dispatcher.utter_message(text="Hmm, it seems like you have set a deadline in the past!")
                dispatcher.utter_message(text="Could you set a deadline in the future?")
                return[SlotSet("deadline", None), FollowupAction(name="deadline_form")]

            else:
                print(deadline)
                print(deadline.date())

            deadline = tracker.get_slot('deadline')

            if difference <= 14:
                
                buttons = [
                {"payload":'/confirm_deadline', "title":"That is correct"},
                {"payload":'/deadline_change', "title":"No, I want to set a different deadline"}
                ]
                dispatcher.utter_message(text="Okay!")
                dispatcher.utter_message(text="So you want to achieve your goal in " + str(difference) + " days by " + str(deadline) + ", is that correct?", buttons=buttons)
                return[]
            
            elif difference > 14 and difference < 70:
                weeks = int(difference / 7)
                buttons = [
                {"payload":'/confirm_deadline', "title":"That is correct"},
                {"payload":'/deadline_change', "title":"No, I want to set a different deadline"}
                ]
                dispatcher.utter_message(text="Okay!")
                dispatcher.utter_message(text="So you want to achieve your goal in around " + str(weeks) + " weeks by " + str(deadline) + ", is that correct?", buttons=buttons)
                return[]

            elif difference > 70:
                months = int(difference / 30)
                buttons = [
                {"payload":'/confirm_deadline', "title":"That is correct"},
                {"payload":'/deadline_change', "title":"No, I want to set a different deadline"}
                ]
                dispatcher.utter_message(text="Okay!")
                dispatcher.utter_message(text="So you want to achieve your goal in around " + str(months) + " months by " + str(deadline) + ", is that correct?", buttons=buttons)
                return[]


    # Save slots to a file
    class Save(Action):
        def name(self) -> Text:
                return "save"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            metadata = extract_metadata_from_tracker(tracker)
            user_id = metadata['userid']
            print(user_id)

            if user_id is None:
                print("User id not found")
                user_id = tracker.sender_id
            
            textfile = open("experiment_data/"+user_id+".txt", "w")
            textfile.write("user_id: " + user_id + "\n")
            textfile.write("mood: " + tracker.get_slot('mood') + "\n")
            textfile.write("goal_type: " + tracker.get_slot('goal_type')  + "\n")
            textfile.write("first_goal: " + tracker.get_slot('first_goal') + "\n")
            textfile.write("goal: " + tracker.get_slot('goal') + "\n")
            textfile.write("importance: " + tracker.get_slot('importance') + "\n")
            textfile.write("importance_why: " + tracker.get_slot('importance_why') + "\n")
            textfile.write("deadline " + tracker.get_slot('deadline') + "\n")
            textfile.write("takeaway: " + tracker.get_slot('opinion2') + "\n")
            textfile.write("start 1: " + str(tracker.get_slot('start_time1')) + "\n")
            textfile.write("reading time 1: " + str(tracker.get_slot('read_first')) + "\n")
            textfile.write("start 2: " + str(tracker.get_slot('start_time2')) + "\n")
            textfile.write("reading time 2: " + str(tracker.get_slot('read_second')) + "\n")
            textfile.close()    

            return[]   

    # Finish the conversation
    class Finish(Action):
        def name(self) -> Text:
                return "finish_conversation"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message(response="utter_goodbye")
            return[]

    class End(Action):
        def name(self) -> Text:
                return "conversation_over"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message(text="*This is the end of the session. Please close this window and return to the questionnaire in Qualtrics.*")
            return[ConversationPaused()]

    # Check length of the user's answer to the take away question
    class CheckLengthOpinion(Action):
        def name(self) -> Text:
                return "check_length_opinion"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            last_message = (tracker.latest_message)['text']

            if (len(last_message) < 25):
                print("too short opinion")
                dispatcher.utter_message(text="Hmm, could you please elaborate a bit more on that?")
                return[SlotSet("opinion2", None), FollowupAction(name="opinion2_form")]
            else:
                return[FollowupAction(name="ask_goal")]

    # Check length of the goal the user has set
    class CheckLengthGoal(Action):
        def name(self) -> Text:
                return "check_length_goal"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            last_message = (tracker.latest_message)['text']

            if (len(last_message) < 25):
                print("too short goal")
                dispatcher.utter_message(text="Hmm, that seems a bit short.")
                dispatcher.utter_message(text="Could you please elaborate a bit more on that?")
                dispatcher.utter_message(text="*Please make sure to write down your whole goal, even if it's the same as before.*")
                return [SlotSet("goal", None), FollowupAction(name="goal_form")]
            else:
                return[FollowupAction(name="intro_importance")]

    # Check length of the user's answer to the importance question
    class CheckLengthImportance(Action):
        def name(self) -> Text:
                return "check_length_importance"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            last_message = (tracker.latest_message)['text']

            if (len(last_message) < 25):
                print("too short importance")
                dispatcher.utter_message(text="Hmm, could you please elaborate a bit more on that?")
                return [SlotSet("importance_why", None), FollowupAction(name="importance_form")]
            else:
                return[FollowupAction(name="intro_achievable")]