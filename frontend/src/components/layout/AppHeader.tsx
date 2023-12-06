import { Typography, Space, Button, Layout } from "@douyinfe/semi-ui";
import { Link } from "react-router-dom";
import SwitchColorMode from "../themeSwitcher";
import { useTitle } from "../appTitle";

export default function AppHeader() {
  return (
    <Layout.Header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 20px",
      }}
    >
      <Typography.Title>
        <Link to="/">NEET Center</Link>
      </Typography.Title>
      <Typography.Title heading={2}>{useTitle()}</Typography.Title>
      <div>
        <Space>
          <SwitchColorMode></SwitchColorMode>
          <Link to="/login">
            <Button disabled>Login</Button>
          </Link>
        </Space>
      </div>
    </Layout.Header>
  );
}
