import { Empty } from "@douyinfe/semi-ui";
import { IllustrationNotFound } from "@douyinfe/semi-illustrations";
import { IllustrationNotFoundDark } from "@douyinfe/semi-illustrations";

() => {
  const emptyStyle = {
    padding: 30,
  };
  return (
    <div style={{ display: "flex", flexWrap: "wrap" }}>
      <Empty
        image={<IllustrationNotFound style={{ width: 150, height: 150 }} />}
        darkModeImage={<IllustrationNotFoundDark style={{ width: 150, height: 150 }} />}
        description={"OOOps..."}
        style={emptyStyle}
      />
    </div>
  );
};
