import React from "react";
import { Divider, Layout, Typography } from "@douyinfe/semi-ui";
import Logo from "../logo";

export default function AppFooter(): React.JSX.Element {
  return (
    <Layout.Footer
      style={{
        textAlign: "center",
        alignItems: "center",
        display: "flex",
        flexDirection: "column",
        padding: "10px",
        gap: "10px",
      }}
    >
      <Divider />
      <Logo styles={{ width: 50 }} withGlow={true} withLink={true} />
      <Typography.Text type="tertiary" style={{ fontSize: 14 }}>
        © 2023 - {new Date().getFullYear()} Neet Design. All rights reserved.
      </Typography.Text>
    </Layout.Footer>
  );
}
