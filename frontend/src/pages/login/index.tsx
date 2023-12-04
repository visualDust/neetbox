import { Form, Checkbox, Button } from "@douyinfe/semi-ui";
import Logo from "../../components/logo";
import styles from "./index.module.css";

const LoginPage = () => {
  return (
    <div className={styles.rootSignupLogins}>
      <div className={styles.main}>
        <div className={styles.login}>
          <Logo className={styles.logo} />
          <p className={styles.title}>NEET Center</p>
          <div className={styles.form}>
            <Form className={styles.inputs}>
              <Form.Input
                label={{ text: "Username" }}
                field="input"
                placeholder="input username"
                style={{ width: "100%" }}
                fieldStyle={{ alignSelf: "stretch", padding: 0 }}
              />
              <Form.Input
                label={{ text: "Password" }}
                field="field1"
                placeholder="input password"
                style={{ width: "100%" }}
                fieldStyle={{ alignSelf: "stretch", padding: 0 }}
              />
            </Form>
            <Checkbox type="default">remember me</Checkbox>
            <Button theme="solid" className={styles.button}>
              Login
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
