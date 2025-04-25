import React from "react";
import clsx from "clsx";
import styles from "./features.module.css";
import useIsMobile from "../hooks/useIsMobile";
type FeatureItem = {
  image: string;
  subtitle: string;
  description: string;
  link: string;
};

export function FeatureCardDesktop({
  image,
  subtitle,
  description,
  link,
}: FeatureItem) {
  return (
    <div
      className={styles["feature-card"]}
      style={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        boxShadow: "5px 5px 5px rgba(0, 0, 0, 0.5)",
      }}
    >
      <div
        style={{
          display: "flex",
          margin: "30px",
          flexDirection: "column",
          justifyContent: "center",
          flex: "50%",
        }}
      >
        <a href={link}>
          <h3 style={{ fontStyle: "italic" }}>{subtitle}</h3>
        </a>
        <div className={clsx(styles["feature-card-text"])}>
          <p>{description}</p>
        </div>
      </div>
      <div
        style={{
          display: "flex",
          flex: "50%",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <img
          style={{ height: "100%", borderRadius: "0 10px 10px 0" }}
          src={image}
        />
      </div>
    </div>
  );
}

export function FeatureCardMobile({
  image,
  subtitle,
  description,
  link,
}: FeatureItem) {
  return (
    <div
      className={styles["feature-card"]}
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxShadow: "5px 5px 5px rgba(0, 0, 0, 0.5)",
      }}
    >
      <img style={{ borderRadius: "10px 10px 0 0" }} src={image} />
      <div
        style={{
          margin: "20px 20px 0px 20px",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <a href={link}>
          <h3 style={{ fontStyle: "italic" }}>{subtitle}</h3>
        </a>
        <div
          style={{
            color: "var(--ifm-color-content-secondary)",
            textAlign: "justify",
          }}
        >
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export function FeatureCard({
  image,
  subtitle,
  description,
  link,
}: FeatureItem) {
  const isMobile = useIsMobile();
  console.log(isMobile);
  const props = { image, subtitle, description, link };
  return isMobile ? FeatureCardMobile(props) : FeatureCardDesktop(props);
}

export const FeatureList = [
  {
    image: "/img/index/view-everywhere.jpg",
    subtitle: "View everywhere",
    description:
      "Monit your projects everywhere on any devides with a browser. visit neetbox frontend console on PC, tablets, even phones.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/simple-apis.jpg",
    subtitle: "Easy python APIs",
    description:
      "Neetbox provides functions and function decorators for python codes. Neetbox python APIs are designed for easy purpose, they automatically connects your projects and web.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/support-different-data.jpg",
    subtitle: "Send types of data",
    description:
      "Neetbox provides apis for different data types, data such as logs, images, scalars etc. are stored in history database and send to frontend automatically. View your data in a single dashboard.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/monit-multiple-projects.jpg",
    subtitle: "View projects on different machines",
    description:
      "View multiple projects running on different machines remotely, or view history data when projects are offline. Select project to view in you frontend sidebar.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/distinguish-runs.jpg",
    subtitle: "Manage projects and runs",
    description:
      "Neetbox knows each time your project runs. Neetbox provides Tensorboard like viewing strateg. You can specific name of a run or select which run to view in frontend.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/use-actions.jpg",
    subtitle: "Remote function call",
    description:
      "Register a python function as an neetbox action, so that i appears as a button on your frontend console. Neetbox allows you to monit your running projects interactively.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/monit-hardware.jpg",
    subtitle: "Check hardware usage",
    description:
      "Neetbox automatically apply hardware monitoring when project launch.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/notify-errors.jpg",
    subtitle: "Notice on error",
    description:
      "Once neetbox frontend is opened in your browser, it shows notifications when there are errors or something needs attention. Solve crashes in time with neetbox.",
    link: "/docs/howto",
  },
];
