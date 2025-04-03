import { CardGroup, Divider } from "@douyinfe/semi-ui";
import { SectionTitle } from "../../components/common/sectionTitle";
import { ServerPropsCard } from "../../components/overview/serverProps";
import { DiskUsageCard } from "../../components/overview/diskUsage";
import ProjectList from "../../components/overview/projectList";

export default function Overview() {
  return (
    <div style={{ padding: "20px", position: "relative" }}>
      <SectionTitle title="Projects" />
      <ProjectList />
      <Divider margin="10px" />
      <SectionTitle title="Server Information" />
      <CardGroup spacing={10} style={{ alignItems: "flex-start" }}>
        <DiskUsageCard />
        <ServerPropsCard />
      </CardGroup>
    </div>
  );
}
