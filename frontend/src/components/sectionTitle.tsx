import { Typography } from "@douyinfe/semi-ui";
import { ReactNode } from "react";

interface Props {
  title: ReactNode;
}

export function SectionTitle(props: Props) {
  return (
    <div>
      <Typography.Title heading={3} style={{ margin: "20px 0" }}>
        {props.title}
      </Typography.Title>
    </div>
  );
}
