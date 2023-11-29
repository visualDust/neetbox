import { Typography } from "@douyinfe/semi-ui";
import { ProjectStatus } from "../../../../services/projects";
import { CPUGraph } from "./cpugraph";
import { GPUGraph } from "./gpugraph";
import { RAMGraph } from "./ramgraph";

export function Hardware({ hardwareData }: { hardwareData: Array<ProjectStatus["hardware"]> }) {
  return (
    <div>
      {hardwareData.every((x) => x.value.gpus.length) ? (
        hardwareData[0].value.gpus.map((_, i) => <GPUGraph key={i} hardwareData={hardwareData} gpuId={i} />)
      ) : (
        <NoInfoLabel text="No GPU Info" />
      )}
      {hardwareData.every((x) => x.value.cpus.length) ? (
        <CPUGraph hardwareData={hardwareData} />
      ) : (
        <NoInfoLabel text="No CPU Info" />
      )}
      {hardwareData.every((x) => x.value.ram) ? (
        <RAMGraph hardwareData={hardwareData} />
      ) : (
        <NoInfoLabel text="No RAM Info" />
      )}
    </div>
  );
}

function NoInfoLabel({ text }: { text: string }) {
  return (
    <Typography.Text style={{ marginLeft: "5px" }} type="tertiary">
      {text}
    </Typography.Text>
  );
}
