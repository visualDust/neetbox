import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import HomepageFeatures from "@site/src/components/HomepageFeatures";

import styles from "./index.module.css";

type FeatureItem = {
  image: string;
  description: string;
  buttonLink?: string;
  buttonText?: string;
};

export function Feature({
  image,
  description,
  buttonLink,
  buttonText,
}: FeatureItem) {
  return (
    <div
      className={styles["feature-card"]}
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent:"space-between"
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

const FeatureList = [
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

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`Hello from ${siteConfig.title}`} description="">
      <div>
        <header
          className={clsx("hero hero--primary")}
          style={{ display: "flex", flexDirection: "column" }}
        >
          <h1 className="hero__title">{siteConfig.title}</h1>
        </header>
        <div
          style={{
            padding: "10px",
            display: "flex",
            flexDirection: "column",
            alignItems:"center",
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
            {FeatureList.map((props, idx) => (
              <Feature key={idx} {...props} />
            ))}
          </div>
          <div style={{ marginTop: "50px" }}>
            <h2>Why NEETBOX?</h2>
          </div>
        </div>
      </div>
    </Layout>
  );
}
