import React from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import { FeatureCard, FeatureList } from "../components/FeatureCards";

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`Hello from ${siteConfig.title}`} description="">
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          backgroundImage: "url('/img/index/background.jpg')",
          backgroundSize: "cover",
          backgroundRepeat: "no-repeat",
          backgroundPosition: "center",
          backgroundAttachment: "fixed",
          height: "100vh",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            paddingLeft: "10%",
            paddingRight: "10%",
            maxWidth: "90%",
            justifyContent: "center",
            paddingBottom: "var(--ifm-navbar-height)",
          }}
        >
          <h1
            style={{
              color: "white",
              textShadow: "3px 3px 3px black",
              textAlign: "center",
            }}
          >
            {siteConfig.title}
          </h1>
          <h3
            style={{
              color: "white",
              textShadow: "1px 1px 1px black",
              textAlign: "center",
            }}
          >
            A tool box for Logging / Debugging / Tracing / Managing /
            Facilitating long running python projects, especially a replacement
            of tensorboard for deep learning projects.
          </h3>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <div style={{ display: "flex", gap: "5px" }}>
              <img src="https://img.shields.io/badge/linux-x86%20or%20arm-blue?logo=linux" />
              <img src="https://img.shields.io/badge/windows-x86%20or%20arm-blue?logo=windows" />
              <img src="https://img.shields.io/badge/mac-intel%20or%20apple%20silicon-blue?logo=apple" />
            </div>
          </div>
          <div style={{ paddingTop: "30px", textAlign: "center" }}>
            <a href="/docs/howto" className="button button--secondary">
              Get started
            </a>
          </div>
        </div>
      </div>
      <div id="howtos">
        <div
          style={{
            padding: "10px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            marginTop: "50px",
          }}
        >
          <h2>Why NEETBOX?</h2>

          <div
            style={{
              maxWidth: "1000px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-evenly",
              marginTop: "20px",
              gap: "20px",
            }}
          >
            {FeatureList.map((props, idx) => (
              <FeatureCard key={idx} {...props} />
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
