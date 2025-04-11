import { CSSProperties } from "react";
import styles from "./logo.module.css";

type LogoProps = {
  styles?: CSSProperties;
  className?: string;
  withGlow?: boolean;
  withLink?: boolean;
  withTitle?: boolean;
};

export default function Logo(props: LogoProps) {
  const { withLink = false, withGlow = false } = props;
  const url = withLink ? "https://neetbox.550w.host" : undefined;
  const glowStyleClassName = withGlow ? styles["neet-logo-glow"] : undefined;
  const combinedStyles: CSSProperties = {
    ...{}, // add default style here
    ...props.styles,
  };
  const imageComponent = (
    <img
      className={glowStyleClassName}
      src={process.env.ASSET_PREFIX + "/logo-no-bg.svg"}
      style={combinedStyles}
    />
  );
  return (
    <div className={props.className}>
      <a href={url} target="_blank">
        {imageComponent}
      </a>
    </div>
  );
}
