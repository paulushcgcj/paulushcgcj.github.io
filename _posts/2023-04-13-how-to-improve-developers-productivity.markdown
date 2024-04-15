---
title:  "How to Improve Developer's Productivity"
date:   2023-04-13 12:00:00 -0700
categories: [article, softskill, repost, encora]
author: paulushc
permalink: /articles/how-to-improve-developers-productivity
header:
    teaser: /assets/2023/04/articles/productivity-cover.jpeg
    overlay_image: /assets/2023/04/articles/productivity-cover.jpeg
    overlay_filter: 0.5
    show_overlay_excerpt: false
---
It's common for developers to spend most of their day between meetings, team syncing, or being interrupted by other team members without any intention to undermine their productivity. This is the reality for most developers these days and has nothing to do with the world of working from home, it happens in the office too. In this article, we’ll share some practices and techniques for keeping tasks on time while supporting the entire team and creating a healthy routine that can benefit developers individually and their teams.
The idea behind this article is to share some tips and start some discussions on what improves and reduces productivity for developers. It’s a compilation of experiences from various developers that have helped them during their careers.

<!--more-->

>  This is a repost from an article that I wrote for [Encora](https://www.encora.com/). You can check the original post [here](https://www.encora.com/insights/how-to-improve-developers-productivity).

# What Does Productivity Mean?

According to the Oxford Dictionary definition:

> **Productivity (noun)**
  The rate at which a worker, a company, or a country produces goods, and the amount produced, compared with how much time, work, and money is needed to produce them.

In Layman’s terms, productivity is the rate at which you output what you receive as input. For a developer, it could be the rate you fix bugs or implement new features; for a Sys Admin, it could be how quickly your tickets are resolved. But no matter what your role is, you have an idea of what productivity means to you, but are you sure this is what you’re supposed to do?

It is all connected to what our responsibilities are, and they change with time and seniority. A junior developer, for example, will get more practical tasks like bug fixing, but a senior developer may spend most of their time advising other team members, helping define and enforce code standards, discussing new features, etc. Using a developer as an example (but the same applies to any skilled worker), the responsibilities and the time spent discussing things will increase along with the seniority of the position, and with that, more time in meetings and less time on the battlefield.

# Productivity Train
To gain productivity, you must first understand what is expected of you as an output. Here is an example based on a junior X, a lead developer. Remember that this is only an example and cannot be considered as a law written in stone. 

As a junior developer, you will be expected to participate in most of your team's routines and meetings. Being a member of the Agile team that uses SCRUM, you are expected to participate in daily meetings, reviews, and plannings because your input and feedback are as important as anyone else's. You can skip a few discussion meetings but remember that discussions related to the topic you’re working on are always relevant.

For a lead developer, most of your time will likely be spent between meetings. You are expected to guide and take technical decisions to ensure the project is on time and aligned with the expected architectural definition. You attend all (or almost all) of your team meetings, be part of all discussions and checkpoints, and are responsible for keeping the machine running.

Again, this is just an example, and can (and likely will) change from project to project, industry to industry, and is only meant to set some seniority-level expectations, so take it with a grain of salt.

# The Calendar Loophole
For most of us, opening a calendar and seeing an ocean of meetings can be overwhelming. We tend to think of it as a waste of precious time, but the hard truth is that reworking something costs more than doing it once the way it was supposed to be, and meetings (good ones) help define what is expected, thus saving precious development time.

It’s not unusual to have meetings just to check if your team needs help or other kind of information, which only creates noise and blocking progress. It can and will happen in a lot of scenarios, like when dealing with time-sensitive or cornerstone tasks and it is the senior/lead’s role to represent the team in these situations so the rest of the team can focus on what they are doing. At the same time, the senior/lead developer is the one who should communicate with the development team to ensure any issue or blocker is addressed before it becomes a huge problem. Being involved with what your team is doing is something that will save you and your team many hours.

# Recipe for Success
Now let's focus on discussing what can be done to improve productivity by addressing some points and using the experience of others and what has been done to address those points. Use this article as the starting point for discussion, the idea here is to start a discussion and create a feedback loop to help others improve their daily routines as well.

# Own Your Time
If someone sends you an invitation to an event or meeting, does it block your calendar? If so, you're letting other people control your time, and that’s not ideal. But that’s what we usually expect, and we've been conditioned to do that, but there is a solution to it.

Block your calendar for times when you need to focus or need to be away for a while. Add an out-of-office event in your calendar to block some time and set it to reply with a refusal to other events. This helps you block some time during your day to do what you need do. Some people use this approach for things such as picking up and dropping their kids at school, medical appointments, or even for their lunchtime.

Not everyone will respect this blocking, but this is something that can be discussed and set in place. You will be able to prevent most of the events, but there will always be some urgent meetings that will require your attention, and for this, people can always ping you on chat to let you know that something is going on and they need you as soon as possible.

# Have a Break
Remember that [KitKat ad that used to air on TV](https://www.youtube.com/watch?v=GC1igm9BcCs)? Yeah, that's true. Have some time to have a break, even if it's just for 5 minutes. Get up, go check your window, get a new cup of coffee, and try not to focus for a few minutes. This will help you focus more later than you think. [The Pomodoro technique](https://en.wikipedia.org/wiki/Pomodoro_Technique) can be helpful, as having some sporadic breaks will make you more productive. Check this article on [Psychology Today](https://www.psychologytoday.com/us/blog/changepower/201704/how-do-work-breaks-help-your-brain-5-surprising-answers) to learn more. 

# Plan by Taking Notes
It can be frustrating to stop what you're doing to join a conversation about a completely different topic, but often you will have to pause your work to do something else, like, going to the restroom, joining a morning meeting, or helping your peer solve a blocker, and for most people, doing this will make them lose their focus and their line of thoughts. 

One suggestion gathered from people that work with a lot of tasks in parallel is to keep notes. For example, when coding, start by planning what are the steps needed to achieve what is required, take notes in your code using comments as if it were a notepad, and express what is expected for that piece of code once is done.

```java
public String updateAndGetTransaction(Long id, BobIsYourUncle receivedDTO){

    // Load data if exists
    // Fail if does not exist
    // Update required fields
    // Save on database
    // Get the transaction ID
    return StringUtils.EMPTY;

}
```

You could be thinking now, **__that's too simple to work!__** But the simple things are usually the most effective. This will not only help you revert to this task in the future, but it will also help you understand whether what you should be doing makes sense, and if the order in which you should do it makes sense. Keep these comments while you code just to remind yourself what you're doing, and once you're done, if this specific piece of code requires more comments to be clear, refactor it, and always remember the [K.I.S.S principle](https://www.interaction-design.org/literature/article/kiss-keep-it-simple-stupid-a-design-principle).

# Sharing is Caring
The next piece of advice  is to share whenever possible. When you're on a team with other professionals, regardless of their seniority level, you will find yourself (or someone else) with more tasks than others, and this time is the perfect opportunity to exercise delegation. Sharing your workload with someone that's free or less overwhelmed shows that you trust that person to complete that task. This is especially important to do with entry-level developers as it helps them boost their confidence and level up their skills. Sometimes you will think that this will make things take much longer than you thought they would if you do it yourself, but as our moms used to say, sharing is caring, and even if you have to take breaks to explain or help someone else complete the task, it shows them that you're here for them in case they need and you also know that they are competent enough to do so, and this will make them better developers, creating persons who understand that they can trust others, but more importantly, will push them forward.

# Time is a Commodity
Time is a thing that once used is lost forever. This is the main reason why we need to use it carefully. We usually plan how much time we take to complete a task because the more time you spend on it, you realize that some things usually take a certain amount of time to complete, and you know how to plan for that, but don't always expect things to go smoothly. It is wise to plan and add some extra time to compensate for unexpected things. A good way to plan time for your tasks is to play [planning poker](https://en.wikipedia.org/wiki/Planning_poker), something that will exercise not only your prediction skills but also your other soft skills as well. And remember, you always plan the amount of time it takes to complete a task based on the worst-case scenario AND use someone else as responsible. You can complete that task in 4 hours, but most of your team members could take at least twice that time, so plan and think that you won't be the one doing it, it is always better to be safe than sorry.

# Final Considerations
These are just some tips to help you organize your day and be more productive, try to apply what you've learned in small steps, not taking this as the holy grail or some kind of law. The idea behind this article is to be a starting point for discussions on what can be done to improve your day, and a lot of those things can be applied outside the professional scope as well. Productivity means a lot of different things to a lot of different people and is usually measured differently, so understanding what it means to you is more important than trying to behave differently because of what others are doing. 