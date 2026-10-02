import React from "react";
import { Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneSequence } from "./SceneSequence";
import scenesData from "./scenes.json";
import { SceneData } from "./types";

export const MainComposition: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scenes: SceneData[] = scenesData as SceneData[];

  const progress = Math.min(frame / durationInFrames, 1);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        backgroundColor: "#020617",
        overflow: "hidden",
      }}
    >
      {scenes.map((scene, idx) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
        >
          <SceneSequence scene={scene} sceneIndex={idx} totalScenes={scenes.length} />
        </Sequence>
      ))}

      {/* Footer Branding */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 140,
          right: 140,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: 20,
          color: "#64748b",
          borderTop: "1px solid rgba(255,255,255,0.1)",
          paddingTop: 20,
          fontFamily: "'Segoe UI', sans-serif",
        }}
      >
        <span style={{ fontWeight: 700, color: "#e2e8f0" }}>
          ⚡ BL_Loops · Remotion Superpowers Studio
        </span>
        <span>React Video Engine · Orquestación Agéntica con IA Local</span>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          height: 6,
          width: `${progress * 100}%`,
          background: "linear-gradient(90deg, #6366f1, #d946ef, #10b981)",
          transition: "width 0.05s linear",
        }}
      />
    </div>
  );
};
