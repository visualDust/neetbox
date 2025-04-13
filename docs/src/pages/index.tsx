import React from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import { FeatureCard, FeatureList } from "../components/FeatureCards";

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`${siteConfig.title}`} description="NEETBOX provides the visualization and tooling needed for machine learning experimentation.">
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
            NEETBOX provides the visualization and tooling needed for machine learning experimentation.
          </h3>
          <div
            style={{
              paddingTop: "10px",
              textAlign: "center",
              gap: "10px",
              display: "flex",
              justifyContent: "center",
            }}
          >
            <a
              href="/docs/howto"
              className="button button--primary"
              style={{ border: "1px solid" }}
            >
              Get started
            </a>
            <a
              href="https://github.com/visualDust/neetbox"
              className="button button--secondary"
              style={{ display: "flex", alignItems: "center", gap: "6px" }}
            >
              <img
                src="/img/github-mark.svg"
                alt="GitHub"
                style={{ width: "16px", height: "16px" }}
              />
              GitHub
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
