import { Typography, Space, Button, Layout } from "@douyinfe/semi-ui";
import { Link } from "react-router-dom";
import SwitchColorMode from "../themeSwitcher";
import { useTitle } from "../appTitle";
import Logo from "../logo";

export default function AppHeader() {
  const { title, extra } = useTitle();
  return (
    <Layout.Header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 20px",
        backgroundColor: "var(--semi-color-primary)",
      }}
    >
      <Typography.Title style={{ color: "var(--semi-color-default)", margin: 0 }}>NEETBOX</Typography.Title>
      <Typography.Title heading={2}>{title}</Typography.Title>
      {extra}
      <div>
        <Space>
          <SwitchColorMode />
          <Link to="/login">
            <Button theme="solid" type="tertiary" disabled>
              Login
            </Button>
          </Link>
        </Space>
      </div>
    </Layout.Header>
  );
}
