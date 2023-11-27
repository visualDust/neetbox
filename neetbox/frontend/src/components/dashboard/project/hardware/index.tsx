import { Typography } from "@douyinfe/semi-ui";
import { ProjectStatus } from "../../../../services/projects";
import { CPUGraph } from "./cpugraph";

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
    </div>
  );
}
