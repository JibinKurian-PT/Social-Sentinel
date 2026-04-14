# 🛡️ Social Sentinel: Business User Guide
### The Executive's Guide to Real-Time Brand Intelligence

Welcome to **Social Sentinel**. In today’s fast-paced digital world, your brand's reputation can change in the blink of an eye. This system is designed to be your "digital eyes and ears," monitoring social media 24/7 and giving you clear, actionable insights without requiring you to look at a single line of code.

---

## 📋 Table of Contents
1.  [What is Social Sentinel?](#section-1-what-is-social-sentinel)
2.  [What You Need Before Starting](#section-2-what-you-need-before-starting)
3.  [One Command to Start Everything](#section-3-one-command-to-start-everything)
4.  [How to Access the Dashboard](#section-4-how-to-access-the-dashboard)
5.  [How to Import Your Own Data (Kaggle)](#section-5-how-to-import-your-own-data-from-kaggle)
6.  [How to Watch Real-Time Data](#section-6-how-to-watch-real-time-data)
7.  [Understanding the Alerts](#section-7-understanding-the-alerts)
8.  [How to Stop the System](#section-8-how-to-stop-the-system)
9.  [Troubleshooting Common Problems](#section-9-troubleshooting-common-problems)
10. [Presenting to Your Company](#section-10-presenting-to-your-company-or-evaluators)
11. [Quick Reference Card](#section-11-quick-reference-card)
12. [Glossary of Simple Terms](#section-12-glossary-of-simple-terms)
13. [Getting Help](#section-13-getting-help)
14. [File Locations for Advanced Users](#section-14-file-locations-for-advanced-users)

---

## SECTION 1: What is Social Sentinel?

### The "Security Camera" for Your Brand
Imagine you have a high-tech **security camera system** installed for your brand’s reputation. 

In a physical store, a security camera watches for theft or safety hazards. **Social Sentinel** does the same for the digital world. Instead of watching a door, it watches the massive, swirling ocean of social media. It detects "reputational hazards" before they catch fire and spread.

When someone tweets about your product or leaves a comment on your YouTube video, Social Sentinel "hears" it instantly. But it doesn't just listen—it *feels*. Every single post is analyzed by our sophisticated AI Brain (built on the powerful BERT model, for those who want to know the "engine" type). This AI identifies the emotion behind the words.

*   **Positive Sentiment:** These are your fans. They are your best marketing tool. Social Sentinel helps you identify who they are and what they love so you can do more of it.
*   **Negative Sentiment:** These are your warnings. A negative post isn't just a complaint; it's a data point. When dozens of people start saying the same negative thing, Social Sentinel sounds the alarm so you can fix the issue before it appears on the evening news.

### Why Real-Time Matters
In the old days of business, you might wait for a "Quarterly Customer Survey" to find out people were unhappy. By then, they've already stopped buying your product. Social Sentinel works in **Real-Time**. This means if a batch of products is defective and people start complaining at 10:00 AM, you know about it by 10:05 AM. That 2-day or 2-week head start is the difference between a minor hiccup and a brand disaster.

---

## SECTION 2: What You Need Before Starting

Setting up a powerful AI system used to take a team of scientists months. We have refined this so you can do it on your laptop in your home office.

### Hardware Requirements
*   💻 **Memory (RAM):** 8GB is the minimum. Think of RAM as the "workspace" for the AI. If you have 16GB or more, the charts will render even faster.
*   🖥️ **Operating System:** Whether you are a Mac lover, a Windows power user, or a Linux enthusiast, Social Sentinel works for you.
*   💾 **Storage:** Ensure you have about 5GB of free space. The AI models we use are a bit large because they are "smarter" than standard apps.

### Software Requirements (The "Containers")
Because Social Sentinel is made of many moving parts (the AI engine, the database, the dashboard), we use a tool called **Docker** or **OrbStack**. 
Think of this like a "Shipping Container." Instead of you having to install 10 different complicated pieces of software, we put them all in one container. You just "load the container" onto your computer, and it works.
*   **Recommendation:** If you are on a Mac, download **OrbStack** from orbstack.dev. It’s easier for non-technical users.

### The Human Requirement
*   **No Coding Needed:** You do not need to know how to write code.
*   **Curiosity:** You just need to be someone who wants to understand their customers better. 
*   **Setup Time:** Allow **30 minutes** for the first time. The system needs to download the "AI Brain" (the BERT model) from the internet. Once that's done, future starts will only take 2 minutes.

---

## SECTION 3: One Command to Start Everything

We know your time is valuable. You shouldn't have to fiddle with settings. We have created a "One-Touch Start."

### The "Terminal" (Your Magic Wand)
Every computer has a "Terminal" (Mac) or "PowerShell" (Windows). It looks like a simple black box where you type text. This is your direct line to the project's engine.

### Step-by-Step Launch:
1.  **Placement:** Make sure your `sentiment-system` folder is on your **Desktop**.
2.  **Open Terminal:** Search for it in your apps.
3.  **The "Move" Command:** Type `cd Desktop/sentiment-system` and hit Enter. This tells the terminal, "Look inside this folder."
4.  **The "Start" Command:** Type `make run` and hit Enter.
5.  **The Wait:** You will see lines of code flying by like the movie "The Matrix." This is the system building your brand monitor. 
    *   **Wait until the scrolling slows down.** Usually 2 to 3 minutes.
    *   If you see "Successfully started," you are ready!

---

## SECTION 4: How to Access the Dashboard

This is where you see the results. Social Sentinel works just like a website on your local machine.

### Your Address
Open your browser (Chrome or Safari) and type:
`http://localhost:8501`

### A Tour of the Command Center:

#### 1. 📊 The Overview Page (The "Executive Summary")
When you walk into a boardroom, this is the page you show first. It answers the question: "How are we doing right now?"
*   **KPI Cards:** Total posts analyzed, total happy users, total angry users.
*   **Sentiment Trend:** A beautiful line graph. If the line is going up, your brand is in a "Good Mood." If it’s dipping, you have work to do.

#### 2. 📉 The Sentiment Page (The "Mood Meter")
This page goes deeper than just "Happy or Sad." 
*   **Sentiment Distribution:** A pie chart showing the exact balance.
*   **Confidence Meter:** Our AI is honest. It tells you how "sure" it is about each post. If the confidence is high, you can trust the data implicitly.
*   **Historical Comparison:** Compare today’s mood to the 30-day average.

#### 3. ☁️ The Topics Page (The "Voice of the Customer")
This is often the most valuable page. It answers: "What is the problem?"
*   **Word Clouds:** Imagine a giant cloud of words. If the word "DELAY" is the biggest, your logistic team needs a call. If "AMAZING SERVICE" is the biggest, your staff deserves a bonus.
*   **Clustering:** The AI groups similar thoughts. It realizes that "too slow," "waiting forever," and "delay" all mean the same thing.

#### 4. 🗺️ The Geo Map Page (The "Global Pulse")
For companies operating in multiple cities or countries, this is your map to the world.
*   **Heat Mapping:** See a map of the world. Green markers appear where people are happy. Red markers appear where people are complaining.
*   **Targeted Strategy:** If you see a cluster of Red in California but Green in Texas, you can narrow your focus to solve the California-specific issue.

#### 5. 📟 The Real-Time Page (The "Live Feed")
This is the "Wow Factor" page. 
*   It shows a scrolling feed of social media posts.
*   Each post is color-coded the moment it arrives.
*   It’s like watching a live news ticker specifically about your company.

---

## SECTION 5: How to Import Your Own Data from Kaggle

Sometimes you want to practice or run a "Simulation." We have made this easy by connecting to **Kaggle**, the world’s largest library of data.

### Why Airline Data?
Airlines are the most commented-on businesses in the world. We’ve pre-configured a tool to import **14,640 tweets** about US Airlines. This is the perfect "playground" to see how Social Sentinel handles a crisis.

### The Import Process:
1.  **Kaggle Token:** Create an account at kaggle.com. Download your `kaggle.json` key (search "API" in your settings).
2.  **The Drop:** Put that file into the `sentiment-system` folder.
3.  **The Trigger:** In your terminal, type:
    `python scripts/import_airline_data.py`
4.  **The Result:** Switch back to your dashboard. You will see the "Real-Time" feed explode with 14,000 airline tweets, and your "Topics" page will start showing words like "Flight," "Cancel," and "Baggage."

---

## SECTION 6: How to Watch Real-Time Data

When you have the **Real-Time** page open, you are seeing the system's "Heartbeat."

### Visual Cues for You:
*   🟢 **The "Happy High":** When you see a stream of green cards, your marketing campaign is working.
*   🔴 **The "Negative Surge":** If you see five red cards in a row, a specific event just happened. Check the text on the cards immediately.
*   🏎️ **The Speedometer:** We have a gauge at the top that moves like a car’s speedometer. If it stays in the "High Green" zone, your brand is healthy.
*   📈 **The Ticker:** Watch the volume chart. Is the number of people talking about you increasing? A sudden spike in volume (even if sentiment is neutral) usually precedes a major news event.

---

## SECTION 7: Understanding the Alerts

You don't have to stare at the dashboard all day. Social Sentinel has an "Auto-Alert" system.

| Alert Level | Meaning | Example Scenario |
| :--- | :--- | :--- |
| **🟢 GREEN** | **Healthy** | "Business as usual. Positive sentiment is 80%." |
| **🟡 YELLOW** | **Caution** | "Sentiment is dropping. People are mentioning 'Software Bug'." |
| **🔴 RED** | **Crisis** | "EMERGENCY: Negative sentiment exceeds 40%. Possible PR crisis detected." |

**The Strategy:** When you see a **Red Alert**, click over to the **Topics Page**. Find the largest red word in the word cloud. That is the "Root Cause" of your crisis. Call the head of that department.

---

## SECTION 8: How to Stop the System

To save your computer's energy, shut down the system when you're done.

1.  Go to the Terminal window.
2.  **The "Stop" Key:** Press **Control and C** at the same time. This tells the system, "Stop processing new data."
3.  **The "Clean Up" Command:** Type `make docker-down` and press Enter. This tells the containers to pack up and "go home." 
    *   *This clears your computer's memory so other apps can run fast again.*

---

## SECTION 9: Troubleshooting Common Problems

Even the best systems have hiccups. Here is your cheat sheet.

*   **"My Dashboard is empty!"**
    *   AI takes time to process. Wait 60 seconds. Make sure you actually have data coming in (did you run the Kaggle script?).
*   **"I see 'Port 8501 is already in use'."**
    *   This happens if you didn't run `make docker-down` last time. Restarting your computer is the simplest "Non-technical" fix.
*   **"I see a 404 Error page."**
    *   Your Docker/OrbStack whale might be sleeping. Open the OrbStack app and make sure it says "Ready."
*   **"The text in the terminal is red!"**
    *   Red text usually means a connection error. Run `make doctor` to find out what's wrong.

---

## SECTION 10: Presenting to Your Company

Want to impress your boss or a group of investors? Use this 10-minute presentation plan:

**Phase 1: The Status Check (0-2m)**
"Welcome. This is our Social Sentinel dashboard. As you can see on the **Overview** page, our overall brand sentiment is 72%. We are currently tracking 5,000 active conversations."

**Phase 2: The Action Demo (2-5m)**
"Now, watch the **Real-Time** page. I'm going to start importing new customer feedback from the airline sector. (Start the script). You can see the AI instantly classifying these as positive or negative. Every red card you see is a customer we can potentially save."

**Phase 3: The Insight Discovery (5-8m)**
"Why are we getting these red cards? Let's check the **Topics** page. Look at the word cloud. 'Customer Service' is our biggest pain point today. We can now provide this data to that team specifically."

**Phase 4: The Strategic Wrap (8-10m)**
"In summary: We no longer wait for weekly reports. We see problems as they happen. Social Sentinel gives us a competitive edge by allowing us to be the most responsive company in our industry."

---

## SECTION 11: Quick Reference Card

*   **To START:** `make run`
*   **To VIEW:** Go to `http://localhost:8501`
*   **To TEST:** `python scripts/import_airline_data.py`
*   **To CHECK HEALTH:** `make doctor`
*   **To STOP:** `Ctrl+C` then `make docker-down`

---

## SECTION 12: Glossary of Simple Terms

*   **Sentiment:** The "Mood" of the post.
*   **BERT:** The name of the AI "Brain" we use (developed by Google).
*   **Container:** A package that holds all the software parts so you don't have to install them manually.
*   **Word Cloud:** A picture made of words where bigger words are more common.
*   **localhost:** A fancy name for "This computer."

---

## SECTION 13: Getting Help

If you're stuck:
1.  Check the `logs/app.log` file—it’s like a plane's "Black Box."
2.  Run `make doctor`.
3.  Contact your internal development team and tell them "The Docker daemon isn't responding." This makes you sound very smart!

---

## SECTION 14: File Locations for Advanced Users

*   🔑 **Secret Keys:** `.env` file (Be careful! Don't share this).
*   📦 **Data Storage:** `data/raw/` (Where the raw social posts are stored).
*   📋 **The 'Black Box':** `logs/app.log`.
*   📬 **Output:** `reports/` folder for any exported data.

---

**Social Sentinel** — *Modern Intelligence for Modern Brands.* 🛡️
