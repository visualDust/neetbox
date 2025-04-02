import { CardGroup, Divider } from "@douyinfe/semi-ui";
import { SectionTitle } from "../../components/common/sectionTitle";
import { ServerPropsCard } from "../../components/overview/serverProps";
import { DiskUsageCard } from "../../components/overview/diskUsage";
import { ProjectCards } from "../../components/overview/projectCards";

export default function Overview() {
  return (
    <div style={{ padding: "20px", position: "relative" }}>
      <SectionTitle title="Projects" />
      <ProjectCards />
      <Divider margin="10px" />
      <SectionTitle title="Server Information" />
      <CardGroup spacing={10}>
        <DiskUsageCard />
        <ServerPropsCard />
      </CardGroup>
    </div>
  );
}
