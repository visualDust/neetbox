import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import HomepageFeatures from "@site/src/components/HomepageFeatures";

import styles from "./index.module.css";

type HowToItem = {
  image: string;
  description: string;
  buttonLink?: string;
  buttonText?: string;
};

type FeatureItem = {
  image: string;
  subtitle: string;
  description: string;
  link: string;
};

export function HowToCard({
  image,
  description,
  buttonLink,
  buttonText,
}: HowToItem) {
  return (
    <div
      className={styles["feature-card"]}
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <div className="text--center">
        <img src={image} style={{ borderRadius: "30px" }} />
      </div>
      <div
        style={{
          display: "flex",
          margin: "30px",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <div className={clsx("text--center", styles["feature-card-text"])}>
          <p>{description}</p>
        </div>
        {buttonLink ? (
          <div style={{ textAlign: "center" }}>
            <a href={buttonLink} className="button button--secondary">
              {buttonText}
            </a>
          </div>
        ) : null}
      </div>
    </div>
  );
}

const HowToList = [
  {
    image: "/img/index/monit-one-machine.png",
    description: "Monit running python codes on your own computer",
    buttonLink: "/docs/howto",
    buttonText: "Use on one computer",
  },
  {
    image: "/img/index/monit-machines-on-local-network.png",
    description:
      "Monit some python codes running on multiple machines connected to same network",
    buttonLink: "/docs/howto",
    buttonText: "Use on some computers",
  },
  {
    image: "/img/index/monit-machines-online.png",
    description:
      "Monit some python codes running on different machines connected to different networks",
    buttonLink: "/docs/howto",
    buttonText: "Use on a lot of computers",
  },
];

export function FeatureCard({
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
        <img src={image} />
      </div>
    </div>
  );
}

const FeatureList = [
  {
    image: "/img/index/neetbox-consistof.jpg",
    subtitle: "All in one",
    description:
      "Neetbox provides python side apis, command line cli app, web service, and frontend pages. Get ready by a single pip install, no registers, no extra steps, on extra configs, install and run by once. ",
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
    subtitle: "Monit everywhere",
    description:
      "View multiple projects running on different machines remotely, or view history data when projects are offline. Select project to view in you frontend sidebar.",
    link: "/docs/howto",
  },
  {
    image: "/img/index/distinguish-runs.jpg",
    subtitle: "Distinguish runs",
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

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`Hello from ${siteConfig.title}`} description="">
      <div>
        <header
          className={clsx("hero hero--primary")}
          style={{ display: "flex", flexDirection: "column" }}
        >
          <h1 className="hero__title">
            <div>{siteConfig.title}</div>
          </h1>
        </header>
        <div
          style={{
            padding: "10px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginTop: "50px",
          }}
        >
          <div
            style={{
              maxWidth: "1000px",
              display: "flex",
              flexDirection: "row",
              justifyContent: "space-evenly",
              gap: "30px",
            }}
          >
            {HowToList.map((props, idx) => (
              <HowToCard key={idx} {...props} />
            ))}
          </div>
          <div style={{ marginTop: "50px" }}>
            <h2>Why NEETBOX?</h2>
            <div
              style={{
                maxWidth: "1000px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-evenly",
                marginTop: "20px",
                gap: "10px",
              }}
            >
              {FeatureList.map((props, idx) => (
                <FeatureCard key={idx} {...props} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
