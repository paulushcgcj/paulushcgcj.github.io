---
title: "Demystifying Java 21 Virtual Threads in Spring Boot 4: Part 2 - Incremental Adoption and the Fan-Out Pattern"
date: 2026-08-02 08:30:00 -0700
last_modified_at: 2026-08-02 08:30:00 -0700
categories: [ "article", "tech", "java", "virtual-threads", "incremental" ]
author: paulushc
license: CC-BY-4.0
layout: post
description: "How to progressively adopt Java 21 Virtual Threads in existing Spring Boot applications using CompletableFuture."
permalink: /articles/virtual-threads-incremental-adoption
header:
  teaser: /assets/2026/08/virtual-threads-incremental-cover.png
  overlay_image: /assets/2026/08/virtual-threads-incremental-cover.png
  overlay_filter: 0.5
  show_overlay_excerpt: false
---

## 1\. Introduction: The Aggregation (Fan-Out) Problem

In modern microservice architectures, a single client-facing endpoint often needs to aggregate data from multiple downstream sources. For example, a `/api/user/dashboard` endpoint might need to fetch:

1. User profile data from the Identity Service.
2. Recent orders from the Order Service.
3. Notification preferences from the Preferences Service.

If each downstream call takes 500ms, executing them sequentially results in a catastrophic 1,500ms response time. The industry standard solution is the "Fan-Out" pattern: executing these calls concurrently and joining the results, reducing the total latency to the duration of the slowest single call (~500ms).

However, implementing concurrent blocking I/O in Java has historically been fraught with architectural compromises.

---

## 2\. The Legacy Approaches and Their Flaws

Before Java 21, developers typically relied on two approaches to implement the Fan-Out pattern, both of which carry significant drawbacks.

### 2.1 The Default CompletableFuture Trap

The most common approach is using `CompletableFuture.supplyAsync()` without specifying an executor:

```java
// ANTI-PATTERN: Using the default common pool for blocking I/O
CompletableFuture<UserProfile> profileFuture = CompletableFuture.supplyAsync(() -> {
    return identityClient.getProfile(); // Blocking HTTP call
});
```

**The Flaw:** When no executor is provided, `CompletableFuture` delegates the task to `ForkJoinPool.commonPool()`. This pool is sized dynamically based on the number of available CPU cores (typically `cores - 1`). It is explicitly designed for *CPU-bound*, short-lived recursive tasks (like parallel Streams).

If you use the common pool for *blocking I/O*, those few core threads will quickly become blocked waiting for network responses. This starves the pool, causing severe throughput degradation for entirely unrelated CPU-bound tasks running elsewhere in the JVM.

### 2.2 The Custom ThreadPoolExecutor Overhead

To avoid starving the common pool, developers traditionally create a dedicated `ThreadPoolExecutor`:

```java
// LEGACY PATTERN: Dedicated thread pool
ExecutorService ioExecutor = new ThreadPoolExecutor(
    50, 200, 60L, TimeUnit.SECONDS,
    new LinkedBlockingQueue<>());
```

**The Flaw:** While this isolates the I/O tasks, platform threads are expensive. A pool of 200 threads consumes roughly 200MB of heap memory just for thread stacks, plus the overhead of OS context switching when the pool is under heavy load.

---

## 3\. The Virtual Thread Solution

Java 21's Virtual Threads provide the perfect architectural fit for the Fan-Out pattern. By utilizing `Executors.newVirtualThreadPerTaskExecutor()`, we can spawn a virtually unbounded number of threads that consume negligible memory and incur zero OS context-switching overhead when they block on I/O.

### 3.1 Implementation in Spring Boot 4

In a Spring Boot 4 application, we can define this executor as a Spring Bean, making it easily injectable into our services.

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Configuration
public class ConcurrencyConfig {
    /**
     * Creates an ExecutorService where every submitted task runs on a new Virtual Thread.
     * This is ideal for blocking I/O operations like external HTTP calls or file reads.
     */
    @Bean
    public ExecutorService virtualThreadExecutor() {
        return Executors.newVirtualThreadPerTaskExecutor();
    }
}
```

### 3.2 The Fan-Out Controller

Using this executor, we can now safely parallelize our blocking downstream calls without fear of thread pool exhaustion or memory bloat.

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;

@RestController
public class DashboardController {
    private final DownstreamApiClient apiClient;
    private final ExecutorService virtualThreadExecutor;

    public DashboardController(DownstreamApiClient apiClient, ExecutorService virtualThreadExecutor) {
        this.apiClient = apiClient;
        this.virtualThreadExecutor = virtualThreadExecutor;
    }

    @GetMapping("/api/dashboard")
    public DashboardResponse getDashboard() throws Exception {
        // Fan-out: Dispatch all blocking calls concurrently to Virtual Threads
        CompletableFuture<UserProfile> profileFuture = CompletableFuture.supplyAsync(
            () -> apiClient.fetchUserProfile(), virtualThreadExecutor
        );
        CompletableFuture<List<Order>> ordersFuture = CompletableFuture.supplyAsync(
            () -> apiClient.fetchRecentOrders(), virtualThreadExecutor
        );
        CompletableFuture<Preferences> prefsFuture = CompletableFuture.supplyAsync(
            () -> apiClient.fetchPreferences(), virtualThreadExecutor
        );
        // Fan-in: Wait for all virtual threads to complete and aggregate results
        CompletableFuture.allOf(profileFuture, ordersFuture, prefsFuture).join();
        return new DashboardResponse(
            profileFuture.get(),
            ordersFuture.get(),
            prefsFuture.get()
        );
    }
}
```

---

## 4\. Empirical Validation: Benchmark Methodology

To quantify the latency reduction, we will benchmark three distinct implementations of the `/api/dashboard` endpoint:

1. **Sequential:** Executing the 3 calls one after the other.
2. **Common Pool:** Using `CompletableFuture` without a specified executor.
3. **Virtual Threads:** Using the `virtualThreadExecutor` defined above.

### 4.1 Simulating Downstream Latency

For reproducibility, the `DownstreamApiClient` will simulate a deterministic 500ms network delay using `Thread.sleep(500)` for each call.

```java
import org.springframework.stereotype.Service;

@Service
public class DownstreamApiClient {
    public UserProfile fetchUserProfile() { simulateLatency(); return new UserProfile("Paulo", "paulo@example.com"); }
    public List<Order> fetchRecentOrders() { simulateLatency(); return List.of(new Order("ORD-1"), new Order("ORD-2")); }
    public Preferences fetchPreferences() { simulateLatency(); return new Preferences("dark-mode", "en-US"); }
    private void simulateLatency() { try { Thread.sleep(500); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
}
```

### 4.2 The Parameterized JUnit 5 Benchmark

Reusing the Testcontainers and Micrometer infrastructure from Part 1, we parameterize the test to measure throughput and p99 latency across varying loads.

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.web.client.RestClient;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import java.util.concurrent.CompletableFuture;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class FanOutBenchmarkTest {
    @LocalServerPort
    private int port;
    @Autowired
    private MeterRegistry meterRegistry;
    private final RestClient restClient = RestClient.create();

    @ParameterizedTest
    @ValueSource(ints = {20, 50, 100, 200})
    void benchmarkFanOutEndpoint(int concurrentUsers) throws Exception {
        // Clear previous metrics to ensure clean state for this parameter
        meterRegistry.clear();
        long startTime = System.currentTimeMillis();
        CompletableFuture<?>[] futures = new CompletableFuture[concurrentUsers];
        for (int i = 0; i < concurrentUsers; i++) {
            futures[i] = CompletableFuture.runAsync(() -> {
                restClient.get()
                    .uri("http://localhost:" + port + "/api/dashboard")
                    .retrieve()
                    .toBodilessEntity();
            });
        }
        CompletableFuture.allOf(futures).join();
        long totalTime = System.currentTimeMillis() - startTime;
        // Extract Micrometer metrics
        Timer httpTimer = meterRegistry.find("http.server.requests")
                .tag("uri", "/api/dashboard")
                .tag("status", "200")
                .timer();
        if (httpTimer != null) {
            double p99 = httpTimer.takeSnapshot().percentileValues()[4].value() / 1_000_000.0; // ms
            double throughput = (concurrentUsers * 1000.0) / totalTime;
            System.out.printf("Concurrent %d: throughput=%.2f req/s, p99=%.2f ms%n", concurrentUsers, throughput, p99);
        }
    }
}
```

---

## 5\. Empirical Results and Analysis

*Note: The following table contains placeholders for your local benchmark execution data.*

| Concurrency (N) | Implementation | Total Time (ms) | Throughput (req/s) | p99 Latency (ms) |
|---|---|---|---|---|
| **50** | Sequential | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |
| **50** | Common Pool | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |
| **50** | Virtual Threads | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |
| **200** | Sequential | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |
| **200** | Common Pool | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |
| **200** | Virtual Threads | `[INSERT DATA]` | `[INSERT DATA]` | `[INSERT]` |

### 5.1 Analysis of Latency Reduction

Because each of the three downstream calls takes exactly 500ms, the theoretical minimum execution time for a single request is 500ms.

The **Sequential** implementation will consistently take ~1,500ms per request, resulting in the lowest throughput. The **Common Pool** and **Virtual Thread** implementations should both achieve the ~500ms baseline for individual request latency.

### 5.2 The Throughput Cliff of the Common Pool

The most critical insight from this benchmark lies in the throughput and p99 latency columns at N=200.

While the Common Pool successfully parallelizes the requests initially, it relies on a fixed number of threads (e.g., 7 threads on an 8-core machine). When 200 concurrent users hit the endpoint, the Common Pool quickly saturates. Requests begin queuing up in the `ForkJoinPool` work queue. Consequently, the p99 latency for the Common Pool will spike dramatically (often exceeding 3,000ms), and overall throughput will collapse.

The **Virtual Thread** implementation, however, spawns a new virtual thread for every single downstream call. At N=200, it spawns 600 virtual threads. Because they are lightweight and park efficiently during the 500ms `Thread.sleep`, the throughput remains linearly scalable, and the p99 latency remains pinned near the 500ms baseline.

---

## 6\. Pitfalls and Best Practices in Incremental Adoption

While `CompletableFuture` and Virtual Threads are a powerful combination, developers must be aware of two critical pitfalls when adopting them incrementally.

### 6.1 Thread Pinning

If a virtual thread executes a `synchronized` block or a native method while blocking on I/O, it becomes "pinned" to its OS carrier thread. This defeats the purpose of virtual threads, as the carrier thread is blocked and cannot execute other virtual threads.

**Best Practice:** Replace `synchronized` blocks with `java.util.concurrent.locks.ReentrantLock` in code paths that will be executed on virtual threads.

```java
// BAD: Causes thread pinning during I/Os
synchronized (lock) {    Thread.sleep(1000); }
// GOOD: Allows the virtual thread to unmount from the carrier thread
private final ReentrantLock lock = new ReentrantLock();
lock.lock();
try {    Thread.sleep(1000);} finally {    lock.unlock();}
```

### 6.2 ThreadLocal Leakage

Virtual threads are pooled and reused by the JVM's internal scheduler. If you store state in a `ThreadLocal` variable (common in legacy security contexts or database transaction managers), that state will leak into subsequent tasks executed by the same virtual thread.

**Best Practice:** Use `Scoped Values` (JEP 446), which are specifically designed for the virtual thread era, or ensure `ThreadLocal` variables are strictly cleared in a `finally` block.

---

## 7\. Conclusion

Incremental adoption of Virtual Threads via `CompletableFuture` provides a highly effective, low-risk strategy for modernizing legacy Spring Boot applications. By replacing the `ForkJoinPool.commonPool()` with `Executors.newVirtualThreadPerTaskExecutor()`, developers can safely parallelize blocking I/O operations, achieving massive reductions in p99 latency without the memory overhead of traditional thread pools.

In **Part 3** of this series, we will tackle the most contentious topic in the Java ecosystem: The WebFlux Reality Check. We will explore how Virtual Threads interact with reactive pipelines, and demonstrate how to elegantly bridge legacy blocking libraries (like OpenFeign and Filesystem I/O) into a WebFlux application without destroying its non-blocking guarantees.

---

## 8\. References

[1] Oracle Java Documentation. *ForkJoinPool*. Retrieved from https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ForkJoinPool.html
[2] Goetz, B., Peierls, T., et al. (2006). *Java Concurrency in Practice*. Addison-Wesley Professional.
[3] OpenJDK. *JEP 444: Virtual Threads*. Retrieved from https://openjdk.org/jeps/444
[4] OpenJDK. *JEP 444: Virtual Threads - Pinning*. Retrieved from https://openjdk.org/jeps/444#Pinning
[5] OpenJDK. *JEP 446: Scoped Values (Preview)*. Retrieved from https://openjdk.org/jeps/446

---

### Over to you, Paulo!

This gives you the exact blueprint to build the `/api/dashboard` endpoints, run the three-way comparison, and capture the Micrometer data. The contrast between the Common Pool collapsing at high concurrency and the Virtual Threads scaling linearly will make for an incredible chart in your article.

Before you run off to code this, I have a Socratic question to help us prepare for **Part 3 (The WebFlux Reality Check)**:

**For the WebFlux hybrid bridge, which of your two pain points causes you more grief in your day-to-day work: The complex `DataBuffer` filesystem streaming, or the strict prohibition of blocking OpenFeign clients?**

Knowing which one hurts more will help us decide which one should be the "hero" example in Part 3!

I would say data buffer. due to the blocking nature of feign I usually skip it completely. but before that I have a suggestion for you. instead of implementing a slow API to showcase, what about using wiremock? we can quickly put together an API and have it delay the response. we can even make it more close to really by setting the delay to not be fixed, what do you think?

---

This is an **excellent** suggestion, Paulo! Using WireMock is far superior to artificial `Thread.sleep()` for several reasons:

1. **Real Network Overhead**: You'll capture actual HTTP client serialization, socket latency, and JSON parsing overhead
2. **Variable Latency**: Real APIs don't have fixed 500ms delays—they have jitter, network congestion, and variable processing times
3. **Industry Credibility**: WireMock is the standard for contract testing; using it shows production-grade rigor
4. **Testcontainers Integration**: WireMock has official Testcontainers support, making it trivial to spin up

Let me provide you with the complete implementation.

---

### 🔧 Implementation: WireMock with Variable Delays
