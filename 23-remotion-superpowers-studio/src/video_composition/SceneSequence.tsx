import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneData } from "./types";

export const SceneSequence: React.FC<{ scene: SceneData; sceneIndex: number; totalScenes: number }> = ({
  scene,
  sceneIndex,
  totalScenes,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrada suave con spring
  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  const translateY = interpolate(enterSpring, [0, 1], [60, 0]);
  const scale = interpolate(enterSpring, [0, 1], [0.95, 1]);
  const opacity = interpolate(enterSpring, [0, 1], [0, 1]);

  // Salida suave al final de la escena
  const exitFrames = 15;
  const exitProgress = interpolate(
    frame,
    [scene.durationInFrames - exitFrames, scene.durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const exitOpacity = 1 - exitProgress;
  const exitY = interpolate(exitProgress, [0, 1], [0, -30]);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: scene.bgGradient,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "80px 140px",
        fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 1400,
          display: "flex",
          flexDirection: "column",
          gap: 28,
          opacity: opacity * exitOpacity,
          transform: `translateY(${translateY + exitY}px) scale(${scale})`,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span
            style={{
              padding: "8px 20px",
              borderRadius: 9999,
              fontSize: 22,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: scene.accentColor,
              backgroundColor: `${scene.accentColor}22`,
              border: `1px solid ${scene.accentColor}66`,
            }}
          >
            {scene.badge}
          </span>
          <span style={{ fontSize: 22, color: "#94a3b8", fontWeight: 500 }}>
            Escena {sceneIndex + 1} de {totalScenes}
          </span>
        </div>

        <h1
          style={{
            fontSize: 72,
            lineHeight: 1.15,
            fontWeight: 800,
            color: "#ffffff",
            textShadow: "0 4px 24px rgba(0,0,0,0.6)",
          }}
        >
          {scene.headline}
        </h1>

        <p
          style={{
            fontSize: 34,
            lineHeight: 1.4,
            color: "#cbd5e1",
            maxWidth: 1100,
          }}
        >
          {scene.subheadline}
        </p>

        {scene.code && (
          <div
            style={{
              marginTop: 10,
              backgroundColor: "#0b1120",
              border: "1px solid #1e293b",
              borderRadius: 16,
              padding: "24px 32px",
              boxShadow: "0 20px 40px rgba(0,0,0,0.4)",
            }}
          >
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#ef4444" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#f59e0b" }} />
              <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#10b981" }} />
            </div>
            <code style={{ fontFamily: "Consolas, monospace", fontSize: 32, color: "#38bdf8" }}>
              {scene.code}
            </code>
          </div>
        )}
      </div>
    </div>
  );
};
