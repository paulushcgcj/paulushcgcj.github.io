---
title: "The Mathematics of the Unknown - How to Estimate Greenfield Software Without Guessing"
date: 2026-07-16 12:00:00 -0700
lastupdated: 2026-07-21 12:32:00 -0700
categories: ["article", "tech", "engineering", "estimation", "agile"]
author: paulushc
license: CC-BY-4.0
description: "Replace Planning Poker guesswork with grounded estimation. Four pillars using PERT, complexity counting, codebase analogies, and pre-mortems."
image: /assets/2026/07/mathofunknow01-cover.png
permalink: /articles/mathematics-of-the-unknown
has_bibliography: true
scholar:
  bibliography: mathematics-of-the-unknown
header:
    teaser: /assets/2026/07/mathofunknow01-cover.png
    overlay_image: /assets/2026/07/mathofunknow01-cover.png
    overlay_filter: 0.5
    show_overlay_excerpt: false
resources:
    - title: "The Mathematics of Technical Debt"
      url: "/articles/mathematics-of-technical-debt"
      icon: "arrow_forward"
    - title: "Fechner, G. T. (1860). Elemente der Psychophysik"
      url: "https://archive.org/details/elementederpsych001fech"
    - title: "Cohn, M. (2005). Agile Estimating and Planning"
      url: "https://www.mountaingoatsoftware.com/books/agile-estimating-and-planning"
    - title: "Kahneman, D., & Tversky, A. (1979). Intuitive prediction: Biases and corrective procedures"
      url: "https://doi.org/10.1017/CBO9780511809477.031"
    - title: "Buehler, R., Griffin, D., & Ross, M. (2002). Inside the planning fallacy"
      url: "https://doi.org/10.1017/CBO9780511808098.016"
    - title: "Developex. (2023). Time & Material Estimation Guide for Software Projects"
      url: "https://developex.com/blog/time-material-estimation-guide/"
    - title: "Weiss, D. M., & Basili, V. R. (1978). Evaluating Software Development by Error Analysis"
      url: "https://apps.dtic.mil/sti/tr/pdf/ADA062922.pdf"
    - title: "McCabe, T. J. (1976). A Complexity Measure"
      url: "https://doi.org/10.1109/TSE.1976.233837"
    - title: "Flyvbjerg, B. (2006). From Nobel Prize to Project Management"
      url: "https://doi.org/10.1177/875697280603700302"
    - title: "Klein, G. (2007). Performing a Project Premortem"
      url: "https://hbr.org/2007/09/performing-a-project-premortem"
---

Every engineering team has sat in a synchronous Planning Poker session, staring at a Jira ticket for a feature that doesn't exist yet. The Product Owner reads the acceptance criteria. The Scrum Master asks for estimates. 

<!--more-->


Three developers immediately throw down a "5". One senior developer throws down a "13". 

*"Why a 13?"* the team asks.
*"I just feel like the payment integration is going to be a nightmare,"* the senior developer replies.

The estimation devolves into a debate of feelings.

Estimating code that *already exists* is a topology problem; we can measure it. Estimating code that *doesn't exist* is a prediction problem under uncertainty. "Feelings" are not a methodology.

This article covers the psychophysics of why teams use Fibonacci, the statistical reasons "gut feelings" fail, and a generalized, empirically validated framework to ground estimates in structural reality, without relying on historical data that becomes stale.

## The Psychophysics of Fibonacci: Why 13 is a Red Flag

The Fibonacci sequence (1, 2, 3, 5, 8, 13, 21...) is not an arbitrary Agile tradition. Its effectiveness is rooted in a psychophysical principle called the **Weber-Fechner Law**.

### The Weber-Fechner Law

This law {% cite fechner1860elemente %} states that human perception of magnitude is *logarithmic*, not linear. We can distinguish between 1kg and 2kg, but we struggle to distinguish between 51kg and 52kg. The just-noticeable difference is proportional to the baseline magnitude.

**What this means for estimation:**
*   The gap between 1 and 2 is 100%. A developer can confidently distinguish a "1" task from a "2" task.
*   The gap between 5 and 8 is 60%. The distinction is harder, but still meaningful.
*   The gap between 8 and 13 is 62.5%. On a logarithmic scale, this jump is nearly identical to the gap between 5 and 8 (60%). The human eye perceives these as similar steps in magnitude. At this point, the uncertainty band of the estimate overlaps with the next number. 

This is why the golden rule of Agile, **"anything above 8 must be broken down,"** is statistically sound. Above 8, the variance in human estimation exceeds the gap between the numbers. A "13" could be an "8" or a "21". The signal-to-noise ratio collapses. A team voting 13 is signaling panic, not estimating.



## The Statistical Failure Modes: Why "Feelings" Fail

When teams estimate new features, they fall prey to well-documented cognitive biases. Understanding these biases is the first step to building a framework that counteracts them.

### 1. The Planning Fallacy {% cite kahneman1979intuitive %}

Humans systematically underestimate the time required to complete tasks, even when they have prior experience with similar tasks. The brain constructs a "best-case scenario" simulation (the happy path) and mistakes it for a prediction.

A meta-analysis by {% cite buehler2002inside %} found that only **25-30% of projects** are completed within their estimated time.

### 2. The Optimism Bias in Integration

When estimating a new feature, developers think in terms of the *new abstractions*: the new API endpoint, the new React component, the new database table. They systematically underestimate the **integration glue**:
*   Error handling and edge cases
*   Migration scripts
*   Test infrastructure setup
*   Cross-team API contracts

Industry consensus and empirical estimation studies consistently show that integration, error handling, and testing routinely consume **40–60%** of actual development time, despite initial estimates typically allocating only **15–20%** to these phases due to optimism bias.

---

## The General Solution: 4 Pillars of Grounded Estimation

If we cannot measure the CCN of non-existent code, and we don't want to rely on stale historical databases, what *can* we measure? We measure the **structural dimensions of the requirement** and the **topology of similar existing code**.

### Pillar 1: Complexity Driver Counting

Since you cannot measure the CCN of non-existent code, you measure the **number of new abstractions** the feature requires. Every new abstraction is a unit of uncertainty.

**The Complexity Driver Taxonomy:**
1.  **New Data Models:** New tables, entities, or domain objects.
2.  **New API Contracts:** New endpoints, GraphQL resolvers, or message schemas.
3.  **New UI States:** New screens, modals, or state machines.
4.  **New Integrations:** Touching external systems you don't control (Stripe, SendGrid).
5.  **New Infrastructure:** CI/CD, feature flags, DB migrations.

**The Protocol:**
Before assigning a Fibonacci number, count the drivers.
*   1-2 drivers = "1" or "2"
*   3-4 drivers = "3" or "5"
*   5-6 drivers = "8"
*   7+ drivers = **Must decompose**

This transforms *"I feel like this is a 5"* into *"This has 4 complexity drivers, which structurally maps to a 5."*

### Pillar 2: Codebase Analogies (The Topology Mirror)

If the code doesn't exist yet, find the code that is *most similar* to what you are about to build. 

If you are asked to estimate a new "User Subscription" feature, do not estimate it in a vacuum. Look at your existing "User Profile Update" feature. Run your static analysis tools (like `lizard`) on the existing analog. 

Calculate the baseline effort of the analog code (using NLOC and CCN). Apply a **Greenfield Uncertainty Multiplier** (1.3x to 1.5x) as a starting point, then calibrate it against your team's actual integration overhead. Every codebase absorbs glue differently. The analog is already built; you know its shape. The new code carries that same base effort, plus the unknowns the analog has already absorbed.

### Pillar 3: PERT Estimation (Quantifying the Unknown)

Instead of asking for one number, ask for three. This converts a "feeling" into a probability distribution.

*   **Optimistic (O):** Everything goes perfectly.
*   **Most Likely (M):** Normal day, normal bugs.
*   **Pessimistic (P):** Integration fails, edge cases explode.

**The PERT Formula:**
$$ \text{Expected} = \frac{O + 4M + P}{6} $$

If a developer "feels" a feature is a 5, but their Pessimistic estimate is a 13, the wide gap tells the team: *"We don't understand the integration well enough to estimate this."* The correct action is not to assign a number, but to schedule a **spike** (a time-boxed research task).

### Pillar 4: The Pre-Mortem (Simulating Failure)

Before finalizing the poker vote, the team spends 2 minutes on a structured exercise:
1.  Assume the feature took **3x longer** than estimated.
2.  Every team member writes down *why* it took so long.
3.  Identify the top 3 reasons.

This is the antidote to the Planning Fallacy. It forces the brain to simulate failure, surfacing the hidden integration glue that was ignored in the happy-path estimation.

---

## The Synchronous Poker Protocol

How do we synthesize this into a meeting? We change the order of operations.

**The Old Way:**
1. Read ticket.
2. Reveal cards.
3. Debate the highest number.

**The Grounded Way:**
1. **Pre-Read (Agent-Assisted):** Before the meeting, an AI agent analyzes the ticket, counts the Complexity Drivers, finds an analog in the codebase, and generates a 1-page "Pre-Poker Briefing" highlighting the unknowns.
2. **Read & Review:** The team reads the ticket and the Pre-Poker Briefing.
3. **Pre-Mortem (2 mins):** "If this takes 3x longer, why did it happen?"
4. **Reveal Cards:** The team votes.
5. **Converge:** If the variance is high (e.g., a "3" and an "13"), the senior developer explains their PERT Pessimistic view. If the unknowns are too high, the ticket is broken down or spiked.

## Conclusion

Estimating greenfield software does not require guesswork. Respecting the logarithmic nature of human perception (Fibonacci), counting the structural abstractions (Complexity Drivers), mirroring existing topology (Codebase Analogies), and simulating failure (Pre-Mortems) replace "feelings" with defensible, structured analysis.

Measure the dimensions of the unknown.
