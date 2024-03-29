import { Typography } from "@douyinfe/semi-ui";
import { HardwareInfo } from "../../../services/types";
import { useCurrentProject, useProjectData } from "../../../hooks/useProject";
import Loading from "../../common/loading";
import { TimeDataMapper } from "../../../utils/timeDataMapper";
import { CPUGraph } from "./cpugraph";
import { GPUGraph } from "./gpugraph";
import { RAMGraph } from "./ramgraph";
import { fetchDataCount } from "./utils";

export function Hardware() {
  const { projectId, runId } = useCurrentProject();
  const data = useProjectData<HardwareInfo>({
    projectId,
    runId,
    type: "hardware",
    transformHTTP: (x) => ({ timestamp: x.timestamp, ...x.metadata }),
    transformWS: (x) => ({ timestamp: x.timestamp, ...x.payload }),
    limit: fetchDataCount,
  });
  return data?.length ? (
    <div>
      {data.every((x) => x.gpus?.length) ? (
        data[0].gpus.map((_, i) => <GPUGraph key={i} data={new TimeDataMapper(data, (x) => x.gpus[i])} />)
      ) : (
        <NoInfoLabel text="No GPU Info" />
      )}
      {data.every((x) => x.cpus.length) ? (
        <CPUGraph data={new TimeDataMapper(data, (x) => x.cpus)} />
      ) : (
        <NoInfoLabel text="No CPU Info" />
      )}
      {data.every((x) => x.ram) ? (
        <RAMGraph data={new TimeDataMapper(data, (x) => x.ram)} />
      ) : (
        <NoInfoLabel text="No RAM Info" />
      )}
    </div>
  ) : (
    <Loading size="large" />
  );
}

function NoInfoLabel({ text }: { text: string }) {
  return (
    <Typography.Text style={{ marginLeft: "5px" }} type="tertiary">
      {text}
    </Typography.Text>
  );
}
