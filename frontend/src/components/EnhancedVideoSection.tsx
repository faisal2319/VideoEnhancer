import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import React from "react";

interface EnhancedVideoSectionProps {
  enhancedVideoUrl: string | null;
  selectedFile: File | null;
  onProcessAnother: () => void;
}

const EnhancedVideoSection: React.FC<EnhancedVideoSectionProps> = ({
  enhancedVideoUrl,
  selectedFile,
  onProcessAnother,
}) => {
  if (!enhancedVideoUrl) return null;
  return (
    <Card>
      <CardHeader>
        <CardTitle>Enhanced Video</CardTitle>
        <CardDescription>Your enhanced video is ready!</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <video
            controls
            className="w-full rounded-lg border"
            src={enhancedVideoUrl}
          >
            Your browser does not support the video tag.
          </video>
          <div className="flex gap-2">
            <Button
              onClick={() => {
                const link = document.createElement("a");
                link.href = enhancedVideoUrl;
                link.download = `enhanced_${selectedFile?.name || "video.mp4"}`;
                link.click();
              }}
              className="flex-1"
            >
              Download Enhanced Video
            </Button>
            <Button variant="outline" onClick={onProcessAnother}>
              Process Another Video
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedVideoSection;
