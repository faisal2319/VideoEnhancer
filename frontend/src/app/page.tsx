"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import UploadSection from "@/components/UploadSection";
import ProgressSection from "@/components/ProgressSection";
import EnhancedVideoSection from "@/components/EnhancedVideoSection";

interface TaskStatus {
  task_id: string;
  status: any;
  progress: number;
  step: string;
  enhanced_video_path?: string;
  enhanced_video_url?: string;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [enhancedVideoUrl, setEnhancedVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith("video/")) {
      setSelectedFile(file);
      setError(null);
      setTaskId(null);
      setTaskStatus(null);
      setEnhancedVideoUrl(null);
    }
  };

  const handleEnhance = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE_URL}/enhance-video`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setTaskId(data.task_id);
      // Start WebSocket for status updates
      startWebSocket(data.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  // WebSocket logic for real-time updates
  const startWebSocket = (taskId: string) => {
    // Determine ws protocol and host
    let wsBase = API_BASE_URL.replace(/^http/, "ws");
    const ws = new WebSocket(`${wsBase}/ws/video/${taskId}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Accept both progress and final status
        setTaskStatus((prev) => ({ ...prev, ...data, task_id: taskId }));
        // If enhancement is done, set video URL
        if (data.state === "SUCCESS" && data.output_path) {
          // The backend returns output_path as minio path, but we expect enhanced_video_url
          setEnhancedVideoUrl(`/video/${taskId}`);
        }
        if (data.state === "FAILURE") {
          setError("Video enhancement failed");
        }
      } catch (e) {
        // Ignore parse errors
      }
    };
    ws.onerror = () => {
      // fallback to polling if ws fails
      pollTaskStatus(taskId);
    };
    ws.onclose = () => {
      // fallback to polling if ws closes before completion
      if (!enhancedVideoUrl && !error) {
        pollTaskStatus(taskId);
      }
    };
  };

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/task-status/${taskId}`);
        if (!response.ok) {
          throw new Error("Failed to get task status");
        }

        const status: TaskStatus = await response.json();
        setTaskStatus(status);

        // If task is completed successfully
        if (status.status?.state === "SUCCESS") {
          clearInterval(pollInterval);
          if (status.enhanced_video_url) {
            setEnhancedVideoUrl(status.enhanced_video_url);
          }
        } else if (status.status?.state === "FAILURE") {
          clearInterval(pollInterval);
          setError("Video enhancement failed");
        }
      } catch (err) {
        clearInterval(pollInterval);
        setError("Failed to get task status");
      }
    }, 2000); // Poll every 2 seconds
  };

  // Remove polling on mount, use WebSocket instead
  useEffect(() => {
    if (taskId) {
      startWebSocket(taskId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50 flex flex-col">
      {/* Topbar */}
      <header className="w-full py-6 bg-white/80 shadow-sm flex justify-center items-center mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-blue-900">
          Video Quality Enhancer
        </h1>
      </header>
      <main className="flex-1 flex justify-center items-start">
        <div className="w-full max-w-5xl px-4 grid grid-cols-1 md:grid-cols-2 gap-10">
          <div className="flex flex-col gap-8">
            <UploadSection
              selectedFile={selectedFile}
              isUploading={isUploading}
              error={error}
              onFileSelect={handleFileSelect}
              onEnhance={handleEnhance}
              disableEnhance={!!taskId}
            />
            <div className="hidden md:block text-xs text-muted-foreground text-center mt-4">
              Secure processing • AI-powered enhancement • Local processing
            </div>
          </div>
          <div className="flex flex-col gap-8">
            <ProgressSection taskStatus={taskStatus} />
            <EnhancedVideoSection
              enhancedVideoUrl={enhancedVideoUrl}
              selectedFile={selectedFile}
              onProcessAnother={() => {
                setSelectedFile(null);
                setTaskId(null);
                setTaskStatus(null);
                setEnhancedVideoUrl(null);
                setError(null);
              }}
            />
          </div>
        </div>
      </main>
      <footer className="md:hidden text-xs text-muted-foreground text-center py-4">
        Secure processing • AI-powered enhancement • Local processing
      </footer>
    </div>
  );
}
