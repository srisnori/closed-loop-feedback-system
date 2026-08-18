# Closed-Loop LLM Inference Runtime

A hardware-software co-design simulator built to explore **memory fragmentation, head-of-line blocking, and the true cost of observability** in Large Language Model (LLM) serving systems. 

This project implements a custom Python scheduling runtime paired with a C++ simulated hardware accelerator. It demonstrates how continuous batching and scatter-gather memory allocation can maximize systolic array utilization, while explicitly profiling the latency tax of polling hardware registers across a simulated PCIe bus.

## Key Architectural Features

### 1. Paged Memory Allocator (Scatter-Gather)
Standard FIFOs suffer from severe memory fragmentation and head-of-line blocking during highly variable LLM workloads. Inspired by PagedAttention, this runtime implements a non-contiguous, block-based virtual memory allocator.
* **Impact:** Allows massive requests (e.g., 512-token prompts) to coexist with smaller requests without requiring contiguous SRAM space, entirely eliminating head-of-line blocking.

### 2. Earliest Deadline First (EDF) Continuous Batching
The runtime decouples the **Prefill** (compute-bound) and **Decode** (memory-bound) phases. When memory congestion occurs, the scheduler falls back to an Earliest Deadline First (EDF) algorithm, running smaller, highly urgent requests into the active continuous batch to protect Service Level Objectives (SLOs).
* **Anti-Starvation Lock:** Includes a starvation-prevention mechanism that halts out-of-order bypassing if a massive request is delayed more than 3 scheduling cycles.

### 3. Event-Driven Hardware Telemetry
Initial design utilized synchronous, cycle-by-cycle polling to bridge the C++ hardware state and the Python scheduler. This revealed a massive **"Telemetry Tax"**—the software spent 147% more time moving observability data across the PCIe bus than executing matrix multiplication.
* **Optimization:** Re-architected the C++/Python `ctypes` bridge to use **Event-Driven Telemetry**, halting bus polling when the scheduler queue is empty. This reduced the observability tax by **35%** while maintaining a 100% SLO attainment.

## 📊 Benchmarks & Performance

Running the `llama-3-8b` synthetic workload across a simulated 48-block memory pool:

| Metric | Open-Loop (Baseline) | Closed-Loop (Telemetry) |
| :--- | :--- | :--- |
| **Completed Requests** | 5 | 5 |
| **Total Hardware Cycles** | 157 | **139** *(+11% Throughput)* |
| **Average Latency** | 79.0 | **58.4** *(-26% Latency)* |
| **SLO Violations** | 2 | **0** |
| **SLO Attainment** | 60.0% | **100.0%** |

### The Cost of Observability
```text
TELEMETRY TAX: 132 cycles
