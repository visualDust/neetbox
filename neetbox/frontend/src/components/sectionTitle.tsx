import { Typography } from "@douyinfe/semi-ui";

interface Props {
  title: string;
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
