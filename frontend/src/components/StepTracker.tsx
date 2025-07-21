import React from "react";

const STEPS = [
  { key: "INIT", label: "Initializing" },
  { key: "SETUP", label: "Setup" },
  { key: "EXTRACT", label: "Extract Frames" },
  { key: "ANALYZE", label: "Analyze Quality" },
  { key: "ENHANCE", label: "Enhance Frames" },
  { key: "RECONSTRUCT", label: "Reconstruct Video" },
  { key: "COMPLETE", label: "Complete" },
];

const CIRCLE_SIZE = 32; // px
const LINE_WIDTH = 3; // px

const StepTracker = ({ step }: { step: string }) => {
  const currentIdx = STEPS.findIndex((s) => s.key === step);
  return (
    <div
      className="relative flex flex-col items-start"
      style={{ minHeight: CIRCLE_SIZE * STEPS.length }}
    >
      {/* Vertical line, perfectly centered behind circles */}
      <div
        className="absolute z-0 bg-border"
        style={{
          left: CIRCLE_SIZE / 2 - LINE_WIDTH / 2,
          top: CIRCLE_SIZE / 2,
          bottom: CIRCLE_SIZE / 2,
          width: LINE_WIDTH,
        }}
      />
      {STEPS.map((s, idx) => {
        const isCompleted = idx < currentIdx;
        const isCurrent = idx === currentIdx;
        return (
          <div
            key={s.key}
            className={
              "flex items-center relative z-10 " +
              (idx < STEPS.length - 1 ? "mb-6" : "")
            }
            style={{ minHeight: CIRCLE_SIZE }}
          >
            <div
              className={
                "flex items-center justify-center rounded-full border-4 transition-all " +
                (isCompleted
                  ? "bg-green-500 border-green-500 text-white shadow-md"
                  : isCurrent
                  ? "bg-blue-600 border-blue-400 text-white shadow-lg ring-2 ring-blue-300 animate-pulse"
                  : "bg-muted text-muted-foreground border-border")
              }
              style={{
                width: CIRCLE_SIZE,
                height: CIRCLE_SIZE,
                position: "relative",
              }}
            >
              {isCompleted ? (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                idx + 1
              )}
            </div>
            <span
              className={
                "ml-4 text-base " +
                (isCurrent
                  ? "font-bold text-blue-700"
                  : isCompleted
                  ? "text-green-700"
                  : "text-muted-foreground")
              }
            >
              {s.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default StepTracker;
