import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import React from "react";

interface UploadSectionProps {
  selectedFile: File | null;
  isUploading: boolean;
  error: string | null;
  onFileSelect: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onEnhance: () => void;
  disableEnhance: boolean;
}

const UploadSection: React.FC<UploadSectionProps> = ({
  selectedFile,
  isUploading,
  error,
  onFileSelect,
  onEnhance,
  disableEnhance,
}) => (
  <Card>
    <CardHeader>
      <CardTitle>Upload Video</CardTitle>
      <CardDescription>Select a video file to enhance</CardDescription>
    </CardHeader>
    <CardContent className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="video-upload">Video File</Label>
        <Input
          id="video-upload"
          type="file"
          accept="video/*"
          onChange={onFileSelect}
          disabled={isUploading || disableEnhance}
        />
      </div>
      {selectedFile && (
        <Card className="bg-muted/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium truncate">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              <div className="w-2 h-2 bg-muted-foreground rounded-full"></div>
            </div>
          </CardContent>
        </Card>
      )}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
      <Button
        onClick={onEnhance}
        disabled={!selectedFile || isUploading || disableEnhance}
        className="w-full"
      >
        {isUploading
          ? "Uploading..."
          : selectedFile
          ? "Enhance Video"
          : "Select video"}
      </Button>
    </CardContent>
  </Card>
);

export default UploadSection;
