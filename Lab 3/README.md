# Chatterboxes
Jesse Iriah

In this lab, we want you to design interaction with a speech-enabled device--something that listens and talks to you. This device can do anything *but* control lights (since we already did that in Lab 1).  First, we want you first to storyboard what you imagine the conversational interaction to be like. Then, you will use wizarding techniques to elicit examples of what people might say, ask, or respond.  We then want you to use the examples collected from at least two other people to inform the redesign of the device.

We will focus on **audio** as the main modality for interaction to start; these general techniques can be extended to **video**, **haptics** or other interactive mechanisms in the second part of the Lab.

### Storyboard

Storyboard and/or use a Verplank diagram to design a speech-enabled device. (Stuck? Make a device that talks for dogs. If that is too stupid, find an application that is better than that.)

\*\***Post your storyboard and diagram here.**\*\*

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/1837c14c-27f3-45f6-8dad-1d43e7cb15a0" />
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/fd82f6ef-4bee-4b0e-9541-86d576e99de2" />
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/c2dbaa11-101d-410a-b331-e9e7d69ded2f" />
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/5610f006-8954-4399-9e3e-72f5519de8ca" />

(Used Gemini Pro to generate Storyboard)

Write out what you imagine the dialogue to be. Use cards, post-its, or whatever method helps you develop alternatives or group responses.

General idea is to help people come up with recipes, so my thought process was thinking in the shoes of when I'm at the fridge, and I don't know what to make. There are times I'm just missing an ingredient or two, or times where I have substitutes that im unaware of.

I have ____, ____, and ____ | Response: Perfect! With these ingredients, you can make ______.

I want to make _____, but i'm missing ____. I currently have ______, _____ ,____ | Response: Okay! Do you have any ____ or ____ on hand? That would be a perfect substitute!

I have ____ and ____ | Response: Hmmm, there's not much you can make with just that. If you go out and get some chicken you could try making some ____!

I'm not really interested in that meal.. | Response: That's okay! What are you feeling? You could also try _____, or let me know what type of food you want and I'll search!


\*\***Please describe and document your process.**\*\*

### Acting out the dialogue
[audioaudio.mp3](https://github.com/user-attachments/files/22711408/audioaudio.mp3)

The initial device acting behaved like I expected. The part that did not go as I expected were the additional features. I added features where it could suggest a meal that would be completable with an additional ingredient. The majority of the time however people aren't interested in going out to buy more ingredients if they're already in the fridge trying to use up leftovers.


# Lab 3 Part 2

For Part 2, you will redesign the interaction with the speech-enabled device using the data collected, as well as feedback from part 1.

## Prep for Part 2

The biggest improvement that could be made is to ensure any misunderstandings are caught. There could be a system in place that would first confirm whether the recorded answer was correct or not. In order to make these confirmations concrete, it will instead use the buttons to confirm, so there is no chance of a misunderstanding.

<img width="212" height="200" alt="image" src="https://github.com/user-attachments/assets/abfbf535-c741-4ac9-9541-15856a6016a7" />
<img width="222" height="196" alt="image" src="https://github.com/user-attachments/assets/56888596-3f92-435e-a5d2-e5cb4d723992" />
<img width="212" height="200" alt="image" src="https://github.com/user-attachments/assets/b1a6d282-3144-42e3-b1e1-f40d1981533e" />
<img width="218" height="197" alt="image" src="https://github.com/user-attachments/assets/c2d7e206-2c1b-4fbd-8882-592640fd075f" />
(Produced using Gemini Pro)


## Prototype your system

The system should:
* use the Raspberry Pi
* use one or more sensors
* require participants to speak to it.

*Document how the system works*
https://youtube.com/shorts/8JGa3FmGa5I
https://youtube.com/shorts/8JGa3FmGa5I


## Test the system
Try to get at least two people to interact with your system. (Ideally, you would inform them that there is a wizard _after_ the interaction, but we recognize that can be hard.)

Answer the following:

### What worked well about the system and what didn't?
The system worked well in the sense that it produced a satisfactory response when given a list of ingredients, but it suffered under the consequences of using the onboard AI system. When producing the recipe, it often took a couple minutes to fully complete the recipe.

### What worked well about the controller and what didn't?
The controller worked well in terms of having clear buttons to describe how to activate/deactivate the mic for voice recording. The recording was sometimes inaccurate, but that is why I added the feature to re-record.

### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?
I could use my system to see what ingredients users are most often listing out when looking for recipes. Another dataset I could keep track of is what recipes users often choose to opt over and reproduce recipes, compared to which recipes users are satisfied with. This could then be used to alter priorities of different recipes and build a database of ideal recipes.






