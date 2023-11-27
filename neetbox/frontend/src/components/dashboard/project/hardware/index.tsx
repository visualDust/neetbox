import { Typography } from "@douyinfe/semi-ui";
import { ProjectStatus } from "../../../../services/projects";
import { CPUGraph } from "./cpugraph";
import { GPUGraph } from "./gpugraph";

export function Hardware({
  hardwareData,
}: {
  hardwareData: Array<ProjectStatus["hardware"]>;
}) {
  return (
    <div>
      {hardwareData.every((x) => x.value.cpus) ? (
        <CPUGraph hardwareData={hardwareData} />
      ) : (
        <Typography.Text>No CPU Info</Typography.Text>
      )}
      {hardwareData.every((x) => x.value.gpus) ? (
        hardwareData[0].value.gpus.map((_, i) => (
          <GPUGraph key={i} hardwareData={hardwareData} gpuId={i} />
        ))
      ) : (
        <Typography.Text>No GPU Info</Typography.Text>
      )}
    </div>
  );
}
