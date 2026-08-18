import copy
from runtime.memory.allocator import Allocator
from runtime.scheduler import Scheduler
from runtime.runtime import Runtime
from runtime.workload_loader import load_workload
from telemetry.broker import TelemetryBroker

def run_experiment():
    requests_base, model_meta = load_workload("workloads/requests.json")
    requests_closed = copy.deepcopy(requests_base)
    print(f"MODEL: {model_meta['name']} ({len(requests_base)} requests)\n")

    # open loop
    alloc_base = Allocator(total_blocks=48)
    sched_base = Scheduler()
    broker_base = TelemetryBroker()
    rt_base = Runtime(alloc_base, sched_base, requests_base, broker_base, closed_loop=False)
    summary_base = rt_base.run()

    # closed loop
    alloc_closed = Allocator(total_blocks=48)
    sched_closed = Scheduler()
    broker_closed = TelemetryBroker()
    rt_closed = Runtime(alloc_closed, sched_closed, requests_closed, broker_closed, closed_loop=True)
    summary_closed = rt_closed.run()

    print(f"{'Metric':<25} | {'Open-Loop (Baseline)':<20} | {'Closed-Loop (Telemetry)':<25}")
    print("-" * 75)
    
    metrics_to_show = ["completed_requests", "total_cycles", "average_latency", "slo_violations", "slo_attainment", "telemetry_events"]
    for k in metrics_to_show:
        print(f"{k:<25} | {str(summary_base.get(k, 0)):<20} | {str(summary_closed.get(k, 0)):<25}")

    print ()
    print(f"TELEMETRY TAX: {summary_closed.get("telemetry_tax_cycles", 0)} cycles")

    # closed loop telemetry breakdown
    print("\n--- Closed-Loop Telemetry Event Breakdown ---")
    summary = broker_closed.get_summary()
    print(f"Final Memory Pressure: {summary['memory_utilization_current']}")
    print(f"Memory Congestion Detected: {summary['memory_congested_signal']}")
    print(f"Hardware Bottleneck Detected: {summary['hardware_bottleneck_signal']}\n")
    
    for ev_name, count in sorted(summary["event_breakdown"].items()):
        is_hw = any(prefix in ev_name for prefix in ["DMA", "SRAM", "SYSTOLIC", "HARDWARE"])
        category = "Hardware" if is_hw else "Runtime"
        print(f"  [{category:<8}] {ev_name:<25}: {count}")

    print("\n--- Execution Timeline (Closed-Loop) ---")
    if not summary['traces']:
        print("  (No traces logged. Ensure runtime.py passes broker to scheduler.schedule())")
    else:
        for trace in summary['traces']:
            print(f"  {trace}")

    # per request breakdown
    print("\n--- Per-Request Breakdown (Closed-Loop) ---")
    print(f"{'Req ID':<8} | {'Arrival':<8} | {'Start':<8} | {'Finish':<8} | {'Latency':<8} | {'SLO':<8} | {'Met SLO?':<10}")
    print("-" * 75)
    for req in sorted(requests_closed, key=lambda r: r.request_id):
        met_slo = "Yes" if (req.latency > 0 and req.latency <= req.slo_deadline) else "No"
        print(f"{req.request_id:<8} | {req.arrival_time:<8} | {req.start_cycle:<8} | {req.finish_cycle:<8} | {req.latency:<8} | {req.slo_deadline:<8} | {met_slo:<10}")

    # force C++ memory cleanup before python unloads shared library
    rt_base.shutdown()
    rt_closed.shutdown()

if __name__ == "__main__":
    run_experiment()