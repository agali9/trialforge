import { useEffect, useRef } from "react";
import uPlot from "uplot";
import "uplot/dist/uPlot.min.css";

export default function MetricChart({ data, metricName }: { data: number[][]; metricName: string }) {
  const root = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!root.current) return;
    const palette = ["#00E5C4", "#3B82F6", "#F59E0B", "#EF4444", "#A78BFA"];
    const chart = new uPlot(
      {
        title: metricName,
        width: root.current.clientWidth || 600,
        height: 240,
        scales: {
          x: { time: false },
        },
        series: [{ label: "step" }, ...data.slice(1).map((_, idx) => ({ stroke: palette[idx % palette.length], width: 2 }))],
        axes: [{ stroke: "#6B7280", label: "Step" }, { stroke: "#6B7280", label: metricName }],
      },
      data,
      root.current,
    );
    return () => chart.destroy();
  }, [data, metricName]);

  return <div ref={root} className="w-full" />;
}
