import { useState } from "react";
import { Upload, X, AlertCircle, CheckCircle, Loader } from "lucide-react";

interface Props {
  readonly open: boolean;
  readonly onClose: () => void;
  readonly onFileSelect: (file: File) => Promise<void>;
  readonly isLoading?: boolean;
  readonly error?: string | null;
  readonly successCount?: number;
  readonly title?: string;
  readonly description?: string;
}

export function FileUploadModal({
  open,
  onClose,
  onFileSelect,
  isLoading = false,
  error = null,
  successCount = 0,
  title = "Import Recipes",
  description = "Upload a JSON file containing recipe data",
}: Readonly<Props>) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [internalError, setInternalError] = useState<string | null>(null);

  if (!open) return null;

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files?.[0]) {
      const file = files[0];
      if (file.name.endsWith(".json")) {
        setSelectedFile(file);
        setInternalError(null);
      } else {
        setInternalError("Please drop a JSON file");
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files?.[0]) {
      setSelectedFile(files[0]);
      setInternalError(null);
    }
  };

  const handleDragZoneKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      document.getElementById("file-input")?.click();
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setInternalError("Please select a file");
      return;
    }

    try {
      await onFileSelect(selectedFile);
      setSelectedFile(null);
    } catch (err) {
      setInternalError(
        err instanceof Error ? err.message : "Upload failed"
      );
    }
  };

  const currentError = error || internalError;
  const displaySuccessCount = successCount > 0;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-base-100 rounded-lg shadow-lg max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-base-200">
          <h2 className="text-lg font-semibold text-base-content">{title}</h2>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm btn-circle"
            disabled={isLoading}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {displaySuccessCount ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-success">
                <CheckCircle className="w-5 h-5 shrink-0" />
                <div>
                  <p className="font-medium">Import successful!</p>
                  <p className="text-sm text-success/80">
                    {successCount} {successCount === 1 ? "recipe" : "recipes"} imported
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-base-content/70">{description}</p>

              {/* Drag and Drop Zone */}
              <button
                type="button"
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onKeyDown={handleDragZoneKeyDown}
                disabled={isLoading}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer w-full ${
                  isDragActive
                    ? "border-primary bg-primary/5"
                    : "border-base-300 hover:border-base-400"
                } ${isLoading ? "opacity-50 pointer-events-none" : ""}`}
              >
                <Upload
                  className={`w-8 h-8 mx-auto mb-2 ${
                    isDragActive
                      ? "text-primary"
                      : "text-base-content/40"
                  }`}
                />
                <p className="text-sm font-medium text-base-content/70 mb-1">
                  {isDragActive
                    ? "Drop your file here"
                    : "Drag and drop your JSON file"}
                </p>
                <p className="text-xs text-base-content/50">or</p>
              </button>

              {/* File Input Button */}
              <div className="flex items-center gap-2">
                <input
                  type="file"
                  id="file-input"
                  accept=".json"
                  onChange={handleFileInput}
                  className="hidden"
                  disabled={isLoading}
                />
                <label
                  htmlFor="file-input"
                  className="flex-1"
                >
                  <button
                    className="btn btn-outline btn-sm w-full"
                    disabled={isLoading}
                    onClick={() => document.getElementById("file-input")?.click()}
                  >
                    Choose File
                  </button>
                </label>
              </div>

              {/* Selected File */}
              {selectedFile && (
                <div className="bg-base-200 rounded p-3">
                  <p className="text-xs text-base-content/70">Selected file:</p>
                  <p className="text-sm font-medium text-base-content truncate">
                    {selectedFile.name}
                  </p>
                </div>
              )}

              {/* Error Message */}
              {currentError && (
                <div className="alert alert-error alert-sm">
                <AlertCircle className="w-4 h-4 shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm">{currentError}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-6 border-t border-base-200">
          {displaySuccessCount ? (
            <button
              onClick={onClose}
              className="btn btn-primary btn-sm"
              disabled={isLoading}
            >
              Done
            </button>
          ) : (
            <>
              <button
                onClick={onClose}
                className="btn btn-ghost btn-sm"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="btn btn-primary btn-sm"
                disabled={isLoading || !selectedFile}
              >
                {isLoading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Importing...
                  </>
                ) : (
                  "Import"
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
