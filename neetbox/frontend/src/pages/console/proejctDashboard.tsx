import { useParams } from "react-router-dom";
import { useMemo } from "react";
import * as echarts from "echarts";
import { Typography } from "@douyinfe/semi-ui";
import PlatformProps from "../../components/dashboard/project/platformProps";
import { ECharts } from "../../components/echarts";
import { ProjectData, useProjectData } from "../../services/projects";

export default function ProjectDashboardButRecreateOnRouteChange() {
  const { projectName } = useParams();
  return <ProjectDashboard key={projectName} />;
}

function ProjectDashboard() {
  const { projectName } = useParams();
  const data = useProjectData(projectName!);

  console.info("project", { projectName, data });
  if (!data.data) return <div>Loading...</div>;
  return (
    <div style={{ padding: "10px" }}>
      <Typography.Title heading={2} style={{ textAlign: "center" }}>
        Project "{projectName}"
      </Typography.Title>
      <Hardware hardwareData={data.history.map((x) => x.hardware)} />
      <PlatformProps data={data.data.platform} />
    </div>
  );
}

function Hardware({
  hardwareData,
}: {
  hardwareData: Array<ProjectData["hardware"]>;
}) {
  return (
    <div>
      <Typography.Title heading={3}>Hardware</Typography.Title>
      <CPUGraph hardwareData={hardwareData} />
    </div>
  );
}

const CPUGraph = ({
  hardwareData,
}: {
  hardwareData: Array<ProjectData["hardware"]>;
}) => {
  const cpus = hardwareData[0].value.cpus;
  const initialOption = () => {
    return {
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: cpus.map((cpu) => `CPU${cpu.id}`),
      },
      xAxis: {
        type: "time",
      },
      yAxis: {
        type: "value",
        max: cpus.length * 100,
      },
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const latestTime = hardwareData[hardwareData.length - 1].timestamp;
    const newOption = {
      series: cpus.map((cpu) => ({
        name: `CPU${cpu.id}`,
        type: "line",
        stack: "cpu",
        areaStyle: {},
        symbol: null,
        data: hardwareData.map((x) => [
          x.timestamp * 1000,
          x.value.cpus[cpu.id].percent,
        ]),
      })),
      xAxis: {
        min: (latestTime - 60) * 1000,
        max: latestTime * 1000,
        data: new Array(10).fill(0).map((x, i) => i),
      },
    } as echarts.EChartsOption;
    return newOption;
  }, [hardwareData]);

  return (
    <ECharts
      initialOption={initialOption}
      updatingOption={updatingOption}
      style={{ height: "300px" }}
    />
  );
};
