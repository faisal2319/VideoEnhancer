import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import React from "react";
import StepTracker from "./StepTracker";

interface TaskStatus {
  task_id: string;
  status: any;
  progress: number;
  step: string;
  enhanced_video_path?: string;
  enhanced_video_url?: string;
}

interface ProgressSectionProps {
  taskStatus: TaskStatus | null;
}

const ProgressSection: React.FC<ProgressSectionProps> = ({ taskStatus }) => {
  if (!taskStatus) return null;
  return (
    <Card>
      <CardHeader>
        <CardTitle>Enhancement Progress</CardTitle>
        <CardDescription>
          {taskStatus.step === "COMPLETE"
            ? "Enhancement completed!"
            : "Processing your video..."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <StepTracker step={taskStatus.step} />
        {taskStatus.status?.meta && (
          <div className="text-xs text-muted-foreground space-y-1 mt-2">
            {taskStatus.status.meta.total_frames && (
              <p>Total frames: {taskStatus.status.meta.total_frames}</p>
            )}
            {taskStatus.status.meta.analyzed_frames && (
              <p>Analyzed frames: {taskStatus.status.meta.analyzed_frames}</p>
            )}
            {taskStatus.status.meta.enhanced_count && (
              <p>Enhanced frames: {taskStatus.status.meta.enhanced_count}</p>
            )}
            {taskStatus.status.meta.copied_count && (
              <p>Copied frames: {taskStatus.status.meta.copied_count}</p>
            )}
            {taskStatus.status.meta.blurry_count && (
              <p>Blurry frames: {taskStatus.status.meta.blurry_count}</p>
            )}
            {taskStatus.status.meta.dark_count && (
              <p>Dark frames: {taskStatus.status.meta.dark_count}</p>
            )}
            {taskStatus.status.meta.good_count && (
              <p>Good frames: {taskStatus.status.meta.good_count}</p>
            )}
            {taskStatus.status.meta.current_frame && (
              <p>
                Processing frame: {taskStatus.status.meta.current_frame} /{" "}
                {taskStatus.status.meta.total_frames}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressSection;
