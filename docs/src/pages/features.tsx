import React from "react";
import clsx from "clsx";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import { FeatureList } from ".";
import styles from "./index.module.css";
import { Carousel } from "react-responsive-carousel";
type FeatureItem = {
  image: string;
  subtitle: string;
  description: string;
  link: string;
};

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
        <img
          src={image}
          style={{ boxShadow: "rgba(0, 0, 0, 0.05) 0px 0px 0px 1px" }}
        />
      </div>
    </div>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`Hello from ${siteConfig.title}`} description="">
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          backgroundColor: "green",
          width: "100%",
          height: "100vh",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            backgroundColor: "red",
            width: "90%",
            height: "50%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <Carousel>
            {FeatureList.map((props, idx) => (
              <FeatureCard key={idx} {...props} />
            ))}
          </Carousel>
        </div>
      </div>
    </Layout>
  );
}
