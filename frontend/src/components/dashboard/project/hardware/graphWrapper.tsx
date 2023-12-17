import { PropsWithChildren, memo } from "react";
import { JsonPopover } from "../jsonView";

export const GraphWrapper = memo(
  ({ title, lastValue, children }: PropsWithChildren<{ title: string; lastValue: any }>) => {
    return (
      <div style={{ position: "relative" }}>
        {children}
        <JsonPopover
          title={title}
          value={lastValue}
          position="right"
          style={{ position: "absolute", left: 5, top: 3 }}
        />
      </div>
    );
  },
);
