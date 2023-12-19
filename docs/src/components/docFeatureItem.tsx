import React, { useState, useEffect } from "react";
import { Carousel } from "react-responsive-carousel";
import useIsMobile from "../hooks/useIsMobile";

export type BadgeItem = {
  imgUrls: string[];
  title: string;
  text: string;
};

function BadgeDesktop({ imgUrls, title, text }: BadgeItem): JSX.Element {
  return (
    <div style={{ display: "flex", flexDirection: "row" }}>
      <div
        style={{
          display: "flex",
          flex: "1",
          flexDirection: "column",
          textAlign: "left",
          paddingRight: "3%",
        }}
      >
        <div>
          <h3>{title}</h3>
          <p>{text}</p>
        </div>
      </div>
      <Carousel
        showArrows={true}
        autoPlay={true}
        showIndicators={false}
        swipeable={false}
        infiniteLoop={true}
      >
        {imgUrls.map((src, idx) => (
          <img key={idx} style={{ objectFit: "fill" }} src={src} />
        ))}
      </Carousel>
    </div>
  );
}

function BadgeMobile({ imgUrls, title, text }: BadgeItem): JSX.Element {
  return (
    <div
      style={{
        backgroundColor: "var(--floating-card-background)",
        borderRadius: "0 0 20px 20px",
      }}
    >
      <div
        style={{
          position: "relative",
        }}
      >
        <Carousel
          showArrows={true}
          autoPlay={true}
          showIndicators={false}
          swipeable={false}
          infiniteLoop={true}
        >
          {imgUrls.map((src, idx) => (
            <img key={idx} style={{ objectFit: "fill" }} src={src} />
          ))}
        </Carousel>
        <h3
          style={{
            position: "absolute",
            left: "5%",
            top: "5%",
            width: "100%",
            textAlign: "left",
            textShadow: "var(--ifm-color-emphasis-0) 1px 0 10px",
          }}
        >
          {title}
        </h3>
      </div>
      <div
        style={{
          backgroundColor: "var(--floating-card-background)",
          padding: "0 3% 3% 3%",
          borderRadius: "0 0 20px 20px",
        }}
      >
        <p style={{ margin: "0" }}>{text}</p>
      </div>
    </div>
  );
}

function FeatureBadgeMobile(badgeItem): JSX.Element {
  return (
    <div style={{ margin: "5%" }}>
      <h3 style={{ textAlign: "center" }}>Recently Maintaining</h3>
      <BadgeMobile {...badgeItem} />
    </div>
  );
}

function FeatureBadgeDesktop(badgeItem): JSX.Element {
  return (
    <div style={{ margin: "5%", maxWidth: "1000px" }}>
      <h3 style={{ textAlign: "end" }}>Recently Maintaining</h3>
      <BadgeDesktop {...badgeItem} />
    </div>
  );
}

function DocFeatureItem(badgeItem): JSX.Element {
  const isTabletOrMobile = useIsMobile();
  return isTabletOrMobile
    ? FeatureBadgeMobile(badgeItem)
    : FeatureBadgeDesktop(badgeItem);
}

export default DocFeatureItem;
