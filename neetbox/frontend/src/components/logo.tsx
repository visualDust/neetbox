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
  const { withLink = false, withTitle = false, withGlow = false } = props;
  const url = withLink ? "https://neetbox.550w.host" : undefined;
  const glowStyleClassName = withGlow ? styles["neet-logo-glow"] : undefined;
  const combinedStyles: CSSProperties = {
    ...{}, // add default style here
    ...props.styles,
  };
  const imageComponent = <img className={glowStyleClassName} src="/logo.svg" />;
  const titleComponent = withTitle ? <span>NEETBOX</span> : null;
  return (
    <div className={props.className} style={combinedStyles}>
      <a href={url} target="_blank">
        {imageComponent}
        {titleComponent}
      </a>
    </div>
  );
}
