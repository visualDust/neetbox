import React, { JSX } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import { FeatureCard, FeatureList } from "../components/FeatureCards";
import { useColorMode } from '@docusaurus/theme-common';

function BackgroundImageBlur() {
  const { colorMode } = useColorMode();

  const imageUrl = colorMode === 'dark' ? '/img/index/background-dark.jpg' : '/img/index/background-light.jpg';
  return (<div
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundImage: `url(${imageUrl})`,
      backgroundSize: "cover",
      backgroundRepeat: "no-repeat",
      backgroundPosition: "center",
      backgroundAttachment: "fixed",
      filter: "blur(5px)",
      zIndex: 1,
    }}
  />);
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout title={`${siteConfig.title}`} description="NEETBOX provides the visualization and tooling needed for machine learning experimentation.">
      <div style={{ position: "relative", height: "100vh", overflow: "hidden" }}>
        {/* Blurred background */}
        <BackgroundImageBlur />

        {/* Optional overlay tint */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.2)",
            zIndex: 2,
          }}
        />

        {/* Content Layer */}
        <div
          style={{
            position: "relative",
            zIndex: 3,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            paddingLeft: "10%",
            paddingRight: "10%",
            paddingBottom: "var(--ifm-navbar-height)",
          }}
        >
          <div style={{ maxWidth: "90%", textAlign: "center" }}>
            <h1
              style={{
                color: "white",
                textShadow: "3px 3px 3px black",
              }}
            >
              {siteConfig.title}
            </h1>
            <h3
              style={{
                color: "white",
                textShadow: "1px 1px 1px black",
              }}
            >
              NEETBOX provides the visualization and tooling needed for machine learning experimentation.
            </h3>
            <div
              style={{
                marginTop: "10px",
                display: "flex",
                justifyContent: "center",
                gap: "10px",
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
      </div>

      <div id="howtos">
        <div
          style={{
            paddingBottom: "50px",
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
