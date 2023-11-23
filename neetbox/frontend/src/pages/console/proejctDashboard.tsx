import { useParams } from "react-router-dom";
import { useRef, useEffect, useState, useMemo } from "react";
import * as echarts from "echarts";
import { useAPI } from "../../hooks/useAPI";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { ECharts } from "../../components/echarts";

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectName } = useParams();
  return <ProjectDashboard key={projectName} />;
}

function ProjectDashboard() {
  const { projectName } = useParams();
  const { isLoading, data, error } = useAPI("/status/" + projectName, {
    refreshInterval: 1000,
  });

  console.info({ isLoading, data });
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>{String(error)}</div>;
  return (
    <div>
      Dashboard for project {projectName}
      <Hardware hardwareData={data.hardware} />
      <PlatformProps data={data.platform} />
    </div>
  );
}

function Hardware({ hardwareData }) {
  return (
    <pre>
      Hardware:
      <CPUGraph
        cpuData={hardwareData.value.cpus}
        timestamp={hardwareData.timestamp}
      />
    </pre>
  );
}

function slideWindow<T>(arr: T[], item: T, max: number) {
  arr.push(item);
  if (arr.length > max) {
    arr.shift();
  }
  return arr;
}

const CPUGraph = ({ cpuData, timestamp }) => {
  type RecordItem = Array<[timestamp: number, percent: number]>;
  const [history, setHistory] = useState<Record<number, RecordItem>>({});
  useEffect(() => {
    setHistory(history =>
      Object.fromEntries(
        cpuData.map((cpu) => {
          return [
            cpu.id,
            slideWindow(
              history[cpu.id] ?? [],
              [timestamp * 1000, cpu.percent],
              20
            ),
          ];
        })
      )
    );
  }, [cpuData]);

  const initialOption = () => {
    return {
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: cpuData.map((cpu) => `CPU${cpu.id}`),
      },
      xAxis: {
        type: "time",
      },
      yAxis: {
        type: "value",
        max: cpuData.length * 100,
      },
      series: [],
    } as echarts.EChartsOption;
  }

  const updatingOption = useMemo(() => {
    const newOption = {
      series: Object.keys(history).map((cpuid) => ({
        name: `CPU${cpuid}`,
        type: "line",
        stack: "cpu",
        areaStyle: {},
        symbol: null,
        data: history[cpuid],
      })),
      xAxis: {
        // max: timestamp,
        data: new Array(10).fill(0).map((x, i) => i),
      },
    };
    return newOption;
  }, [history]);

  return <ECharts initialOption={initialOption} updatingOption={updatingOption} />;
};
