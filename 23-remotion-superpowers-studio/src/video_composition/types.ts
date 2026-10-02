export interface SceneData {
  id: string;
  title: string;
  startFrame: number;
  durationInFrames: number;
  headline: string;
  subheadline: string;
  bgGradient: string;
  accentColor: string;
  badge: string;
  code?: string;
}

export interface VideoProps {
  scenes: SceneData[];
  title: string;
}
