import { SectionTitle } from "../../components/common/sectionTitle";
import { ServerPropsCard } from "../../components/overview/serverProps";
import { DiskUsageCard } from "../../components/overview/diskUsage";
import { ProjectCards } from "../../components/overview/projectCards";

export default function Overview() {
  return (
    <div style={{ padding: "20px", position: "relative" }}>
      <SectionTitle title="Projects" />
      <ProjectCards />
      <SectionTitle title="Server Information" />
      <div style={{ display: "flex", flexDirection: "row", gap: "20px" }}>
        <DiskUsageCard />
        <ServerPropsCard />
      </div>
    </div>
  );
}
