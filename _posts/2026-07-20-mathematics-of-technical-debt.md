---
title:  "The Mathematics of Technical Debt - How to Empirically Estimate Refactoring and Testing Effort"
date:   2026-07-20 08:50:00 -0700
lastupdated: 2026-07-21 11:48:00 -0700
categories: ["article", "tech", "engineering", "estimation", "refactoring"]
author: paulushc
license: CC-BY-4.0
permalink: /articles/mathematics-of-technical-debt
header:
    teaser: /assets/2026/07/math-of-tech-debt.png
    overlay_image: /assets/2026/07/math-of-tech-debt.png
    overlay_filter: 0.5
    show_overlay_excerpt: false
resources:
    - title: "The Mathematics of the Unknown"
      url: "/articles/mathematics-of-the-unknown"
      icon: "arrow_back"
    - title: "A Complexity Measure (McCabe, 1976)"
      url: "https://ieeexplore.ieee.org/document/1702388"
      icon: "book"
    - title: "lizard — Code Complexity Analyzer"
      url: "https://github.com/terryyin/lizard"
      icon: "code"
    - title: "Cyclomatic Complexity Density and Software Maintenance Productivity (Gill & Kemerer, 1991)"
      url: "https://dl.acm.org/doi/10.1109/32.106988"
      icon: "book"
    - title: "Cognitive Complexity — SonarSource"
      url: "https://www.sonarsource.com/resources/cognitive-complexity/"
      icon: "link"
    - title: "Technical Debt Quadrant — Martin Fowler"
      url: "https://martinfowler.com/bliki/TechnicalDebtQuadrant.html"
      icon: "link"
    - title: "Cyclomatic Complexity — Incus Data (upper-bound property, CC value ranges)"
      url: "https://incusdata.com/blog/cyclomatic-complexity"
      icon: "link"
    - title: "Is Cyclomatic Complexity Really Related to Branch Coverage? — Mark Seemann"
      url: "https://blog.ploeh.dk/2023/05/08/is-cyclomatic-complexity-really-related-to-branch-coverage/"
      icon: "link"
    - title: "Coding on Copilot: 2023 Data Shows Downward Pressure on Code Quality — GitClear"
      url: "https://www.gitclear.com/coding_on_copilot_data_shows_ais_downward_pressure_on_code_quality/"
      icon: "link"
    - title: "Pareto Principle — Investopedia"
      url: "https://www.investopedia.com/terms/1/80-20-rule.asp"
      icon: "book"
---

Most engineering teams have faced this scenario: Product Management asks for an estimate to refactor a legacy module or add test coverage to a critical service. The senior developer stares at the screen, squints at the nested `if` statements, and says, *"I don't know, maybe a week?"*

<!--more-->

Gut-feeling estimation undermines reliable reporting. We underestimate the "blast radius" of tightly coupled code, and we overestimate the time required to write tests for simple, isolated logic.

The first article in this series, *The Mathematics of the Unknown*, tackled the inverse problem: estimating work on code that doesn't exist yet. It introduced the Complexity Driver Taxonomy, Codebase Analogies, and PERT estimation as structured alternatives to Planning Poker guesswork. Those tools work because they measure the *dimensions of the requirement* before a single line of code is written.

This article picks up the other side of the coin. When the code already exists and needs to be refactored or tested, the requirement dimensions are no longer the bottleneck. The bottleneck is the code's internal structure: its size, its branching complexity, and how those properties translate into hours of work. We can measure the *topology* of the code and derive the effort required to change it mathematically.

This article explores how to use static analysis, specifically Net Lines of Code (NLOC) and Cyclomatic Complexity (CCN), to build a calibrated model for estimating refactoring and testing time. It covers the mathematics, analyzes real-world code examples in Java and TypeScript, is honest about where the model's numbers come from and where they break down, and establishes a framework you can automate today.

## Scope of This Model: In-Place Refactoring Only

Before you apply these formulas in a planning meeting, it is worth being explicit about what this model does **not** cover.

The formulas in this article assume the code being estimated already lives in its native environment — same language, same framework, same architecture. You are modifying, cleaning, or adding tests to code that is already where it belongs. The NLOC and CCN you measure with `lizard` are the actual NLOC and CCN of the work you will perform.

This assumption breaks down the moment the work involves moving code **across paradigms**. If the task is to migrate a Struts 1 service into Spring Boot 4, or to port an AngularJS module to React, or to extract a monolith module into a standalone microservice, you are no longer doing in-place refactoring. You are doing one of two fundamentally different things:

- **Modernization** — preserving the existing business rules and workflows while rewriting the code in a new paradigm.
- **Transformation** — rethinking the workflows, retiring obsolete rules, and introducing new behavior alongside the migration.

Both scenarios require a different mathematical model. The source code's NLOC becomes a poor proxy for the target code's NLOC (because modern frameworks often compress or expand boilerplate differently), and the Global Context Tax we defined here no longer captures the full cost of reverse-engineering legacy patterns or negotiating new business rules.

A planned companion article, *The Mathematics of Migration*, will cover these two scenarios in depth — including how to derive a Translation Factor by comparing the same operation across frameworks, how to price the reverse-engineering overhead using empirically measured code-comprehension rates, and how to account for the one-time Foundation Setup Cost of bootstrapping a new service. If your ticket says "rewrite in Spring Boot 4," that article is the one to read next.

## The Metrics That Matter: NLOC and CCN

To estimate effort, we must abandon raw Lines of Code (LOC). LOC measures volume, not complexity. A 500-line file with 500 simple getter methods takes minutes to refactor. A 500-line file with nested state machines takes days.

Instead, we rely on two metrics, extractable via tools like `lizard` or SonarQube:

1.  **Net Lines of Code (NLOC):** The physical size of the logic, excluding comments and blank lines. This represents the *baseline cognitive load* of reading and modifying the file.
2.  **Cyclomatic Complexity (CCN):** Introduced by Thomas J. McCabe in 1976, CCN measures the number of linearly independent paths through a program's source code. Every `if`, `for`, `while`, `case`, and `&&`/`||` operator increments the CCN.

The link between these two metrics and real maintenance effort isn't just intuitive — it has empirical backing. Gill and Kemerer's 1991 follow-up study on McCabe's metric analyzed 834 software modules and found that a "complexity density" ratio (CCN divided by size) was a meaningful predictor of maintenance productivity. That's the same shape of relationship this article's model leans on: NLOC sets the floor, CCN adjusts it.

**The Golden Rule of Estimation:**
*   **NLOC** dictates the baseline time to read, understand, and rewrite the code.
*   **CCN** acts as a multiplier for refactoring (because complex logic is fragile) and as a strong signal for testing effort — McCabe's own work establishes CCN as an *upper bound* on the number of test cases needed for full branch coverage, not an exact count. Some branches turn out to be unreachable or already covered by another path, so treat CCN as "test at most this many paths," not "test exactly this many."

### Getting the Numbers: lizard vs. SonarQube

**`lizard`** is a small, open-source Python CLI that computes NLOC and CCN across a dozen-plus languages (Java and TypeScript both included) without needing to build or compile anything — it just parses the source. Install it with `pip install lizard`, then point it at a file or directory:

```
$ lizard OrderProcessingService.java --csv
NLOC,CCN,token,PARAM,length,location,file,function,long_name,start,end
50,10,187,1,50,"processOrder(...) OrderProcessingService.java:24-55",OrderProcessingService.java,processOrder,processOrder(Order order),24,55
```

Each row is one function, not the whole file — the per-file NLOC quoted in the examples below is really the sum of a file's function rows. `lizard -C 10` fails the run (non-zero exit code) if any function exceeds a CCN threshold you set, which is a cheap way to gate pull requests before they reach a human reviewer. It also has a `-o report.html` option for a browsable, sortable report, and a code-clone detector (`-Eduplicate`) that's useful for spotting copy-pasted logic while you're already in there.

**SonarQube** measures the same underlying properties but as a server-based platform: a scanner runs inside your CI pipeline and reports to a dashboard that tracks Cyclomatic *and* Cognitive Complexity over time, with quality gates tied to your build. It's the right tool if you already have it wired into CI and want ongoing visibility across the whole codebase. `lizard` is the right tool for a quick, no-infrastructure check on a single file or PR, right before you write up an estimate — which is the workflow this article assumes.

## A Calibrated Mathematical Model — With a Caveat

To translate these metrics into hours, we use a heuristic model with a starting set of constants. It's important to be upfront about what these constants are and aren't: they are **not** derived from a published dataset. They're a reasonable starting point for a senior full-stack developer working in a familiar codebase, meant to be replaced with your own team's numbers once you have a few sprints of real data to calibrate against. Treat the values below as defaults, not gospel:

*   **Java (Spring Boot) Refactoring Baseline:** 333 NLOC per hour.
*   **React (TypeScript) Refactoring Baseline:** 200 NLOC per hour. (React requires more mental context switching for state and hooks).
*   **Testing Baseline:** 9 minutes (0.15 hrs) per CCN path to write a *meaningful* assertion, plus 3 minutes (0.05 hrs) per external dependency for fast mocking.

**Calibrating this to your team:** run `lizard` against a handful of pull requests you already tracked actual hours for, plot NLOC/CCN against real time spent, and solve for your own rate. Teams with heavy onboarding debt, unfamiliar domains, or junior-heavy rosters will see meaningfully lower NLOC/hour numbers than the defaults above — that's expected, not a flaw in the method.

### The Formulas

**1. Refactoring Effort (Per File):**
$$ \text{Time} = \left( \frac{\text{NLOC}}{\text{Base Rate}} \right) \times (1 + (\text{CCN} \times \text{Complexity Penalty})) $$
*(Note: The complexity penalty adds a time multiplier for the fragility of the code. E.g., 1% added time per CCN point for Java, 1.5% for React).*

**2. Testing Effort (Per File):**
$$ \text{Time} = (\text{CCN} \times 0.15) + (\text{External Dependencies} \times 0.05) $$

## The Hidden Cost: The Discovery Phase & Context Loading

There is a fatal flaw in the formulas above. If you present these numbers to management, they will say: *"Add 15% for discovery and architecture mapping."*

Applying a 15% buffer to *every single file* commits the **Compounding Fallacy of Context** (a name coined for this article, not an established industry term — but the underlying problem is real). That assumption means the developer re-learns the entire microservice architecture for every file they touch. Discovery is a **global, fixed-cost activity**. You map the database schema, understand the external API contracts, and figure out the CI/CD pipeline *once* per project.

To solve this, we introduce the **Global Context Tax**.

Instead of multiplying individual file estimates, we calculate discovery time as a single, global line item based on the **Total Volume (NLOC) of the entire scope**, ignoring the local Cyclomatic Complexity (CCN) penalties.

**The Global Context Tax Formula:**
$$ \text{Discovery Time} = \max\left(1.0 \text{ hour}, \left( \frac{\text{Total Scope NLOC}}{\text{Average Base Rate}} \right) \times 0.15 \right) $$

This ensures that even if you are only refactoring one tiny file, you allocate a minimum of 1 hour to understand its broader context. But if you are refactoring a massive 10,000 LOC directory, the 15% scales up naturally based on total volume, *without* compounding per file.

---

## Code Example 1: Java Spring Boot Service

Let's analyze a typical, slightly messy Spring Boot service.

```java
// OrderProcessingService.java
package com.example.orders;

import com.example.billing.BillingClient;
import com.example.inventory.InventoryClient;
import com.example.notifications.EmailService;
import org.springframework.stereotype.Service;

@Service
public class OrderProcessingService {

    private final BillingClient billingClient;
    private final InventoryClient inventoryClient;
    private final EmailService emailService;

    public OrderProcessingService(BillingClient billingClient, 
                                  InventoryClient inventoryClient, 
                                  EmailService emailService) {
        this.billingClient = billingClient;
        this.inventoryClient = inventoryClient;
        this.emailService = emailService;
    }

    public String processOrder(Order order) {
        if (order == null || order.getItems() == null) {
            return "INVALID_ORDER";
        }

        double total = 0;
        for (Item item : order.getItems()) {
            if (item.isActive()) {
                if (item.getDiscount() != null && item.getDiscount() > 0) {
                    total += item.getPrice() * (1 - item.getDiscount());
                } else {
                    total += item.getPrice();
                }
            }
        }

        if (total > 0) {
            if (billingClient.charge(order.getUserId(), total)) {
                if (inventoryClient.reserve(order.getItems())) {
                    emailService.sendConfirmation(order.getUserId());
                    return "SUCCESS";
                } else {
                    billingClient.refund(order.getUserId(), total);
                    return "INVENTORY_FAILED";
                }
            } else {
                return "BILLING_FAILED";
            }
        }
        return "ZERO_TOTAL";
    }
}
```

### Analyzing the Java Code

If we run `lizard OrderProcessingService.java --csv`, we get:
*   **NLOC:** ~49 lines
*   **CCN:** 10 (the null-and-empty-list check contributes 2 decision points via the `if` and the `||`; the `for` loop, the two nested `if`s inside it plus the `&&`, and the three nested `if`s in the billing/inventory block account for the rest).
*   **External Dependencies:** 3 (`BillingClient`, `InventoryClient`, `EmailService` injected via constructor).

### Calculating the Effort (Single File Scope)

**Refactoring Estimate:**

$$
\begin{aligned}
\mathrm{Base\ Time}           &= \frac{49\ \mathrm{NLOC}}{333\ \mathrm{LOC/hr}} \approx 0.15\ \mathrm{hrs} \\[4pt]
\mathrm{Complexity\ Mult.}    &= 1 + (10\ \mathrm{CCN} \times 0.01) = 1.10 \\[4pt]
\mathrm{Total\ Refactor\ Time} &= 0.15 \times 1.10 \approx 0.16\ \mathrm{hrs\ (10\ min)}
\end{aligned}
$$

**Testing Estimate:**

$$
\begin{aligned}
\mathrm{Meaningful\ Test\ Time} &= 10\ \text{CCN} \times 0.15\ \text{hrs} = \mathbf{1.50\ hrs} \\[4pt]
\mathrm{Fast\ Mocking\ Time} &= 3\ \text{Deps} \times 0.05\ \text{hrs} = \mathbf{0.15\ hrs} \\[4pt]
\mathrm{Total\ Testing\ Time} &= 1.50 + 0.15 = \mathbf{1.65\ hrs\ (1\ hr\ 39\ min)}
\end{aligned}
$$

**Global Context Tax:**
*   Since the scope is one file, the formula `(49/333) * 0.15` yields ~1 minute.
*   However, we apply the **Minimum Discovery Threshold** of 1.0 hour to map the surrounding architecture.

**Reporting Output:**
*"To refactor this service, write tests, and map the surrounding architecture, the estimated effort is **2 hours 49 minutes** (1 hr Discovery + 10 min Refactor + 1 hr 39 min Testing)."*

---

## Code Example 2: React + TypeScript Hook

The backend isn't the only place this model applies. Here's a TanStack Query hook of the kind you'd find in any React/TypeScript frontend, with the same shape of nested conditionals as the Java example above.

```typescript
// useOrderStatus.ts
import { useQuery } from '@tanstack/react-query';

interface OrderStatus {
  status: 'PENDING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
  eta?: string;
}

async function fetchOrderStatus(orderId: string): Promise<OrderStatus> {
  const response = await fetch(`/api/orders/${orderId}/status`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('ORDER_NOT_FOUND');
    }
    throw new Error('STATUS_FETCH_FAILED');
  }
  return response.json() as Promise<OrderStatus>;
}

export function useOrderStatus(orderId: string | undefined) {
  const query = useQuery({
    queryKey: ['orderStatus', orderId],
    queryFn: () => {
      if (!orderId) throw new Error('orderId is required');
      return fetchOrderStatus(orderId);
    },
    enabled: Boolean(orderId),
    retry: (failureCount, error) => {
      if (error instanceof Error && error.message === 'ORDER_NOT_FOUND') {
        return false;
      }
      return failureCount < 3;
    },
  });

  if (query.isPending) {
    return { label: 'Loading...', tone: 'neutral' as const };
  }

  if (query.isError) {
    return { label: 'Unable to load status', tone: 'error' as const };
  }

  const { status, eta } = query.data;

  if (status === 'CANCELLED') {
    return { label: 'Order cancelled', tone: 'error' as const };
  }

  if (status === 'DELIVERED') {
    return { label: 'Delivered', tone: 'success' as const };
  }

  if (eta) {
    return { label: `${status} — arriving ${eta}`, tone: 'neutral' as const };
  }

  return { label: status, tone: 'neutral' as const };
}
```

### Analyzing the TypeScript Code

*   **NLOC:** ~45 lines
*   **CCN:** 11 (the `response.ok`/`404` pair inside the fetch helper, the `isPending` and `isError` guards, the `instanceof`+`&&` check and the `< 3` comparison inside `retry`, and the three status-branching `if`s at the end — every relational operator in a boolean context counts as a decision point in McCabe's model).
*   **External Dependencies:** 1 primary boundary (the network call inside `fetchOrderStatus`, mocked at the `fetch` boundary). Testing also requires wrapping the hook in a `QueryClientProvider` or mocking `useQuery` directly, but that is framework test-infrastructure overhead rather than a per-dependency mock cost.

**Refactoring Estimate:**

$$
\begin{aligned}
\mathrm{Base\ Time}           &= \frac{45\ \mathrm{NLOC}}{200\ \mathrm{LOC/hr}} = 0.225\ \mathrm{hrs} \\[4pt]
\mathrm{Complexity\ Mult.}    &= 1 + (11\ \mathrm{CCN} \times 0.015) = 1.165 \\[4pt]
\mathrm{Total\ Refactor\ Time} &= 0.225 \times 1.165 \approx 0.26\ \mathrm{hrs\ (16\ min)}
\end{aligned}
$$

**Testing Estimate:**

$$
\begin{aligned}
\mathrm{Meaningful\ Test\ Time} &= 11\ \text{CCN} \times 0.15\ \text{hrs} = \mathbf{1.65\ hrs} \\[4pt]
\mathrm{Fast\ Mocking\ Time} &= 1\ \text{Dep} \times 0.05\ \text{hrs} = \mathbf{0.05\ hrs} \\[4pt]
\mathrm{Total\ Testing\ Time} &= 1.65 + 0.05 = \mathbf{1.70\ hrs\ (1\ hr\ 42\ min)}
\end{aligned}
$$

Notice the React example has fewer NLOC than the Java one but a comparable CCN — the "more mental context switching" penalty and the lower base rate are doing real work here, not just padding the estimate. Total for this file, applying the same 1.0-hour discovery floor as a standalone scope: **2 hours 58 minutes** (1 hr Discovery + 16 min Refactor + 1 hr 42 min Testing).

---

## Handling Scale: The "Top 3" Heuristic & Global Discovery

What happens when you are asked to estimate the refactoring of an entire microservice containing 40 files? Running this math on 40 files is tedious and often inaccurate, as developers rarely refactor every file equally.

We apply the **Pareto Principle (80/20 Rule)** to code complexity. Originally observed by Vilfredo Pareto in 1906 and adapted to quality management by Joseph Juran in 1941, the principle states that roughly 80% of effects come from 20% of causes. In software, this pattern appears across defect distribution, feature usage, and code complexity. In any large codebase, 80% of the technical debt and refactoring effort is concentrated in 20% of the files. This heuristic doesn't have the same empirical backing as the CCN-effort relationship above — treat it as a practical rule of thumb for triage, not a load-bearing part of the estimate.

**The Protocol for Large Directories:**
1. Run `lizard` on the entire directory to get the Total Scope NLOC.
2. Sort the output by CCN (Cyclomatic Complexity).
3. Isolate the **Top 3 most complex files** and calculate their specific Refactoring and Testing times.
4. For the remaining files, apply a flat "Low Complexity Tail" estimate (3 minutes per file).
5. **Calculate the Global Context Tax ONCE** using the Total Scope NLOC of all files.

**Worked example:** say `lizard` reports 40 files totaling 6,400 NLOC (average ~160 NLOC/file, blended Java/TypeScript base rate of ~300 NLOC/hr). The Global Context Tax is `max(1.0, (6400/300) * 0.15)` ≈ **3 hours 12 min**. The top 3 files by CCN average 220 NLOC and CCN 18 each — running each through the refactor and testing formulas above gives roughly 1–1¼ hours refactoring and about 3 hours testing per file, or about **11 hours 42 min** for all three combined. The remaining 37 files at the flat 3-minute tail add **1 hour 51 min**. Total: **about 16 hours 45 min** for the directory — a defensible number you can hand to a planning meeting, built from three worked examples and a flat tail instead of 40 individual guesses.

This gives management an accurate, defensible number that respects the reality of context loading, without getting bogged down in analyzing trivial DTOs.

## Where the Model Breaks Down

No estimation model survives contact with every codebase, and this one has real edges worth naming before you lean on it in a planning meeting:

*   **CCN isn't a perfect proxy for test count.** As the McCabe metric's own literature points out, cyclomatic complexity is an *upper bound* on the tests needed for branch coverage, not the exact count — some paths are unreachable, and some tests exercise more than one branch at once. Treat the testing formula as a ceiling estimate, not a precise requirement.
*   **The base rates assume a specific developer profile.** A senior developer fluent in the codebase and a junior developer new to it will produce very different NLOC/hour numbers on the same file. If your team's composition doesn't match "senior full-stack developer familiar with this service," recalibrate before trusting the output.
*   **Switch statements and lookup tables inflate CCN without inflating real difficulty.** A 10-case `switch` on an enum is mechanically simple to test even though it drives CCN up sharply — the model will overestimate testing time here unless you spot-check outliers before reporting them.
*   **The Pareto heuristic in the scaling section is a triage tool, not a proof.** Some codebases really do concentrate debt in a handful of files; others spread it evenly. Sort by CCN first and sanity-check the top files by eye before assuming the 80/20 split holds.

None of this invalidates the approach — it just means the output is a *calibrated estimate*, not a guarantee. That's still a large step up from "maybe a week?"

## Conclusion

Static analysis tools extract NLOC and CCN, and calibrated mathematical models translate those metrics into hours — but the model is only as honest as the constants feeding it. Respecting the non-compounding nature of architectural discovery, treating CCN as an upper bound rather than an exact count, and recalibrating the base rates against your own team's real data are what separate this from another flavor of gut-feeling estimation wearing a formula's clothes.

Measure the topology. Then check your work against reality, and adjust.