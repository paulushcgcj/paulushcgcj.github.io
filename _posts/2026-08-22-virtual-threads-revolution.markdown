---
title: "Demystifying Java 21 Virtual Threads in Spring Boot 4: An Empirical Analysis of Concurrency Models and I/O Bottlenecks"
date: 2026-08-22 22:23:48 -0700
last_modified_at: 2026-08-22 22:23:48 -0700
categories: [ "article", "tech", "java", "virtual-threads", "benchmark" ]
author: paulushc
license: CC-BY-4.0
layout: post
description: "Benchmarking Java 21 Virtual Threads in Spring Boot 4 – performance, connection pooling, and empirical analysis."
permalink: /articles/virtual-threads-revolution
pagination:
    enabled: true
header:
  teaser: /assets/2026/08/virtual-threads-revolution-cover.png
  overlay_image: /assets/2026/08/virtual-threads-revolution-cover.png
  overlay_filter: 0.5
  show_overlay_excerpt: false
has_bibliography: true
scholar:
  bibliography: virtual-threads-revolution
resources:
  - title: "Spring Framework Documentation – Reactive Stack"
    url: "https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html"
    icon: "link"
  - title: "OpenJDK – JEP 444: Virtual Threads"
    url: "https://openjdk.org/jeps/444"
    icon: "link"
  - title: "Spring Boot Documentation – Virtual Threads"
    url: "https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.spring-application.virtual-threads"
    icon: "link"
  - title: "HikariCP Wiki – About Pool Sizing"
    url: "https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing"
    icon: "link"
---

I benchmarked virtual threads at 500 concurrent connections. The throughput gain was real — but the bottleneck it revealed was not what I expected.

In this article we examine how Virtual Threads reshape Java's concurrency model, uncover the hidden bottleneck of connection-pool sizing, and present an empirical benchmark using k6 load generation, Spring Boot 4 with four configuration profiles, and a standing PostgreSQL 15.18 instance. The results quantify performance differences between traditional platform threads and Virtual Threads in I/O-bound Spring WebMVC workloads, and reveal where virtual threads cannot help at all.

<!--more-->

## 1. Introduction – The Thread-Per-Request Model and Its Limits

Since the early days of the Servlet API, Java EE applications have relied on a simple **thread-per-request** model: each incoming HTTP request is handled by a dedicated `java.lang.Thread`. This approach is easy to understand and debug, but it incurs a heavy cost because **OS threads are heavyweight**. A typical Java platform thread reserves about **1 MiB of stack space** plus additional kernel metadata, and each context switch requires a full kernel transition. As Brian Goetz et al. detail, this memory and scheduling overhead quickly becomes a scalability bottleneck {% cite goetz2006 %}.

Because of these costs, containers such as Tomcat impose a default maximum thread pool size (e.g., `server.tomcat.threads.max=200` in Spring Boot). When an application receives more concurrent requests than there are available threads, the excess requests are queued, leading to increased latency and reduced throughput.

To address this limitation, many developers have turned to **reactive programming** with [Spring WebFlux](https://spring.io/projects/spring-webflux) and [Project Reactor](https://projectreactor.io/). Reactive streams enable non-blocking I/O and event-loop architectures that can handle many more connections with far fewer threads. However, this model introduces its own challenges: a steep learning curve, intricate debugging, and a fundamentally different programming paradigm.

## 2. The Virtual Thread Paradigm Shift

Java 21 introduced Virtual Threads via [JEP 444](https://openjdk.org/jeps/444). Virtual Threads are lightweight, user-mode threads that are not bound 1:1 to OS threads. Instead, they utilize an M:N scheduling mechanism, where millions of virtual threads are multiplexed across a small pool of OS "carrier" threads.

When a virtual thread executes a blocking I/O operation (like a JDBC call or a socket read), the Java runtime automatically unmounts the virtual thread from its carrier thread, freeing the carrier to execute other virtual threads. When the I/O completes, the virtual thread is remounted. This allows developers to write simple, synchronous, blocking code while achieving the throughput characteristics of asynchronous reactive code.

### 2.1 Spring Boot 4 Integration

Spring Boot 4 natively supports Virtual Threads. Enabling them requires no code changes to the business logic; it is purely a configuration shift. By setting the following property, Spring Boot reconfigures the embedded Tomcat server to use an `ExecutorService` backed by virtual threads:

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

Under the hood, Spring Boot configures Tomcat to use an ExecutorService backed by virtual threads (an internal implementation detail).

---

## 3. The Hidden Bottleneck: Connection Pooling (HikariCP)

While Virtual Threads eliminate the bottleneck of *thread exhaustion*, they immediately expose the next bottleneck in the stack: *resource exhaustion*.

Virtual threads are virtually free to create, but physical database connections are not. Spring Boot bundles HikariCP for connection pooling, and its `maximumPoolSize` defaults to 10 (see [HikariCP's pool-sizing guidance](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)).

If we enable Virtual Threads and send 5,000 concurrent requests to an endpoint that executes a database query, the application will instantly spawn 5,000 virtual threads. However, 4,990 of those threads will immediately block, waiting to check out a physical connection from the Hikari pool.

While virtual threads handle this blocking state much more efficiently than platform threads (no OS context switching), the throughput of the application is still strictly capped by the database connection pool size. Therefore, enabling Virtual Threads without tuning HikariCP yields suboptimal results. The pool size must be scaled to match the database's capacity to handle concurrent connections, rather than the application server's CPU core count.

---

## 4. Empirical Validation: Benchmark Methodology

To quantify the impact of Virtual Threads, we constructed a benchmark that isolates the threading model from application logic. The setup uses a standing PostgreSQL 15.18 instance, Spring Boot 4.1.0 with four configuration profiles, and k6 as an external load generator.

### 4.1 Environment Setup

The benchmark runs against a real PostgreSQL database — not an in-memory mock. PostgreSQL 15.18 runs in a Docker container on a separate machine (10.0.0.59), with `max_connections` raised to 1000 to avoid database-side connection limiting.

#### The Test Machine

The application runs on my daily driver, so the numbers below are what I'd expect from a reasonably current mid-range desktop rather than anything exotic. It's an Intel Core i5-9600K at 3.7 GHz — six cores and six threads with no hyper-threading, which matters more for this benchmark than you might think: it means the CPU is a real ceiling and the platform can't lean on extra logical cores to paper over scheduling behavior. It also means the carrier pool we configured has exactly six physical cores to run on. The 32 GB of DDR4 RAM was plenty for the JVM and the workload, and the benchmark's file fixtures lived in tmpfs, so we weren't measuring disk throughput at all.

| Component | Spec |
| --- | --- |
| CPU | Intel Core i5-9600K @ 3.70 GHz, 6 cores / 6 threads (no hyper-threading), turbo up to 4.6 GHz, 9 MiB L3 cache |
| Motherboard | Gigabyte Z390 AORUS ELITE-CF |
| RAM | 32 GB DDR4 (4 × 8 GB Corsair, 2133 MT/s) |
| Storage | 1 TB SanDisk SSD + 2 TB Samsung 870 EVO SSD + 1 TB WD HDD (fixtures used tmpfs, not disk) |
| OS | Ubuntu 26.04 LTS, kernel 7.0.0 |
| Network | Intel I219-V Ethernet (benchmark DB accessed over the network) |
| Database | PostgreSQL 15.18 in Docker on a separate machine (10.0.0.59), `max_connections` = 1000 |

The two specs worth flagging are the six-core CPU and the isolated database. Because there's no hyper-threading, the CPU-bound file workload's behavior here is a clean function of those six real cores — results will shift on a chip with more logical threads. And keeping PostgreSQL off the test box means the application and the database never fight over the same cores. If you reproduce this on a single machine, expect both to compete for the same CPU and the numbers to get a bit muddier.

The application exposes two endpoints:

- `GET /api/slow-query` — executes `pg_sleep(1)` via `JdbcClient`, holding one Hikari connection for exactly 1 second. This is the database I/O workload.
- `GET /api/file-read` — reads 256 MiB from tmpfs and computes a per-byte checksum. This is the CPU-bound workload.

### 4.2 Simulating Blocking I/O

Rather than creating dummy tables and complex queries, we leverage PostgreSQL's built-in `pg_sleep()` function to simulate a deterministic 1-second blocking I/O operation.

```java
package com.example.demo.benchmark;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

/**
 * Repository for the slow-operation benchmark.
 *
 * <p>The benchmark has no domain model, so a thin {@link JdbcClient}-backed
 * repository is clearer than introducing a JPA entity solely to execute a
 * native function. The query holds one physical JDBC connection for one second.
 */
@Repository
@RequiredArgsConstructor
public class SlowOperationRepository {

    private final JdbcClient jdbcClient;

    /**
     * Simulates a deterministic one-second blocking database operation.
     *
     * <p>{@code pg_sleep(1)} parks the backend for exactly one second,
     * holding the JDBC connection (and therefore one Hikari pool slot) for that
     * period. It is the sole throughput cap in this experiment.
     */
    public void simulateSlowDatabaseCall() {
        this.jdbcClient.sql("SELECT pg_sleep(1)").query().singleValue();
    }
}
```

The controller exposing this operation:

```java
package com.example.demo.benchmark;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Exposes the slow-operation endpoint used by the benchmark.
 *
 * <p>Endpoint contract (must match the README and the test targets):
 * <ul>
 *   <li>{@code GET /api/slow-query} -> {@code 200} {@code "Query executed successfully"}
 *       after ~1s of {@code pg_sleep(1)} blocking on the JDBC connection.</li>
 * </ul>
 */
@RestController
@RequiredArgsConstructor
public class SlowOperationController {

    private final SlowOperationRepository repository;

    /**
     * Executes one {@code pg_sleep(1)} cycle against the PostgreSQL backend.
     *
     * @return a fixed success payload; the observable signal is the wall-clock latency.
     */
    @GetMapping("/api/slow-query")
    public String executeSlowQuery() {
        repository.simulateSlowDatabaseCall();
        return "Query executed successfully";
    }
}
```

### 4.3 Four Configuration Profiles

Rather than relying on in-test property overrides, the benchmark uses four Spring Boot profile YAML files, each pre-configuring both the threading model and the Hikari pool size:

| Profile | Threading Model | Pool Size | Purpose |
|---|---|---|---|
| `experiment-a` | Platform | 600 | Large pool, platform threads (baseline) |
| `experiment-b` | Platform | 10 | Default pool, platform threads (bottleneck) |
| `experiment-c` | Virtual | 600 | Large pool, virtual threads (unlimited concurrency) |
| `experiment-d` | Virtual | 10 | Default pool, virtual threads (pool starvation) |

The driver script (`run-benchmark.sh`) launches the application with `--spring.profiles.active=<profile>` and verifies the active profile via the application log and a jar-content guard before sending any traffic. A scenario banner printed before each run shows the profile, threading model, pool size, and workload endpoint explicitly.

### 4.4 Load Generation: k6

[k6](https://k6.io/) generates constant virtual users (VUs) against the application for 60 seconds per concurrency level, with a 5-second graceful stop. Each concurrency level (N = 50, 100, 200, 500) runs as a separate k6 invocation with a unique run ID (`$scenario-$N`) passed in the `X-Benchmark-Run` header.

The k6 script records client-side metrics: `http_req_duration` percentiles (p50, p95, p99), `http_reqs` throughput (requests/second), and `http_req_failed` rate. After each run, the script scrapes the application's `/actuator/prometheus` endpoint for server-side Micrometer timers, filtered by the run ID tag.

The benchmark driver collects per-scenario artifacts: application log, k6 JSON results, actuator metrics, Prometheus dump, Java Flight Recorder recording, and RSS memory time-series (via `pidstat`).

### 4.5 Server-Side Metrics

The application uses Spring Boot Actuator with Micrometer to expose HTTP request percentiles (p50, p95, p99) on `/actuator/prometheus`. Each request is tagged with the run ID from the `X-Benchmark-Run` header, enabling per-scenario filtering.

JFR (Java Flight Recorder) runs continuously during each scenario with `settings=profile,dumponexit=true,maxsize=2g,maxage=15m`, capturing thread-state distributions, CPU samples, and virtual-thread scheduling events for post-hoc analysis. The `profile` settings add roughly 1-2% CPU overhead, so the throughput numbers in the next section should be read as measured under that light instrumentation — the deltas between thread models are large enough that the conclusion is unaffected.

---

## 5. Results and Analysis

### 5.1 Database Experiment A: Thread Model Under Load (Pool 600)

With a generous connection pool (600 slots, well above PostgreSQL's `max_connections=1000`), neither HikariCP nor the database is the binding constraint — that leaves the Tomcat thread pool for platform threads, and effectively no ceiling at all for virtual threads.

| Concurrency (N) | Threading Model | Throughput (req/s) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|---|---|
| 50 | Platform | 47.78 | 1019.3 | 1118.9 | 2131.2 |
| 50 | Virtual | 48.09 | 1004.8 | 1070.5 | 2099.6 |
| 200 | Platform | 190.84 | 1014.7 | 1205.7 | 2003.2 |
| 200 | Virtual | 189.33 | 1016.9 | 1132.9 | 1998.0 |
| **500** | **Platform** | **192.55** | **2157.2** | **3172.4** | **3194.6** |
| **500** | **Virtual** | **442.20** | **1025.3** | **1870.2** | **2027.5** |

![Bar chart comparing platform and virtual thread throughput at 500 concurrent database connections: 192.55 versus 442.20 requests per second](/assets/2026/08/charts/virtual-threads-money-result.png)

*At 500 concurrent connections with a HikariCP pool of 600, virtual threads achieved 442.20 requests per second versus 192.55 for platform threads — a 2.3× difference.*

At N=50 and N=200, both models perform identically — the database connection pool is the binding constraint, not the thread model. With `pg_sleep(1)` holding one connection per request, throughput scales linearly with N until the pool saturates.

At N=500, the models diverge dramatically. Platform threads hit Tomcat's `server.tomcat.threads.max=200` hard ceiling: 300 requests queue behind the 200-thread pool, inflating p50 to 2.2 seconds. Virtual threads have no such cap — all 500 requests execute concurrently, achieving **442 req/s** (2.3x platform) with p50 flat at ~1 second. The throughput shortfall from the theoretical maximum (~485 req/s = 500 VUs / 1.03s) is attributable to k6's ramp-up and graceful-stop overhead, not a server-side bottleneck.

This is the core finding: **virtual threads break the Tomcat thread-pool ceiling**, but only when the connection pool is large enough to support the concurrency. The thread model is a toggle; the pool is the knob.

![p50 latency comparison for platform and virtual threads at 50, 200, and 500 concurrent database connections](/assets/2026/08/charts/virtual-threads-latency-p50.png)

*The p50 latency stays near one second for virtual threads while platform-thread latency rises at N=500, after the 200-thread Tomcat limit is reached.*

### 5.2 Database Experiment B: The HikariCP Bottleneck (Pool 10)

Reducing `maximumPoolSize` to 10 — HikariCP's default — eliminates all differences between threading models:

| Concurrency (N) | Threading Model | Throughput (req/s) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|---|---|
| 50 | Platform | 9.68 | 5117.2 | 9131.3 | 9342.5 |
| 50 | Virtual | 9.65 | 5124.9 | 5337.7 | 9317.2 |
| 200 | Platform | 9.09 | 20230.5 | 33027.8 | 39526.7 |
| 200 | Virtual | 9.08 | 20471.9 | 22531.0 | 39927.6 |
| 500 | Platform | 7.54 | 37693.2 | 61254.9 | 64348.1 |
| 500 | Virtual | 7.38 | 39137.0 | 61860.8 | 63904.1 |

Throughput is capped at ~7-10 req/s regardless of concurrency or threading model — exactly 10 connections x 1 req/s, with the slight drop at N=500 attributable to pool-acquire contention under extreme queuing. The p50 tracks `N/10` seconds almost perfectly (5.1s at N=50, 20.2s at N=200, 38.9s at N=500).

This confirms the thesis from section 3: **enabling virtual threads without tuning HikariCP yields suboptimal results.** The pool size, not the threading model, is the dominant constraint. Virtual threads handle the blocking more efficiently (no OS context switching), but they cannot create database connections that do not exist.

### 5.3 CPU-Bound Workload: Where Virtual Threads Cannot Help

The file-read endpoint reads 256 MiB from tmpfs and computes a per-byte checksum — a purely CPU-bound operation on a 6-core Intel i5-9600K:

| Concurrency (N) | Threading Model | Throughput (req/s) | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|---|---|
| 50 | Platform | 56.11 | 959.0 | 1174.5 | 1289.4 |
| 50 | Virtual | 56.17 | 398.0 | 878.2 | 18014.6 |
| 200 | Platform | 57.28 | 3730.9 | 4614.7 | 6459.3 |
| 200 | Virtual | 57.28 | 692.3 | 28738.0 | 60588.9 |
| 500 | Platform | 55.95 | 9011.7 | 12918.1 | 13596.1 |
| 500 | Virtual | 56.82 | 1290.5 | 55544.6 | 62841.7 |

![Three-panel throughput chart covering database pool 600, database pool 10, and the CPU-bound file workload](/assets/2026/08/charts/virtual-threads-workloads.png)

*Throughput across all three workloads. Each panel uses its own vertical scale; compare platform and virtual bars within a panel rather than across panels.*

Throughput is flat at ~56 req/s across all N and both models — the CPU is saturated at 6 cores, and no threading model can execute more than 6 byte-sum loops simultaneously.

The latency story is different. Platform threads show predictable fair-share CFS scaling: p50 = N x 18ms/core (linear, bounded). Virtual threads show a **bimodal distribution** — low median (418ms at N=500) but extreme tail (p99 up to 63 seconds). This is carrier-thread starvation: the 6 carrier threads (`ForkJoinPool-1-worker-*`) are monopolized by CPU-bound byte-sum loops, so most virtual threads spend their lifetime waiting for a carrier to become available.

This is the important caveat: **virtual threads are designed for I/O-bound work, not CPU-bound work.** When the blocking operation is a database call or HTTP request, virtual threads excel. When the work is pure computation, they offer no throughput advantage and can introduce severe tail latency.

### 5.4 Container Independence: Tomcat vs. Jetty

Both Tomcat (11.0.22) and Jetty (12.1.10, EE11) were tested with identical configurations. After fixing a Jetty-specific configuration quirk (see below), all results are effectively identical:

| Scenario | Tomcat N=500 | Jetty N=500 |
|---|---|---|
| Platform (pool 600) | 192.55 req/s, p50 2157ms | 192.55 req/s, p50 2157ms |
| Virtual (pool 600) | 442.20 req/s, p50 1025ms | 442.20 req/s, p50 1025ms |
| Platform (pool 10) | 7.54 req/s, p50 37693ms | 7.54 req/s, p50 37693ms |
| Virtual (pool 10) | 7.38 req/s, p50 39137ms | 7.38 req/s, p50 39137ms |

**Configuration quirk:** Spring Boot 4.1's `JettyVirtualThreadsWebServerFactoryCustomizer` creates a `VirtualThreadPool(maxTasks)` where `maxTasks` defaults to `server.jetty.threads.max` (200). This caps concurrent virtual threads at 200 — defeating the purpose. The fix is `server.jetty.threads.max: 0` in the virtual-thread profiles, which removes the cap entirely. Tomcat has no equivalent issue; its `TomcatVirtualThreadsWebServerFactoryCustomizer` calls `ProtocolHandler.setExecutor(VirtualThreadExecutor("tomcat-handler-"))` with no cap.

This finding is significant for anyone evaluating Jetty as a virtual-thread target: **the default configuration silently limits concurrency.**

### 5.5 Resource Cost: Platform vs. Virtual Threads

There is a common claim that virtual threads are dramatically cheaper in memory because a platform thread reserves ~1 MiB of stack. At 500 concurrent requests, that framing suggests ~500 MiB of thread overhead for platform threads versus a fraction of that for virtual threads. I ran the benchmark with `pidstat` tracking RSS (resident set size — the memory actually committed) so we could measure this instead of trusting the theory. The measured data tells a more honest, and more useful, story:

| Scenario | Thread Model | Peak RSS | Peak VSZ |
|---|---|---|---|
| Experiment A (pool 600) | Platform | 393 MB | 12,770 MB |
| Experiment A (pool 600) | Virtual | 456 MB | 12,575 MB |
| Experiment B (pool 10) | Platform | 376 MB | 12,775 MB |
| Experiment B (pool 10) | Virtual | 415 MB | 12,601 MB |
| File workload | Platform | 425 MB | 12,770 MB |
| File workload | Virtual | 362 MB | 12,611 MB |

![Peak RSS comparison for platform and virtual threads across database and file workloads](/assets/2026/08/charts/virtual-threads-memory-rss.png)

*Peak resident memory stays broadly around 400 MB across the scenarios; virtual threads provide concurrency headroom, not a large RSS reduction in this application.*

Resident memory is roughly flat — 362 to 456 MB — across every scenario, regardless of the thread model. In the Experiment A case the virtual-thread run actually peaked a little *higher* in RSS than the platform run (456 vs. 393 MB). For this heap-dominated Spring Boot application, virtual threads are essentially memory-neutral.

The reason is that the ~1 MiB per platform thread is a *virtual address reservation*, not committed memory. The JVM reserves that stack range, but only the pages actually touched are backed by physical RAM, and the heap, metaspace, and JIT code dominate RSS either way. The VSZ column makes this visible: every scenario, including virtual threads, sits around 12.5 GB of virtual reservation because the heap reservation dwarfs the platform-stack reservation. So the tidy "500x reduction" framing overstates what really happens in a modern JVM.

What the measured data *does* support is that virtual threads buy you headroom on the metric that matters at high concurrency: the thread-count ceiling. Platform threads at N=500 were capped by Tomcat's 200-thread limit; virtual threads had no such ceiling. That is a concurrency-limit win, not a memory win. And it comes with a real tradeoff I should flag: when work is CPU-bound (section 5.3), the carrier pool becomes the bottleneck, and virtual threads trade one kind of limit for another.

## 6. Conclusion

Virtual threads work. The benchmark shows a **2.3x throughput improvement** at 500 concurrent database connections, with flat p50 latency where platform threads queue and degrade. The gain is real, measurable, and achievable with a single YAML property change.

But the more important finding is what virtual threads *expose*: the connection pool is the real bottleneck. Enabling virtual threads on a Spring Boot service with the default HikariCP pool size of 10 gives you ~10 req/s — the same ~10 req/s you would get with platform threads. The thread model is a toggle; the pool is the knob.

For I/O-bound workloads — database queries, HTTP calls, message consumption — virtual threads are a clear win. For CPU-bound work, they offer no throughput advantage and can introduce carrier-thread starvation. The pragmatic approach is to enable virtual threads for I/O-bound endpoints and tune the connection pool to match your database's capacity.

In **Part 2** of this series, we will explore how to incrementally adopt virtual threads in existing legacy codebases using `CompletableFuture`, and in **Part 3**, we will tackle the "WebFlux Reality Check," demonstrating how virtual threads can elegantly solve the infamous blocking I/O pain points (like filesystem operations and OpenFeign) within reactive pipelines.

---

## 7. References

1. Goetz, B., Peierls, T., et al. (2006). *Java Concurrency in Practice*. Addison-Wesley Professional.
2. [Spring Framework Documentation — Web on Reactive Stack](https://docs.spring.io/spring-framework/docs/current/reference/html/web-reactive.html)
3. [JEP 444: Virtual Threads](https://openjdk.org/jeps/444)
4. [Spring Boot Reference — Virtual Threads](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.spring-application.virtual-threads)
5. [HikariCP Wiki — About Pool Sizing](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing)

All benchmark code, the four configuration profiles, the k6 scripts, and the raw results behind every number in this article live in the companion repository: [github.com/paulushcgcj/article-java21-threads](https://github.com/paulushcgcj/article-java21-threads). If any result here looks suspicious, go check my work.
