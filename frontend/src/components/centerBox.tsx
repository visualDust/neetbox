import { CSSProperties, PropsWithChildren } from "react";

export const CenterBox = (props: PropsWithChildren<{ style?: CSSProperties }>) => {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", ...props.style }}>
      {props.children}
    </div>
  );
};
