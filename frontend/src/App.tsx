import { Button } from "@douyinfe/semi-ui";
import { Link } from "react-router-dom";

export function Home() {
  return (
    <div>
      <Link to="/console">
        <Button>console</Button>
      </Link>
    </div>
  );
}
