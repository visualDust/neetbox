import { useRouteError } from "react-router";

export const RouteError = () => {
  const error = useRouteError();
  const text = `${error}\n\n${(error as Error)?.stack}`;
  return <pre style={{ whiteSpace: "pre-wrap", margin: 10 }}>{text}</pre>;
};
