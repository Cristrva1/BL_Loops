import React from "react";
import { Composition } from "remotion";
import { MainComposition } from "./MainComposition";
import scenesData from "./scenes.json";
import { SceneData } from "./types";

export const Root: React.FC = () => {
  const scenes: SceneData[] = scenesData as SceneData[];
  const totalFrames = scenes.reduce((acc, s) => acc + s.durationInFrames, 0);

  return (
    <Composition
      id="MainVideo"
      component={MainComposition}
      durationInFrames={totalFrames || 360}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
