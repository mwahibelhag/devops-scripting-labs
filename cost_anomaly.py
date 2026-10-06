#!/usr/bin/env python3
import statistics
import sys
from datetime import datetime, timedelta
import boto3

def get_daily_costs(days=30):
    ce = boto3.client("ce", region_name="us-east-1")
    end = datetime.today().date() - timedelta(days=1)
    start = end - timedelta(days=days)
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": str(start), "End": str(end)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return response["ResultsByTime"]

def build_service_timeseries(results):
    services = {}
    for day in results:
        date_str = day["TimePeriod"]["Start"]
        for group in day["Groups"]:
            service = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            if service not in services:
                services[service] = []
            services[service].append({"date": date_str, "cost": cost})
    return services

def detect_anomalies(services, baseline_days=7, multiplier=2.0):
    anomalies = []
    for service, daily in services.items():
        if len(daily) < baseline_days + 1:
            continue
        for i in range(baseline_days, len(daily)):
            day = daily[i]
            baseline_costs = [d["cost"] for d in daily[i - baseline_days : i]]
            avg = statistics.mean(baseline_costs)
            if avg < 0.01:
                continue
            try:
                std = statistics.stdev(baseline_costs)
            except statistics.StatisticsError:
                continue
            threshold = avg + (multiplier * std)
            if day["cost"] > threshold:
                anomalies.append({
                    "service": service,
                    "date": day["date"],
                    "actual": round(day["cost"], 2),
                    "baseline_avg": round(avg, 2),
                    "pct_above": round(((day["cost"] - avg) / avg) * 100, 1)
                })
    return anomalies

if __name__ == "__main__":
    results = get_daily_costs(30)
    services = build_service_timeseries(results)
    anomalies = detect_anomalies(services)
    for a in anomalies:
        print(f"[ALERT] Service: {a['service']} | Date: {a['date']} | Actual: ${a['actual']} | Avg: ${a['baseline_avg']} | Spike: +{a['pct_above']}%")
        