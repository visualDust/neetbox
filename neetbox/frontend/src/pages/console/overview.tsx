import { useParams } from "react-router-dom";
import { useAPI } from "../../hooks/useAPI";

export default function Overview() {
  // const { projectName } = useParams();
  // const { isLoading, data, error } = useAPI("/status/" + projectName);
  // if (!data) return <div>Loading...</div>;
  // console.info({ isLoading, data });
  return <div>Overview</div>;
}
