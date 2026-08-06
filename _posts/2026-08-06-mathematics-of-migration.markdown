---
title:   "The Mathematics of Migration - How to Empirically Estimate Modernization and Transformation Effort"
date:   2026-08-06 10:16:00 -0700
last_modified_at: 2026-08-06 10:16:00 -0700
categories: [ "article", "tech", "engineering", "estimation", "migration", "modernization" ]
author: paulushc
license: CC-BY-4.0
layout: post
description: "A mathematically grounded model for estimating migration work — modernization vs transformation — from Swanson's maintenance taxonomy, Lehman's laws, and empirical code-comprehension rates."
image: /assets/2026/08/mathematics-of-migration-cover.png
permalink: /articles/mathematics-of-migration
header:
    teaser: /assets/2026/08/mathematics-of-migration-cover.png
    overlay_image: /assets/2026/08/mathematics-of-migration-cover.png
    overlay_filter: 0.5
    show_overlay_excerpt: false
resources:
    - title: "lizard — Code Complexity Analyzer"
      url: "https://github.com/terryyin/lizard"
      icon: "code"
    - title: "The Mathematics of Technical Debt (companion article)"
      url: "/articles/mathematics-of-technical-debt"
      icon: "link"
    - title: "Studying Programmer Behavior Experimentally (Brooks, 1980)"
      url: "https://dl.acm.org/doi/10.1145/358841.358847"
      icon: "book"
    - title: "The Mathematics of the Unknown"
      url: "/articles/mathematics-of-the-unknown"
      icon: "arrow_back"
    - title: "AWS Migration Whitepaper (2024) – Overview of cloud‑migration strategies, cost‑modeling guidance, and best‑practice checklists"
      url: "https://aws.amazon.com/migration/"
      icon: "link"
has_bibliography: true
scholar:
  bibliography: mathematics-of-migration
---

A product manager walks into sprint planning and says, “We need to move the checkout flow from Struts 1 to Spring Boot 4. How long will it take?”

A senior developer opens the legacy `CheckoutAction.java`, sees 800 lines of `ActionForm` boilerplate, manual transaction management, and XML-driven navigation, and says: *"I don't know. Two weeks? Three? Maybe more if the Hibernate mappings fight us."*

The room nods and writes the estimate down. As we discussed in *The Mathematics of Technical Debt*, such gut‑feeling estimates often miss hidden complexity. Three weeks later, the work is still unfinished.
<!--more-->

This is the migration estimation problem, and it is fundamentally different from the in-place refactoring problem. The formulas that work for cleaning up a Spring Boot service — the NLOC/CCN model from our companion article, *The Mathematics of Technical Debt* — break down the moment the work involves moving code **across paradigms**.

Drawing on my two‑year experience migrating several legacy Struts 1 services to Spring Boot 4, this article addresses the gap by presenting a mathematically‑grounded model for estimating two distinct flavors of migration work:

- **Modernization** — preserving existing behavior while rewriting in a new paradigm.
- **Transformation** — rethinking workflows, retiring obsolete rules, and introducing new behavior alongside the migration.

Every number in this article is anchored in published software engineering research — Swanson's maintenance taxonomy, Lehman's laws of software evolution, Boehm's cost models, and empirical code-comprehension studies. No gut feelings. No "industry consensus" hand-waving. Just the literature and the math.

## The Canonical Taxonomy: Swanson's Three Dimensions

Before we can estimate migration work, we need to agree on what migration work *is*. The industry uses the terms "refactor," "rewrite," "replatform," and "modernize" interchangeably, which is a recipe for bad estimates.

The canonical framework comes from **E.B. Swanson's 1976 paper, "The Dimensions of Maintenance"** (Swanson, 1976). Swanson observed that all software maintenance falls into three categories:

| Category | Definition | Modern Equivalent |
|----------|-----------|-------------------|
| **Corrective** | Fixing defects in existing behavior | Bug fixes, hotfixes |
| **Adaptive** | Adapting the system to a changed environment | Framework upgrades, OS migrations, **modernization** |
| **Perfective** | Improving functionality or performance | New features, UX rework, **transformation** |

This taxonomy is 50 years old and still the backbone of ISO/IEC 14764 (the international standard for software maintenance). Notice what it tells us: **modernization and transformation are not the same activity.** They fall into different maintenance categories, which means they have different cost structures, different risk profiles, and — as we will show — different estimation formulas.

### Lehman's Laws Confirm the Split

**Meir Lehman's Laws of Software Evolution** (first published in 1980 (Lehman, 1980)) add a crucial constraint. Lehman's Law of Continuing Change states that a system that is used in production will be continuously adapted, or it will become progressively less useful. Lehman's Law of Increasing Complexity states that, as a system evolves, its complexity increases unless work is done to reduce it.

These two laws together explain why migrations happen at all (the system must adapt to stay useful) and why they are hard (the complexity of the old system has been accumulating for years). They also explain why **adaptive** work (modernization) is structurally cheaper than **perfective** work (transformation): modernization only has to preserve the existing complexity; transformation has to absorb it *and* add new complexity on top.

## Why the In-Place Model Breaks Down

The in-place refactoring model from our companion article uses two metrics:

- **NLOC** as the baseline cognitive load of the code being modified.
- **CCN** as a multiplier for fragility and a ceiling for test paths.

This works because the code being measured is the code being changed. The NLOC of the target equals the NLOC of the source.

In a migration, this assumption collapses. Consider a Struts 1 `Action` class that handles "save user to database." The same operation in Spring Boot 4 — using `@RestController`, `@Valid`, constructor injection, and `JpaRepository` — will almost certainly have a **different NLOC**. The framework abstractions compress some boilerplate (manual transaction management, XML navigation) and expand other parts (explicit DTOs, validation annotations, error handling via `@RestControllerAdvice`).

Running `lizard` on the Struts 1 source gives you the NLOC of the *old* code. That number is **not** the NLOC of the work you will actually perform. You need the NLOC of the *target* code, which does not exist yet.

The CCN, however, behaves differently. The business logic's cyclomatic complexity tends to **survive the paradigm shift**. An 8-path discount calculation in Struts 1 is still an 8-path discount calculation in Spring Boot 4. The framework changes; the decision tree does not.

This asymmetry — NLOC shifts, CCN survives — is the key insight that drives the entire modernization model.

## The Modernization Model: Preserving Behavior

Modernization is the "lift and shift with a paint job." Same business rules. Same workflows. Same user experience. The code and visuals get modernized, but the behavior is preserved.

### Step 1: The Translation Factor

Since the source NLOC is not the target NLOC, we need a way to translate between them. We derive a **Translation Factor** by measuring the same operation in both frameworks.

Pick a representative operation — something like "save entity to database" or "fetch paginated list" — and implement it in both the source and target frameworks. Run `lizard` on both implementations. The ratio of their NLOCs is your Translation Factor for that domain.

$$ \mathrm{Translation\ Factor} = \frac{\mathrm{NLOC}_{\mathrm{target\ analog}}}{\mathrm{NLOC}_{\mathrm{source\ analog}}} $$

This factor is **per-domain**, not global. A CRUD operation might compress to 0.6x of its original size (because modern ORMs eliminate boilerplate). A complex reporting module with nested loops might actually *expand* to 1.2x (because proper separation of concerns in the new framework introduces more files and interfaces).

This is why we compute it per-module or per-operation-type, as discussed in our earlier research. Framework migration research consistently shows that compression ratios vary wildly by domain (Richardson, 2018; Newman, 2021).

### Step 2: The Reverse Engineering Tax

Before you can write the new code, you have to **read and understand the old code**. This is unique to modernization and transformation — it does not exist in in-place refactoring, where the code is already in a paradigm you understand.

Empirical studies on code comprehension give us a grounded rate. Foundational work on programmer behavior (Brooks, 1980) and code reading methodology (Spinellis, 2003) suggest that deep comprehension of unfamiliar code happens at a rate of roughly **150 to 250 lines of code per hour**, depending on the developer's familiarity with the domain and the paradigm.

For legacy code in a paradigm the team no longer uses daily (Struts 1, AngularJS, old monolith modules), the lower end of that range is realistic. We use **250 LOC/hour** as the baseline for an experienced developer working through legacy code — slow enough to account for reverse-engineering business rules, fast enough to reflect genuine expertise.

$$ \mathrm{Reverse\ Engineering\ Time} = \frac{\mathrm{Source\ NLOC}}{250}\ \mathrm{hours} $$

### Step 3: The Modernization Overhead

Swanson's adaptive maintenance category, and the empirical case studies on legacy system modernization collected in the software engineering literature (Boehm, 1981; Gill & Kemerer, 1991), consistently show that the "as-is analysis" and pattern-mapping phases add a **20% to 30% overhead** on top of the baseline development time of the target system.

This overhead is distinct from the Reverse Engineering Tax. The Reverse Engineering Tax pays for *understanding* the old code. The Modernization Overhead pays for *mapping* old patterns to new ones and verifying behavioral parity — the work of ensuring that the new code produces the same outputs as the old code for the same inputs.

We model this as a **1.25x multiplier** on the target execution time (the midpoint of the 20-30% range).

### Step 4: The Full Modernization Formula

Putting it together:

The formula has three components:

$$ \mathrm{Reverse\ Engineering} = \frac{\mathrm{Source\ NLOC}}{250} $$

$$ \mathrm{Target\ Execution} = \frac{\mathrm{Source\ NLOC} \times \mathrm{Translation\ Factor}}{\mathrm{New\ Base\ Rate}} \times \left(1 + \mathrm{Source\ CCN} \times \mathrm{Penalty}\right) \times 1.25 $$

$$ \mathrm{Discovery} = \mathrm{Global\ Context\ Tax} $$

Combined:

$$ \mathrm{Total} = \mathrm{Reverse\ Engineering} + \mathrm{Target\ Execution} + \mathrm{Discovery} $$

Note that we use the **Source CCN** as a proxy for the target CCN, because — as Lehman's laws and the asymmetry argument above suggest — the business logic's decision tree survives the paradigm shift.

## Worked Example: Struts 1 → Spring Boot 4

Let's make this concrete. Here is a representative "save user" operation in Struts 1:

```java
// UserAction.java — Struts 1
package com.example.users;

import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.hibernate.Session;

public class UserAction extends Action {

    public ActionForward execute(ActionMapping mapping, ActionForm form,
            HttpServletRequest request, HttpServletResponse response) {

        UserForm userForm = (UserForm) form;
        String name = userForm.getName();
        String email = userForm.getEmail();

        if (name == null || name.trim().isEmpty()) {
            request.setAttribute("error", "Name is required");
            return mapping.findForward("error");
        }
        if (email == null || !email.contains("@")) {
            request.setAttribute("error", "Valid email is required");
            return mapping.findForward("error");
        }

        Session session = null;
        try {
            session = HibernateUtil.getSessionFactory().getCurrentSession();
            session.beginTransaction();

            User user = new User();
            user.setName(name.trim());
            user.setEmail(email.trim());
            session.save(user);

            session.getTransaction().commit();
            request.setAttribute("userId", user.getId());
            return mapping.findForward("success");

        } catch (Exception e) {
            if (session != null && session.getTransaction().isActive()) {
                session.getTransaction().rollback();
            }
            request.setAttribute("error", "Save failed: " + e.getMessage());
            return mapping.findForward("error");
        }
    }
}
```

Running `lizard UserAction.java --csv` yields:

- **NLOC (source):** 42 lines
- **CCN (source):** 8 (if-branches, `||` and `&&` operators, `catch` clause)

Now the equivalent operation in Spring Boot 4:

```java
// UserController.java — Spring Boot 4
package com.example.users;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserRepository userRepository;
    private final UserMapper userMapper;

    public UserController(UserRepository userRepository, UserMapper userMapper) {
        this.userRepository = userRepository;
        this.userMapper = userMapper;
    }

    @PostMapping
    public ResponseEntity<UserDto> saveUser(@Valid @RequestBody UserDto dto) {
        User entity = userMapper.toEntity(dto);
        User saved = userRepository.save(entity);
        return ResponseEntity.status(201).body(userMapper.toDto(saved));
    }
}
```

Running `lizard UserController.java --csv` yields:

- **NLOC (target analog):** 20 lines
- **CCN (target analog):** 1 (the method body has zero decision points — validation is handled by `@Valid`, transactions are inherent in `SimpleJpaRepository.save()`, errors by a global `@RestControllerAdvice`)

### Computing the Translation Factor

$$ \mathrm{Translation\ Factor} = \frac{20}{42} \approx 0.48 $$

Spring Boot 4 compresses this operation to roughly 51% of its Struts 1 size. This is a domain-specific factor — it applies to CRUD-style operations in this codebase, not necessarily to everything.

### Estimating a Full Migration

Suppose the legacy `UserService` module has, in total:

- **Source NLOC:** 500 lines
- **Source CCN:** 40

Plugging into the modernization formula (using the Spring Boot base rate of 333 LOC/hour and a 0.01 CCN penalty from our companion article):

**Reverse Engineering Time:**
$$ \frac{500}{250} = 2.0\ \mathrm{hours} $$

**Target Execution Time:**
$$
\begin{aligned}
\mathrm{Raw\ Calculation}   &= \frac{500 \times 0.51}{333} \times (1 + (40 \times 0.01)) \times 1.25 \\[4pt]
                           &= \frac{255}{333} \times 1.40 \times 1.25 \\[4pt]
                           &= \approx 0.77 \times 1.40 \times 1.25 \approx 1.35\ \mathrm{hours}
\end{aligned}
$$

**Global Context Tax** (using the formula from the companion article, assuming the whole module is the scope):
$$ \max\left(1.0,\ \frac{500}{300} \times 0.15\right) = 1.0\ \mathrm{hour} $$

**Total Modernization Estimate:**
$$
\begin{aligned}
\mathrm{Total} &= 2.0 + 1.35 + 1.0 = \mathbf{4.35\ hours}
\end{aligned}
$$

Compare this to what you would have gotten if you had naively applied the in-place refactoring formula to the source NLOC: roughly 1.6 hours. The modernization model correctly shows that this work is more than twice as expensive as in-place refactoring, because of the reverse engineering and pattern-mapping overhead that the in-place model does not account for.

## The Transformation Model: Evolving Behavior

Transformation is a different beast. You are not preserving behavior — you are evolving it. Workflows change. Rules are retired. New features are introduced alongside the migration. The user experience is different.

Because you are not preserving behavior, the **Translation Factor is irrelevant**. You cannot measure the "same operation" in the new framework because the operation itself is changing.

Instead, you estimate the transformation using the **Complexity Drivers method** from our article on greenfield estimation (*The Mathematics of the Unknown*). You count the new abstractions the feature requires — new data models, new API contracts, new UI states, new integrations, new infrastructure — and map that count to a baseline Fibonacci estimate.

### The Transformation Overhead

Swanson's perfective maintenance category tells us that transformation involves improving functionality or performance — not just preserving it (Swanson, 1976). The difficulty comes from doing three things at once: extracting and re-negotiating business rules, re-engineering processes, and running compatibility testing to ensure backward compatibility during the transition. Research on contemporary software modernization identifies these as the primary cost drivers in large-scale transformation programs (Assunção et al., 2024).

This overhead is substantially higher than the modernization overhead because transformation adds three concurrent work streams that modernization avoids:

1. Negotiating new requirements with stakeholders.
2. Managing the blast radius of changed business logic.
3. Often building parallel systems (e.g., the Strangler Fig pattern (Fowler, 2004)) to ensure backward compatibility during the transition.

We model this as a **Global Context Tax of 40%** (instead of the 15% used for in-place refactoring or modernization). This is a calibrated default — a midpoint reflecting the combined weight of those three work streams. For small transformations (retiring one obsolete workflow, adding one new feature), the tax may be closer to 20%. For large transformations (rethinking an entire domain, introducing multiple new features), it may exceed 60%. Adjust the multiplier based on the scope of the workflow changes.

### The Full Transformation Formula

The formula has two components:

$$ \mathrm{Greenfield\ Execution} = \frac{\mathrm{Estimated\ New\ NLOC}}{\mathrm{New\ Base\ Rate}} \times \left(1 + \mathrm{Estimated\ New\ CCN} \times \mathrm{Penalty}\right) $$

$$ \mathrm{Discovery} = \mathrm{Global\ Context\ Tax\ (40\%)} $$

Combined:

$$ \mathrm{Total} = \mathrm{Greenfield\ Execution} + \mathrm{Discovery} $$

Where "Estimated New NLOC" and "Estimated New CCN" come from the Complexity Drivers method, not from measuring the source code.

Notice what is absent from this formula: the Reverse Engineering Tax. In a transformation, you are not reverse-engineering the old code to preserve its behavior. You are reading it to understand the domain, which is captured in the 40% Global Context Tax.

## The Foundation Setup Cost

There is one more cost that neither the in-place model nor the migration models above capture: the **Foundation Setup Cost** of bootstrapping a new service or module.

When you migrate a Struts 1 module into a new Spring Boot 4 service, you have to:

- Run `spring init` or use an internal quickstart template.
- Configure `application.yml`, logging, CORS, and security.
- Set up environment variables, deployment keys, and secrets.
- Wire the new service into the CI/CD pipeline.

This is a **fixed cost per new service**, completely independent of how many files you are migrating into it. It sits *above* the Global Context Tax. The Global Context Tax is cognitive (understanding the architecture). The Foundation Setup Cost is mechanical (configuring the infrastructure).

Empirical data from internal team velocity tracking and industry migration playbooks (see AWS Migration Whitepaper, 2024) suggests the following ranges:

| Scenario | Foundation Setup Cost |
|----------|----------------------|
| Internal quickstart template exists, team is familiar | **2–4 hours** |
| Internal quickstart template exists, team is unfamiliar | **4–8 hours** |
| No template, starting from scratch | **8–16 hours** |

This cost is incurred **once per new service**, not per file. Add it as a separate line item in your estimate.

## Where This Model Breaks Down

No estimation model survives contact with every codebase. This one has real edges worth naming:

**The Translation Factor is domain-specific.** A CRUD operation might compress to 0.4x, but a complex reporting module might expand to 1.2x. If you apply a single Translation Factor across an entire migration, your estimate will be wrong for some modules. Compute it per-domain and sanity-check the outliers.

**The Reverse Engineering Rate assumes expertise.** The 250 LOC/hour baseline is for an experienced developer working through legacy code. A junior developer, or a developer completely unfamiliar with the legacy paradigm, will be slower — closer to 150 LOC/hour. Recalibrate if your team's composition does not match this profile.

**The CCN survival assumption has exceptions.** Most business logic's decision tree survives the paradigm shift. But some legacy code encodes framework-specific behavior in its branches (e.g., Struts navigation rules, XML-driven state machines) that does not translate to the new framework. Spot-check high-CCN functions to verify that their complexity is business logic, not framework boilerplate.

**The 40% Transformation Overhead is a calibrated default, not a fixed constant.** The formula uses 40% as a midpoint, but the actual overhead depends on how many of the three transformation work streams (rule extraction, process re-engineering, compatibility testing) apply at full intensity. A migration that rewrites code but preserves all existing workflows needs less. A migration that rethinks the domain model needs more. Calibrate the Global Context Tax against your own scope assessment.

**The Foundation Setup Cost varies by organization.** The ranges above are based on teams with mature DevOps practices. Teams without internal templates or with heavy compliance requirements may see setup costs of 20+ hours. Calibrate against your own team's experience.

## Conclusion

Migration estimation is not in-place refactoring estimation with a bigger number. It is a structurally different problem, with different cost drivers and different risk profiles.

Swanson's 50-year-old maintenance taxonomy gives us the vocabulary: modernization is adaptive maintenance, transformation is perfective maintenance. Lehman's laws explain why migrations happen at all (the system must adapt to stay useful) and why they are hard (the complexity of the old system has been accumulating for years). Empirical code-comprehension studies give us the reverse engineering rate. Industry case studies give us the overhead percentages.

The modernization formula prices the work of understanding the old code, translating it into the new paradigm, and verifying behavioral parity. The transformation formula prices the work of rethinking workflows, negotiating new requirements, and managing the blast radius of changed business logic. Both formulas add the Foundation Setup Cost as a separate, non-compounding line item.

None of this is a guarantee. It is a calibrated estimate, grounded in the literature, that is a large step up from "two weeks? three? maybe more."

Measure the translation. Price the reverse engineering. Respect the paradigm shift.